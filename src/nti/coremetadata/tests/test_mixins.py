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

import time
import unittest

from datetime import datetime
from datetime import timedelta

from nti.coremetadata.interfaces import IRecordable
from nti.coremetadata.interfaces import ICreatedTime
from nti.coremetadata.interfaces import ILastModified
from nti.coremetadata.interfaces import IDefaultPublished
from nti.coremetadata.interfaces import ICalendarPublishable
from nti.coremetadata.interfaces import IRecordableContainer

from nti.coremetadata.mixins import RecordableMixin
from nti.coremetadata.mixins import CalendarPublishableMixin
from nti.coremetadata.mixins import RecordableContainerMixin
from nti.coremetadata.mixins import CreatedAndModifiedTimeMixin

from nti.coremetadata.tests import SharedConfiguringTestLayer

from nti.testing.time import time_monotonically_increases

class TestMixins(unittest.TestCase):

	layer = SharedConfiguringTestLayer

	def test_plus_extend(self):
		c = CreatedAndModifiedTimeMixin()
		for iface in (ICreatedTime, ILastModified):
			assert_that(c, validly_provides(iface))
			assert_that(c, verifiably_provides(iface))

		t = time.time() + 100
		c.updateLastMod(t)
		assert_that(c, has_property('lastModified', is_(t)))

		c.updateLastModIfGreater(100)
		assert_that(c, has_property('lastModified', is_(t)))

	def test_recordable(self):
		c = RecordableMixin()
		assert_that(c, has_property('locked', is_(False)))
		assert_that(c, validly_provides(IRecordable))
		assert_that(c, verifiably_provides(IRecordable))
		c.lock()
		assert_that(c, has_property('locked', is_(True)))
		assert_that(c.is_locked(), is_(True))
		c.unlock()
		assert_that(c, has_property('locked', is_(False)))

	def test_recordable_container(self):
		c = RecordableContainerMixin()
		assert_that(c, has_property('child_order_locked', is_(False)))
		assert_that(c, validly_provides(IRecordableContainer))
		assert_that(c, verifiably_provides(IRecordableContainer))
		c.child_order_lock()
		assert_that(c, has_property('child_order_locked', is_(True)))
		assert_that(c.is_child_order_locked(), is_(True))
		c.child_order_unlock()
		assert_that(c, has_property('child_order_locked', is_(False)))

	def test_plublishable(self):
		c = CalendarPublishableMixin()
		assert_that(c, validly_provides(ICalendarPublishable))
		assert_that(c, verifiably_provides(ICalendarPublishable))

		c.publish()
		assert_that(c, verifiably_provides(IDefaultPublished))

		c.unpublish()
		assert_that(c, does_not(verifiably_provides(IDefaultPublished)))

	@time_monotonically_increases
	def test_publish_status(self):
		obj = CalendarPublishableMixin()
		assert_that( obj.is_published(), is_( False ))
		yesterday = datetime.utcnow() - timedelta( days=1 )
		tomorrow = yesterday + timedelta( days=2 )
		last_mod = 0

		obj.publish( start=yesterday )
		assert_that( obj.is_published(), is_( True ))
		assert_that( obj.publishLastModified, greater_than( last_mod ))
		last_mod = obj.publishLastModified

		obj.publish( start=tomorrow )
		assert_that( obj.is_published(), is_( False ))
		assert_that( obj.publishLastModified, greater_than( last_mod ))
		last_mod = obj.publishLastModified

		obj.publish()
		assert_that( obj.is_published(), is_( True ))
		assert_that( obj.publishLastModified, greater_than( last_mod ))
		last_mod = obj.publishLastModified

		obj.publish( start=tomorrow )
		assert_that( obj.is_published(), is_( False ))
		assert_that( obj.publishLastModified, greater_than( last_mod ))
		last_mod = obj.publishLastModified

		obj.publish( start=yesterday )
		assert_that( obj.is_published(), is_( True ))
		assert_that( obj.publishLastModified, greater_than( last_mod ))
		last_mod = obj.publishLastModified

		obj.publish( start=tomorrow, end=tomorrow )
		assert_that( obj.is_published(), is_( False ))
		assert_that( obj.publishLastModified, greater_than( last_mod ))
		last_mod = obj.publishLastModified

		obj.publish( start=yesterday, end=tomorrow )
		assert_that( obj.is_published(), is_( True ))
		assert_that( obj.publishLastModified, greater_than( last_mod ))
		last_mod = obj.publishLastModified

		obj.publish( start=yesterday, end=yesterday )
		assert_that( obj.is_published(), is_( False ))
		assert_that( obj.publishLastModified, greater_than( last_mod ))
		last_mod = obj.publishLastModified

		obj.publish()
		assert_that( obj.is_published(), is_( True ))
		assert_that( obj.publishLastModified, greater_than( last_mod ))
		last_mod = obj.publishLastModified
