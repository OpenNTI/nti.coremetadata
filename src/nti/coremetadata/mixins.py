#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import time

from datetime import datetime

from zope import interface

from zope.event import notify

from .interfaces import IRecordable
from .interfaces import ICalendarPublishable
from .interfaces import ILastModified
from .interfaces import IDefaultPublished

from .interfaces import ObjectPublishedEvent
from .interfaces import ObjectUnpublishedEvent

class CreatedTimeMixin(object):

	_SET_CREATED_MODTIME_ON_INIT = True

	createdTime = 0

	def __init__(self, *args, **kwargs):
		if self._SET_CREATED_MODTIME_ON_INIT and self.createdTime == 0:
			self.createdTime = time.time()
		super(CreatedTimeMixin, self).__init__(*args, **kwargs)

class ModifiedTimeMixin(object):

	lastModified = 0

	def __init__(self, *args, **kwargs):
		super(ModifiedTimeMixin, self).__init__(*args, **kwargs)

	def updateLastMod(self, t=None):
		self.lastModified = (t if t is not None and t > self.lastModified else time.time())
		return self.lastModified

	def updateLastModIfGreater(self, t):
		"""
		Only if the given time is (not None and) greater than this object's is this object's time changed.
		"""
		if t is not None and t > self.lastModified:
			self.lastModified = t
		return self.lastModified

@interface.implementer(ILastModified)
class CreatedAndModifiedTimeMixin(CreatedTimeMixin, ModifiedTimeMixin):

	def __init__(self, *args, **kwargs):
		# We set the times now so subclasses can rely on them
		if self._SET_CREATED_MODTIME_ON_INIT:
			self.createdTime = time.time()
			self.updateLastModIfGreater(self.createdTime)
		super(CreatedAndModifiedTimeMixin, self).__init__(*args, **kwargs)

@interface.implementer(IRecordable)
class RecordableMixin(object):

	locked = False

	def __init__(self, *args, **kwargs):
		super(RecordableMixin, self).__init__(*args, **kwargs)

@interface.implementer(ICalendarPublishable)
class CalendarPublishableMixin(object):

	publishBeginning = None
	publishEnding = None

	def __init__(self, *args, **kwargs):
		super(CalendarPublishableMixin, self).__init__(*args, **kwargs)

	def do_publish(self, event=True):
		interface.alsoProvides(self, IDefaultPublished)
		if event:
			notify(ObjectPublishedEvent(self))

	def publish(self, start=None, end=None):
		if start is not None:
			# It wouldn't make sense to just send an
			# ending date on a publish call.
			self.publishBeginning = start
			self.publishEnding = end
		else:
			# Explicit publish, reset any dates we have.
			self.do_publish()
			self.publishBeginning = None
			self.publishEnding = None

	def do_unpublish(self, event=True):
		interface.noLongerProvides(self, IDefaultPublished)
		if event:
			notify(ObjectUnpublishedEvent(self))

	def unpublish(self):
		self.do_unpublish()
		self.publishBeginning = None
		self.publishEnding = None

	def is_published(self):
		"""
		Published if either explicitly published or after
		our start date and before our end date, if provided.
		"""
		now = datetime.utcnow()
		start = self.publishBeginning
		end = self.publishEnding
		result = IDefaultPublished.providedBy(self) \
				or ( 	( start is not None and now > start ) \
					and ( end is None or now < end ))
		return bool( result )

	isPublished = is_published
