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
from zope.container.contained import Contained

from nti.schema.fieldproperty import UnicodeConvertingFieldProperty

from .interfaces import IContained

class CreatedTimeMixin(object):

	createdTime = 0
	_SET_CREATED_MODTIME_ON_INIT = True

	def __init__(self, *args, **kwargs):
		if self._SET_CREATED_MODTIME_ON_INIT and self.createdTime == 0:
			self.createdTime = time.time()
		super(CreatedTimeMixin,self).__init__( *args, **kwargs )

@interface.implementer(IContained)
class _ContainedMixin(Contained):
	"""
	Defines something that can be logically contained inside another unit
	by reference. Two properties are defined, id and containerId.
	"""

	# It is safe to use these properties in persistent objects because
	# they read/write to the __dict__ with the same name as the field,
	# and setattr on the persistent object is what set _p_changed, so
	# assigning to them still changes the object correctly
	containerId = UnicodeConvertingFieldProperty(IContained['containerId'])
	id = UnicodeConvertingFieldProperty(IContained['id'])

	# __name__ is NOT automatically defined as an id alias, because that could lose
	# access to existing data that has a __name__ in its instance dict

	def __init__(self, *args, **kwargs ):
		containerId = kwargs.pop( 'containerId', None )
		containedId = kwargs.pop( 'containedId', None )
		super(_ContainedMixin,self).__init__(*args, **kwargs)
		if containerId is not None:
			self.containerId = containerId
		if containedId is not None:
			self.id = containedId

ContainedMixin = ZContainedMixin = _ContainedMixin
