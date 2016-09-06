#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

from zope.interface.interfaces import ObjectEvent
from zope.interface.interfaces import IObjectEvent

from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from zope.schema import Iterable

from zope.security.management import system_user

from nti.schema.field import Bool
from nti.schema.field import Number
from nti.schema.field import ValidDatetime

SYSTEM_USER_ID = system_user.id
SYSTEM_USER_NAME = getattr(system_user, 'title').lower()

class ICreatedTime(interface.Interface):
	"""
	Something that (immutably) tracks its created time.
	"""

	createdTime = Number(title=u"The timestamp at which this object was created.",
						 description="Typically set automatically by the object.",
						 default=0.0)

class ILastModified(ICreatedTime):
	"""
	Something that tracks a modification timestamp.
	"""

	lastModified = Number(title=u"The timestamp at which this object or its contents was last modified.",
						  default=0.0)

class ILastViewed(ILastModified):
	"""
	In addition to tracking modification and creation times, this
	object tracks viewing (or access) times.

	For security sensitive objects, this may be set automatically in
	an audit-log type fashion. The most typical use, however, will be
	to allow clients to track whether or not the item has been
	displayed to the end user since its last modification; in that
	case, the client will be responsible for updating the value seen
	here explicitly (we can not assume that requesting an object for
	externalization, for example, results in viewing).

	In some cases it may be necessary to supplement this object with
	additional information such as a counter to get the desired
	behaviour.
	"""
	# There is no zope.dublincore analoge for this.
	lastViewed = Number(title="The timestamp at which this object was last viewed.",
						default=0.0)

class IContentTypeMarker(interface.Interface):
	"""
	Marker interface for deriving mimetypes from class names.
	"""

class ICreated(interface.Interface):
	"""
	Something created by an identified entity.
	"""
	creator = interface.Attribute("The creator of this object.")

class ITitled(interface.Interface):
	"""
	A piece of content with a title, either human created or potentially
	automatically generated. (This differs from, say, a person's honorrific title.
	"""
	title = interface.Attribute("The title of this object.")

class IRecordable(interface.Interface):
	"""
	A marker interface for objects whose changes are to be recorded
	"""
	locked = Bool("If this object is locked.", default=False, required=False)
	locked.setTaggedValue('_ext_excluded_out', True)

	def lock(event=True):
		"""
		lock this object
		
		:param event: Notify lock event
		"""

	def unlock(event=True):
		"""
		unlock this object
		
		:param event: Notify unlock event
		"""

	def isLocked():
		"""
		return if this object is locked
		"""
	is_locked = isLocked

class IRecordableContainer(IRecordable):
	"""
	A marker interface for `IRecordable` container objects.
	"""
	child_order_locked = Bool(title="If this children order/set of this container are locked.",
							  default=False, required=False)
	child_order_locked.setTaggedValue('_ext_excluded_out', True)

	def child_order_lock(event=True):
		"""
		child order lock this object
		
		:param event: Notify lock event
		"""
	childOrderLock = child_order_lock

	def child_order_unlock(event=True):
		"""
		child order unlock this object
		
		:param event: Notify unlock event
		"""
	childOrderUnlock = child_order_unlock

	def is_child_order_locked():
		"""
		return if this object is child order locked
		"""
	isChildOrderLocked = is_child_order_locked

class IDefaultPublished(interface.Interface):
	"""
	A marker interface mixed in to an instance to specify
	that it has been "published" by its creator, thus sharing
	it with the default sharing applicable to its creator
	(whatever that means).
	"""

class IObjectPublishedEvent(IObjectEvent):
	"""
	An event that is sent, when an object has been published
	"""

class IObjectUnpublishedEvent(IObjectEvent):
	"""
	An event that is sent, when an object has been unpublished
	"""

@interface.implementer(IObjectPublishedEvent)
class ObjectPublishedEvent(ObjectEvent):
	pass

@interface.implementer(IObjectUnpublishedEvent)
class ObjectUnpublishedEvent(ObjectEvent):
	pass

class IObjectLockedEvent(IObjectEvent):
	"""
	An event that is sent, when an object has been locked
	"""

class IObjectUnlockedEvent(IObjectEvent):
	"""
	An event that is sent, when an object has been unlocked
	"""

@interface.implementer(IObjectLockedEvent)
class ObjectLockedEvent(ObjectEvent):
	pass

@interface.implementer(IObjectUnlockedEvent)
class ObjectUnlockedEvent(ObjectEvent):
	pass

class IObjectChildOrderLockedEvent(IObjectEvent):
	"""
	An event that is sent, when an object has been child-order-locked
	"""

class IObjectChildOrderUnlockedEvent(IObjectEvent):
	"""
	An event that is sent, when an object has been child-order-unlocked
	"""

@interface.implementer(IObjectChildOrderLockedEvent)
class ObjectChildOrderLockedEvent(ObjectEvent):
	pass

@interface.implementer(IObjectChildOrderUnlockedEvent)
class ObjectChildOrderUnlockedEvent(ObjectEvent):
	pass

class IPublishable(interface.Interface):

	publishLastModified = Number(title=u"The timestamp at which this object updated its publication state.",
						  		 default=0.0,
						  		 required=False)

	def publish():
		"""
		Cause this object to provide :class:`IDefaultPublished`
		"""

	def unpublish():
		"""
		Cause this object to no longer provide :class:`IDefaultPublished`
		"""

	def is_published():
		"""
		Return if this object is published
		"""
	isPublished = is_published

class ICalendarPublishableMixin(interface.Interface):

	publishBeginning = ValidDatetime(
		title="This object is not available before this time",
		description="""When present, this specifies the time instant at which
					   this obj is to be available.""",
		required=False)

	publishEnding = ValidDatetime(
		title="This object is not available after this time",
		description="""When present, this specifies the last instance at which
					   this obj is to be available.""",
		required=False)

class ICalendarPublishable(IPublishable, ICalendarPublishableMixin):
	pass

class ICalendarPublishableModifiedEvent(IObjectModifiedEvent, ICalendarPublishableMixin):
	"""
	An event that is sent, when an calendar publishable object is modified
	"""

@interface.implementer(ICalendarPublishableModifiedEvent)
class CalendarPublishableModifiedEvent(ObjectModifiedEvent):

	def __init__(self, obj, publishBeginning=None, publishEnding=None, *descriptions):
		super(CalendarPublishableModifiedEvent, self).__init__(obj, *descriptions)
		self.publishEnding = publishEnding
		self.publishBeginning = publishBeginning

class INoPublishLink(interface.Interface):
	"""
	Marker interface for objects that are publishable but no links to
	publish operations should be provided
	"""
INoPublishLink.setTaggedValue('_ext_is_marker_interface', True)

class IContent(ILastModified, ICreated):
	"""
	It's All Content.
	"""

class IModeledContentBody(interface.Interface):
	"""
	Marker interface for objects that have a iterable `body` attrbute
	with content
	"""
	body = Iterable(title="Content elements")

class IObjectJsonSchemaMaker(interface.Interface):
	"""
	Marker interface for an object Json Schema maker utility
	"""

	def make_schema(schema, user=None):
		"""
		Create the JSON schema.

		:param schema The zope schema to use.
		:param user The user (optional)
		"""

class IIdentity(interface.Interface):
	"""
	Base interface for Identity base objects
	"""

class IExternalService(interface.Interface):
	"""
	Base interface for external services
	"""
