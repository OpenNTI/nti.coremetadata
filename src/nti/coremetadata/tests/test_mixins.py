#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import unittest

from nti.coremetadata.interfaces import IContained
from nti.coremetadata.interfaces import IZContained

from nti.coremetadata.mixins import ContainedMixin

from nti.coremetadata.tests import SharedConfiguringTestLayer


class TestMixins(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_contained(self):
        c = ContainedMixin(containerId="100", containedId="200")
        assert_that(c, validly_provides(IContained))
        assert_that(c, verifiably_provides(IContained))
        assert_that(c, verifiably_provides(IZContained))
        assert_that(c, has_property('containerId', is_("100")))
        assert_that(c, has_property('id', is_("200")))
