#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import time

from zope import interface

from zope.event import notify

from nti.coremetadata.interfaces import IRecordable
from nti.coremetadata.interfaces import IPublishable
from nti.coremetadata.interfaces import IDefaultPublished
from nti.coremetadata.interfaces import ICalendarPublishable
from nti.coremetadata.interfaces import IRecordableContainer

from nti.coremetadata.interfaces import ObjectLockedEvent
from nti.coremetadata.interfaces import ObjectUnlockedEvent
from nti.coremetadata.interfaces import ObjectPublishedEvent
from nti.coremetadata.interfaces import ObjectUnpublishedEvent
from nti.coremetadata.interfaces import ObjectChildOrderLockedEvent
from nti.coremetadata.interfaces import ObjectChildOrderUnlockedEvent
from nti.coremetadata.interfaces import CalendarPublishableModifiedEvent

from nti.coremetadata.utils import is_published
from nti.coremetadata.utils import is_calendar_published

import zope.deferredimport
zope.deferredimport.initialize()
zope.deferredimport.deprecated(
	"Import from nti.base.mixins instead",
	CreatedTimeMixin='nti.base.mixins:CreatedTimeMixin',
	ModifiedTimeMixin='nti.base.mixins:ModifiedTimeMixin',
	CreatedAndModifiedTimeMixin='nti.base.mixins:ModifiedTimeMixin',)

@interface.implementer(IRecordable)
class RecordableMixin(object):

	locked = False

	def __init__(self, *args, **kwargs):
		super(RecordableMixin, self).__init__(*args, **kwargs)

	def lock(self, event=True, **kwargs):
		self.locked = True
		if event:
			notify(ObjectLockedEvent(self))

	def unlock(self, event=True, **kwargs):
		self.locked = False
		if event:
			notify(ObjectUnlockedEvent(self))

	def isLocked(self):
		return self.locked
	is_locked = isLocked

@interface.implementer(IRecordableContainer)
class RecordableContainerMixin(RecordableMixin):

	child_order_locked = False

	def __init__(self, *args, **kwargs):
		super(RecordableContainerMixin, self).__init__(*args, **kwargs)

	def child_order_lock(self, event=True, **kwargs):
		self.child_order_locked = True
		if event:
			notify(ObjectChildOrderLockedEvent(self))
	childOrderLock = child_order_lock

	def child_order_unlock(self, event=True, **kwargs):
		self.child_order_locked = False
		if event:
			notify(ObjectChildOrderUnlockedEvent(self))
	childOrderUnlock = child_order_unlock

	def is_child_order_locked(self):
		return self.child_order_locked
	isChildOrderLocked = is_child_order_locked

@interface.implementer(IPublishable)
class PublishableMixin(object):

	publishLastModified = None

	__publication_predicate_interface__ = None
	
	def __init__(self, *args, **kwargs):
		super(PublishableMixin, self).__init__(*args, **kwargs)

	def _update_publish_last_mod(self):
		"""
		Update the publish last modification time.
		"""
		self.publishLastModified = time.time()
	updatePublishLastModified = _update_publish_last_mod

	def do_publish(self, event=True, **kwargs):
		self._update_publish_last_mod()
		interface.alsoProvides(self, IDefaultPublished)
		if event:
			notify(ObjectPublishedEvent(self))

	def publish(self, *args, **kwargs):
		if not self.is_published():
			self.do_publish(**kwargs)

	def do_unpublish(self, event=True, **kwargs):
		self._update_publish_last_mod()
		interface.noLongerProvides(self, IDefaultPublished)
		if event:
			notify(ObjectUnpublishedEvent(self))

	def unpublish(self, *args, **kwargs):
		if self.is_published():
			self.do_unpublish(**kwargs)

	def is_published(self, *args, **kwargs):
		interface = 	kwargs.get('interface', None) \
					or	getattr(self, '__publication_predicate_interface__', None)
		if interface is not None:
			kwargs['interface'] = interface
		return is_published(self, *args, **kwargs)
	isPublished = is_published

@interface.implementer(ICalendarPublishable)
class CalendarPublishableMixin(PublishableMixin):

	publishEnding = None
	publishBeginning = None

	def publish(self, start=None, end=None, **kwargs):
		if start is None:
			# Explicit publish, reset any dates we have.
			# The user may publish but specify just an end date.
			self.do_publish(**kwargs)
		else:
			# Update mod time and notify our object is changing.
			self._update_publish_last_mod()
			notify(CalendarPublishableModifiedEvent(self, start, end))
			interface.noLongerProvides(self, IDefaultPublished)
		self.publishEnding = end
		self.publishBeginning = start

	def unpublish(self, *args, **kwargs):
		self.do_unpublish(**kwargs)
		self.publishEnding = None
		self.publishBeginning = None

	def is_published(self, *args, **kwargs):
		interface = 	kwargs.get('interface', None) \
					or	getattr(self, '__publication_predicate_interface__', None)
		if interface is not None:
			kwargs['interface'] = interface
		return is_calendar_published(self, *args, **kwargs)
	isPublished = is_published
