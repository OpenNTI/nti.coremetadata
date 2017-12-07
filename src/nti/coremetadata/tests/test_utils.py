#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

import unittest

from zope import component
from zope import interface

from zope.security.management import system_user

from nti.coremetadata.interfaces import IObjectJsonSchemaMaker

from nti.coremetadata.utils import make_schema
from nti.coremetadata.utils import current_principal

from nti.coremetadata.tests import SharedConfiguringTestLayer


class TestUtils(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_current_principal(self):
        c = current_principal(True)
        assert_that(c, has_property('id', is_(system_user.id)))

    def test_make_schema(self):
        marker = object()

        @interface.implementer(IObjectJsonSchemaMaker)
        class FakeMaker(object):
            def make_schema(self, unused_schema, unused_user=None):
                return marker
        schema_maker = FakeMaker()
        component.getGlobalSiteManager().registerUtility(schema_maker,
                                                         IObjectJsonSchemaMaker)
        result = make_schema(interface.Interface)
        assert_that(result, is_(marker))
        component.getGlobalSiteManager().unregisterUtility(schema_maker,
                                                           IObjectJsonSchemaMaker)
