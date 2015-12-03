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

import time
import unittest

from nti.coremetadata.interfaces import IRecordable
from nti.coremetadata.interfaces import ICreatedTime
from nti.coremetadata.interfaces import ILastModified
from nti.coremetadata.interfaces import IDefaultPublished
from nti.coremetadata.interfaces import ICalendarPublishable

from nti.coremetadata.mixins import RecordableMixin
from nti.coremetadata.mixins import CalendarPublishableMixin
from nti.coremetadata.mixins import CreatedAndModifiedTimeMixin

from nti.coremetadata.tests import SharedConfiguringTestLayer

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

	def test_plublishable(self):
		c = CalendarPublishableMixin()
		assert_that(c, validly_provides(ICalendarPublishable))
		assert_that(c, verifiably_provides(ICalendarPublishable))

		c.publish()
		assert_that(c, verifiably_provides(IDefaultPublished))

		c.unpublish()
		assert_that(c, does_not(verifiably_provides(IDefaultPublished)))
