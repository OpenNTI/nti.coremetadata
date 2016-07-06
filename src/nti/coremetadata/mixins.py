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

from nti.coremetadata.interfaces import IRecordable
from nti.coremetadata.interfaces import IPublishable
from nti.coremetadata.interfaces import ILastModified
from nti.coremetadata.interfaces import IDefaultPublished
from nti.coremetadata.interfaces import ICalendarPublishable
from nti.coremetadata.interfaces import IRecordableContainer

from nti.coremetadata.interfaces import ObjectLockedEvent
from nti.coremetadata.interfaces import ObjectUnlockedEvent
from nti.coremetadata.interfaces import ObjectPublishedEvent
from nti.coremetadata.interfaces import ObjectUnpublishedEvent
from nti.coremetadata.interfaces import ObjectChildOrderLockedEvent
from nti.coremetadata.interfaces import ObjectChildOrderUnlockedEvent

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

	def lock(self):
		self.locked = True
		notify(ObjectLockedEvent(self))

	def unlock(self):
		self.locked = False
		notify(ObjectUnlockedEvent(self))

	def isLocked(self):
		return self.locked
	is_locked = isLocked

@interface.implementer(IRecordableContainer)
class RecordableContainerMixin(RecordableMixin):

	child_order_locked = False

	def __init__(self, *args, **kwargs):
		super(RecordableContainerMixin, self).__init__(*args, **kwargs)

	def child_order_lock(self):
		self.child_order_locked = True
		notify(ObjectChildOrderLockedEvent(self))
	childOrderLock = child_order_lock

	def child_order_unlock(self):
		self.child_order_locked = False
		notify(ObjectChildOrderUnlockedEvent(self))
	childOrderUnlock = child_order_unlock

	def is_child_order_locked(self):
		return self.child_order_locked
	isChildOrderLocked = is_child_order_locked

@interface.implementer(IPublishable)
class PublishableMixin(object):

	def __init__(self, *args, **kwargs):
		super(PublishableMixin, self).__init__(*args, **kwargs)

	def do_publish(self, event=True, **kwargs):
		interface.alsoProvides(self, IDefaultPublished)
		if event:
			notify(ObjectPublishedEvent(self))

	def publish(self, *args, **kwargs):
		if not self.is_published():
			self.do_publish( **kwargs )

	def do_unpublish(self, event=True, **kwargs):
		interface.noLongerProvides(self, IDefaultPublished)
		if event:
			notify(ObjectUnpublishedEvent(self))

	def unpublish(self, **kwargs):
		if self.is_published():
			self.do_unpublish( **kwargs )

	def is_published(self):
		return IDefaultPublished.providedBy(self)
	isPublished = is_published

@interface.implementer(ICalendarPublishable)
class CalendarPublishableMixin(PublishableMixin):

	publishEnding = None
	publishBeginning = None

	def publish(self, start=None, end=None, **kwargs):
		if start is None:
			# Explicit publish, reset any dates we have.
			# The user may publish but specify just an end date.
			self.do_publish( **kwargs )
		else:
			interface.noLongerProvides(self, IDefaultPublished)
		self.publishEnding = end
		self.publishBeginning = start

	def unpublish(self, **kwargs):
		self.do_unpublish( **kwargs )
		self.publishEnding = None
		self.publishBeginning = None

	def is_published(self):
		"""
		Published if either explicitly published or after
		our start date and before our end date, if provided.
		"""
		now = datetime.utcnow()
		end = self.publishEnding
		start = self.publishBeginning
		result =  	(	IDefaultPublished.providedBy(self)
					 or (start is not None and now > start) ) \
				and (end is None or now < end)
		return bool(result)
	isPublished = is_published
