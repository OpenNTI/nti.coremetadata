#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that
does_not = is_not

import unittest

from zope import interface

from nti.base.interfaces import ILastModified

from nti.coremetadata.jsonschema import CoreJsonSchemafier

from nti.coremetadata.tests import SharedConfiguringTestLayer

from nti.schema.field import Number
from nti.schema.field import Object

class TestJsonSchema(unittest.TestCase):

    layer = SharedConfiguringTestLayer

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
            object = Object(interface.Interface)
        assert_that(schemafier.process_object(IBase['object']),
                    is_(none()))
