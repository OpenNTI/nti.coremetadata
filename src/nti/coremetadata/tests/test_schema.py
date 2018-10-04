#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods,inherit-non-class

from hamcrest import is_
from hamcrest import is_not
from hamcrest import assert_that
does_not = is_not

import unittest

from zope import interface

from zope.schema.interfaces import InvalidURI
from zope.schema.interfaces import ValidationError

from nti.coremetadata.schema import DataURI
from nti.coremetadata.schema import bodySchemaField
from nti.coremetadata.schema import BodyFieldProperty
from nti.coremetadata.schema import AbstractFieldProperty
from nti.coremetadata.schema import CompoundModeledContentBody
from nti.coremetadata.schema import MessageInfoBodyFieldProperty
from nti.coremetadata.schema import ExtendedCompoundModeledContentBody

from nti.coremetadata.tests import SharedConfiguringTestLayer

from nti.schema.field import Number
from nti.schema.field import ListOrTupleFromObject

from nti.schema.interfaces import VariantValidationError


class TestSchema(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_data_uri(self):
        m = DataURI()
        m._validate('data:-1')
        with self.assertRaises(InvalidURI):
            m._validate('urn:isbn:0-395-36341-1')

    def test_extended_compound_modeled_content_body(self):
        field = ExtendedCompoundModeledContentBody()
        assert_that(field, is_(ListOrTupleFromObject))

    def test_model(self):
        class IModel(interface.Interface):
            abs = bodySchemaField(fields=(Number(),))
            body = ExtendedCompoundModeledContentBody()
            msg = CompoundModeledContentBody()

        @interface.implementer(IModel)
        class Model(object):
            abs = AbstractFieldProperty(IModel['abs'])
            body = BodyFieldProperty(IModel['body'])
            msg = MessageInfoBodyFieldProperty(IModel['msg'])

        # body
        m = Model()
        m.body = [b'aizen']
        # message
        m.msg = b'aizen'
        m.msg = [u'aizen']
        # coverage
        with self.assertRaises(ValidationError):
            m.abs = object()
        with self.assertRaises(ValidationError):
            m.abs = []
        with self.assertRaises(VariantValidationError):
            m.abs = [()]
