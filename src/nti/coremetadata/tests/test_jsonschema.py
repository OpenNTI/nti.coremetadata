#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods,inherit-non-class

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import has_key
from hamcrest import has_entry
from hamcrest import assert_that
does_not = is_not

import unittest

from zope import component
from zope import interface

from zope.schema import vocabulary

from nti.base.interfaces import ILastModified

from nti.coremetadata.interfaces import IObjectJsonSchemaMaker

from nti.coremetadata.jsonschema import CoreJsonSchemafier

from nti.coremetadata.tests import SharedConfiguringTestLayer

from nti.schema.field import Choice
from nti.schema.field import Number
from nti.schema.field import Object
from nti.schema.field import Variant
from nti.schema.field import TextLine
from nti.schema.field import ListOrTuple


SAMPLE_VOCABULARY = vocabulary.SimpleVocabulary(
    [vocabulary.SimpleTerm(x) for x in ('a', 'b', 'c')]
)


class TestJsonSchema(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_default(self):
        class IModel(ILastModified):
            abs = Number()

        maker = component.queryUtility(IObjectJsonSchemaMaker)
        assert_that(maker, is_not(none()))
        result = maker.make_schema(IModel)
        assert_that(result,
                    has_entry('Fields', has_key('abs')))

    def test_allow_fields(self):
        class IModel(ILastModified):
            abs = Number()
        schemafier = CoreJsonSchemafier(IModel)
        assert_that(schemafier.allow_field('abs', IModel['abs']),
                    is_(True))
        assert_that(schemafier.allow_field('lastModified', IModel['lastModified']),
                    is_(False))

    def test_process_object(self):
        class ISpirit(interface.Interface):
            pass

        class IBleach(interface.Interface):
            shinigami = Object(ISpirit)
        schemafier = CoreJsonSchemafier(IBleach)
        assert_that(schemafier.process_object(IBleach['shinigami']),
                    is_('Spirit'))

        class IBase(interface.Interface):
            obj = Object(interface.Interface)
        schemafier = CoreJsonSchemafier(IBase)
        assert_that(schemafier.process_object(IBase['obj']),
                    is_(none()))

        assert_that(schemafier.get_ui_types_from_field(IBase['obj']),
                    is_(('Object', None)))

    def test_process_variant(self):
        class I1(interface.Interface):
            obj = Variant((Object(interface.Interface),
                           Number()))
        schemafier = CoreJsonSchemafier(I1)
        assert_that(schemafier.get_ui_types_from_field(I1['obj']),
                    is_(('Variant', 'float')))

        class I2(interface.Interface):
            obj = Variant((Object(interface.Interface),
                           Choice(vocabulary=SAMPLE_VOCABULARY)))
        schemafier = CoreJsonSchemafier(I2)
        assert_that(schemafier.get_ui_types_from_field(I2['obj']),
                    is_(('Variant', 'string')))

        class I3(interface.Interface):
            obj = Variant((Object(interface.Interface),))
        schemafier = CoreJsonSchemafier(I3)
        assert_that(schemafier.get_ui_types_from_field(I3['obj']),
                    is_(('Variant', 'Variant')))

    def test_process_list(self):
        class I1(interface.Interface):
            obj = ListOrTuple(TextLine())
        schemafier = CoreJsonSchemafier(I1)
        assert_that(schemafier.get_ui_types_from_field(I1['obj']),
                    is_(('List', 'string')))

        class I2(interface.Interface):
            obj = ListOrTuple(Object(interface.Interface))
        schemafier = CoreJsonSchemafier(I2)
        assert_that(schemafier.get_ui_types_from_field(I2['obj']),
                    is_(('List', None)))

        class I3(interface.Interface):
            obj = ListOrTuple(Choice(vocabulary=SAMPLE_VOCABULARY))
        schemafier = CoreJsonSchemafier(I3)
        assert_that(schemafier.get_ui_types_from_field(I3['obj']),
                    is_(('List', 'string')))

        class I4(interface.Interface):
            obj = ListOrTuple(Variant((Object(interface.Interface),)))
        schemafier = CoreJsonSchemafier(I4)
        assert_that(schemafier.get_ui_types_from_field(I4['obj']),
                    is_(('List', 'list')))
