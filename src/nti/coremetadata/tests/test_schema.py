#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

import time
import unittest

from nti.coremetadata.mixins import CalendarPublishableMixin
from nti.coremetadata.interfaces import ICalendarPublishable

from nti.coremetadata.schema import parse_datetime

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.coremetadata.tests import SharedConfiguringTestLayer

class TestSchema(unittest.TestCase):

	layer = SharedConfiguringTestLayer

	def test_datatime(self):
		
		class Foo(CalendarPublishableMixin):
			createDirectFieldProperties(ICalendarPublishable)
		field = ICalendarPublishable['publishEnding']
		
		now = time.time()
		dt = parse_datetime(now)
		assert_that(dt, is_not(none()))
		
		c = Foo()
		field.bind(c)
		
		field.set(c, None)
		assert_that(c, has_property('publishEnding', is_(none())))
		
		field.set(c, now) # as float
		assert_that(c, has_property('publishEnding', is_(dt)))
				
		field.set(c, dt) # as datetime
		assert_that(c, has_property('publishEnding', is_(dt)))
		
		field.set(c, dt.isoformat()) # as string
		assert_that(c, has_property('publishEnding', is_(dt)))
