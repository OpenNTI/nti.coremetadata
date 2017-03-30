#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import greater_than
from hamcrest import has_property
does_not = is_not

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import unittest

from datetime import datetime
from datetime import timedelta

from nti.coremetadata.interfaces import IContained
from nti.coremetadata.interfaces import IZContained
from nti.coremetadata.interfaces import IDefaultPublished
from nti.coremetadata.interfaces import ICalendarPublishable

from nti.coremetadata.mixins import ContainedMixin
from nti.coremetadata.mixins import CalendarPublishableMixin

from nti.coremetadata.tests import SharedConfiguringTestLayer

from nti.testing.time import time_monotonically_increases


class TestMixins(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_plublishable(self):
        c = CalendarPublishableMixin()
        assert_that(c, validly_provides(ICalendarPublishable))
        assert_that(c, verifiably_provides(ICalendarPublishable))

        c.publish()
        assert_that(c, verifiably_provides(IDefaultPublished))
        assert_that(c.isPublished(), is_(True))

        c.unpublish()
        assert_that(c, does_not(verifiably_provides(IDefaultPublished)))
        assert_that(c.isPublished(), is_(False))

    @time_monotonically_increases
    def test_publish_status(self):
        obj = CalendarPublishableMixin()
        assert_that(obj.is_published(), is_(False))
        yesterday = datetime.utcnow() - timedelta(days=1)
        tomorrow = yesterday + timedelta(days=2)
        last_mod = 0

        obj.publish(start=yesterday)
        assert_that(obj.is_published(), is_(True))
        assert_that(obj.publishLastModified, greater_than(last_mod))
        last_mod = obj.publishLastModified

        obj.publish(start=tomorrow)
        assert_that(obj.is_published(), is_(False))
        assert_that(obj.publishLastModified, greater_than(last_mod))
        last_mod = obj.publishLastModified

        obj.publish()
        assert_that(obj.is_published(), is_(True))
        assert_that(obj.publishLastModified, greater_than(last_mod))
        last_mod = obj.publishLastModified

        obj.publish(start=tomorrow)
        assert_that(obj.is_published(), is_(False))
        assert_that(obj.publishLastModified, greater_than(last_mod))
        last_mod = obj.publishLastModified

        obj.publish(start=yesterday)
        assert_that(obj.is_published(), is_(True))
        assert_that(obj.publishLastModified, greater_than(last_mod))
        last_mod = obj.publishLastModified

        obj.publish(start=tomorrow, end=tomorrow)
        assert_that(obj.is_published(), is_(False))
        assert_that(obj.publishLastModified, greater_than(last_mod))
        last_mod = obj.publishLastModified

        obj.publish(start=yesterday, end=tomorrow)
        assert_that(obj.is_published(), is_(True))
        assert_that(obj.publishLastModified, greater_than(last_mod))
        last_mod = obj.publishLastModified

        obj.publish(start=yesterday, end=yesterday)
        assert_that(obj.is_published(), is_(False))
        assert_that(obj.publishLastModified, greater_than(last_mod))
        last_mod = obj.publishLastModified

        obj.publish()
        assert_that(obj.is_published(), is_(True))
        assert_that(obj.publishLastModified, greater_than(last_mod))
        last_mod = obj.publishLastModified

    def test_contained(self):
        c = ContainedMixin(containerId="100", containedId="200")
        assert_that(c, validly_provides(IContained))
        assert_that(c, verifiably_provides(IContained))
        assert_that(c, verifiably_provides(IZContained))
        assert_that(c, has_property('containerId', is_("100")))
        assert_that(c, has_property('id', is_("200")))
