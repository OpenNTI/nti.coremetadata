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
from hamcrest import has_property
does_not = is_not

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import unittest

from zope.location.interfaces import IContained as IZContained

from nti.coremetadata.interfaces import IContained
from nti.coremetadata.interfaces import IVersioned

from nti.coremetadata.mixins import ContainedMixin
from nti.coremetadata.mixins import VersionedMixin

from nti.coremetadata.tests import SharedConfiguringTestLayer


class TestMixins(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_contained(self):
        c = ContainedMixin(containerId=u"100", containedId=u"200")
        assert_that(c, validly_provides(IContained))
        assert_that(c, verifiably_provides(IContained))
        assert_that(c, verifiably_provides(IZContained))
        assert_that(c, has_property('containerId', is_("100")))
        assert_that(c, has_property('id', is_("200")))
        
    def test_versioned(self):
        c = VersionedMixin()
        c.update_version(u"100")
        assert_that(c, validly_provides(IVersioned))
        assert_that(c, verifiably_provides(IVersioned))
        assert_that(c, has_property('Version', is_("100")))
        c.update_version()
        assert_that(c, has_property('version', is_not(none())))
        assert_that(c, has_property('version', is_not("100")))
