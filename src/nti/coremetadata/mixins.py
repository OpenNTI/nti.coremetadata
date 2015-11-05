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

from .interfaces import IRecordable
from .interfaces import IPublishable
from .interfaces import ILastModified
from .interfaces import IDefaultPublished

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

@interface.implementer(IPublishable)
class PublishableMixin(object):
	
	def __init__(self, *args, **kwargs):
		super(PublishableMixin, self).__init__(*args, **kwargs)
		
	def publish(self):
		interface.alsoProvides(self, IDefaultPublished)

	def unpublish(self):
		interface.noLongerProvides(self, IDefaultPublished)
		
	def is_published(self):
		return IDefaultPublished.providedBy(self)
	isPublished = is_published
