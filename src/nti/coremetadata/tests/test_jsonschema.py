#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import is_not
from hamcrest import assert_that
does_not = is_not

import unittest

from nti.base.interfaces import ILastModified

from nti.coremetadata.jsonschema import CoreJsonSchemafier

from nti.coremetadata.tests import SharedConfiguringTestLayer

from nti.schema.field import Number


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