#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import component
from zope import interface

from zope.interface.interfaces import ObjectEvent
from zope.interface.interfaces import IObjectEvent

from zope.container.interfaces import IContainer

from zope.lifecycleevent import ObjectModifiedEvent

from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from zope.location.interfaces import IContained as IZContained

from zope.mimetype.interfaces import IContentTypeAware

from zope.schema import Iterable

from zope.security.management import system_user

from nti.base.interfaces import IFile
from nti.base.interfaces import INamed
from nti.base.interfaces import ITitled
from nti.base.interfaces import ICreated
from nti.base.interfaces import ILastModified

from nti.contentfragments.schema import Tag
from nti.contentfragments.schema import Title

from nti.schema.field import Bool
from nti.schema.field import Number
from nti.schema.field import Object
from nti.schema.field import ListOrTuple
from nti.schema.field import ValidTextLine
from nti.schema.field import ValidDatetime
from nti.schema.field import UniqueIterable
from nti.schema.field import TupleFromObject
from nti.schema.field import DecodingValidTextLine

SYSTEM_USER_ID = system_user.id
SYSTEM_USER_NAME = getattr(system_user, 'title').lower()

import zope.deferredimport
zope.deferredimport.initialize()

zope.deferredimport.deprecated(
	"Import from nti.base.interfaces instead",
	ILastViewed='nti.base.interfaces:ILastViewed',
	ICreatedTime='nti.base.interfaces:ICreatedTime',)

class IContentTypeMarker(interface.Interface):
	"""
	Marker interface for deriving mimetypes from class names.
	"""

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

	def publish(event=True):
		"""
		Cause this object to provide :class:`IDefaultPublished`
		
		:param event: Notify unlock event
		"""

	def unpublish(event=True):
		"""
		Cause this object to no longer provide :class:`IDefaultPublished`
		
		:param event: Notify unlock event
		"""

	def is_published(*args, **kwargs):
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

class IPublishablePredicate(interface.Interface):
	"""
	Subscriber for publishable objects to determiend if an object
	is published
	"""
	
	def is_published(publishable, principal=None, context=None, *args, **kwargs):
		"""
		return if the specified publishable is published for the given 
		principal and context
		"""
	isPublished = is_published

class ICalendarPublishablePredicate(interface.Interface):
	"""
	Subscriber for calendar-publishable objects to determiend if an object
	is published
	"""
	
	def is_published(publishable, principal=None, context=None, *args, **kwargs):
		"""
		return if the specified calendar publishable is published for the given 
		principal and context
		"""
	isPublished = is_published

def get_publishable_predicate(publishable, interface=None):
	interface = IPublishablePredicate if interface is None else interface
	predicates = list(component.subscribers((publishable,), interface))
	def uber_filter(publishable, *args, **kwargs):
		return all((p.is_published(publishable, *args, **kwargs) for p in predicates))
	return uber_filter

def get_calendar_publishable_predicate(publishable, interface=None):
	interface = ICalendarPublishablePredicate if interface is None else interface
	predicates = list(component.subscribers((publishable,), interface))
	def uber_filter(publishable, *args, **kwargs):
		return all((p.is_published(publishable, *args, **kwargs) for p in predicates))
	return uber_filter
	
# containers

class IShouldHaveTraversablePath(interface.Interface):
	"""
	A marker interface for things that should have a resource
	path that can be traversed. This is a temporary measure (everything
	*should* eventually have a resource path) and a non-disruptive
	way to start requiring ILink externalization to use resource paths
	exclusively.
	"""
	
class IContained(IZContained):
	"""
	Something logically contained inside exactly one (named) :class:`IContainer`.
	Most uses of this should now use :class:`zope.container.interfaces.IContained`.
	(This class previously did not extend that interface; it does now.)
	"""

	# For BWC, these are not required
	containerId = DecodingValidTextLine(
					title="The ID (name) of the container to which this object belongs. "
						  "Should match the __parent__.__name__",
					required=False)

	id = DecodingValidTextLine(
					title="The locally unique ID (name) of this object in the container "
						  "it belongs. Should match the __name__",
					required=False)

class INamedContainer(IContainer):
	"""
	A container with a name.
	"""
	container_name = interface.Attribute("The human-readable nome of this container.")

zope.deferredimport.deprecated(
	"Import from zope.container.interfaces instead",
	IZContainer='zope.container.interfaces:IContainer')

# content

class IContent(ILastModified, ICreated):
	"""
	It's All Content.
	"""

class IModeledContent(IContent, IContained, IContentTypeMarker):
	"""
	Content accessible as objects.
	Interfaces that extend this MUST directly provide IContentTypeAware.
	"""

class IEnclosedContent(IContent, IContained, IContentTypeAware,
					   IShouldHaveTraversablePath):
	"""
	Content accessible logically within another object.
	This typically serves as a wrapper around another object, whether
	modeled content or unmodeled content. In the case of modeled content,
	its `__parent__` should be this object, and the `creator` should be the same
	as this object's creator.
	"""
	name = interface.Attribute("The human-readable name of this content.")
	data = interface.Attribute("The actual enclosed content.")

class IModeledContentBody(interface.Interface):
	"""
	Marker interface for objects that have a iterable `body` attrbute
	with content
	"""
	body = Iterable(title="Content elements")

class ITitledContent(ITitled):
	"""
	A piece of content with a title, either human created or potentially
	automatically generated. (This differs from, say, a person's honorrific title.
	"""
	title = Title()

class ITaggedContent(interface.Interface):
	"""
	Something that can contain tags.
	"""

	tags = TupleFromObject(title="Applied Tags",
						   value_type=Tag(min_length=1, title="A single tag",
										  description=Tag.__doc__, __name__='tags'),
						   unique=True,
						   default=())

# content types

class IIdentity(interface.Interface):
	"""
	Base interface for Identity base objects
	"""

class IThreadable(interface.Interface):
	"""
	Something which can be used in an email-like threaded fashion.

	.. note:: All the objects should be IThreadable, but it is not possible
		to put that in a constraint without having infinite recursion
		problems.
	"""

	inReplyTo = Object(interface.Interface,
					   title="""The object to which this object is directly a reply.""",
					   required=False)

	references = ListOrTuple(title="""A sequence of objects this object transiently references, in order up to the root""",
							 value_type=Object(interface.Interface, title="A reference"),
							 default=())

	replies = UniqueIterable(title="All the direct replies of this object",
							 description="This property will be automatically maintained.",
							 value_type=Object(interface.Interface, title="A reply"))
	replies.setTaggedValue('_ext_excluded_out', True)  # Internal use only

	referents = UniqueIterable(title="All the direct and indirect replies to this object",
							   description="This property will be automatically maintained.",
							   value_type=Object(interface.Interface, title="A in/direct reply"))
	referents.setTaggedValue('_ext_excluded_out', True)  # Internal use only

class IWeakThreadable(IThreadable):
	"""
	Just like :class:`IThreadable`, except with the expectation that
	the items in the reply chain are only weakly referenced and that
	they are automatically cleaned up (after some time) when deleted. Thus,
	it is not necessarily clear when a ``None`` value for ``inReplyTo``
	means the item has never had a reply, or the reply has been deleted.
	"""

class IInspectableWeakThreadable(IWeakThreadable):
	"""
	A weakly threaded object that provides information about its
	historical participation in a thread.
	"""

	def isOrWasChildInThread():
		"""
		Return a boolean object indicating if this object is or was
		ever part of a thread chain. If this returns a true value, it
		implies that at some point ``inRelpyTo`` was non-None.
		"""

class IReadableShared(interface.Interface):
	"""
	Something that can be shared with others (made visible to
	others than its creator. This interface exposes the read side of sharing.
	"""

	def isSharedWith(principal):
		"""
		Is this object directly or indirectly shared with the given principal?
		"""

	def isSharedDirectlyWith(principal):
		"""
		Is this object directly shared with the given target?
		"""

	def isSharedIndirectlyWith(principal):
		"""
		Is this object indirectly shared with the given target?
		"""

	sharingTargets = UniqueIterable(
		title="A set of entities this object is directly shared with (non-recursive, non-flattened)",
		value_type=Object(IIdentity, title="An entity shared with"),
		required=False,
		default=(),
		readonly=True)

	flattenedSharingTargets = UniqueIterable(
		title="A set of entities this object is directly or indirectly shared with (recursive, flattened)",
		value_type=Object(IIdentity, title="An entity shared with"),
		required=False,
		default=(),
		readonly=True)

	flattenedSharingTargetNames = UniqueIterable(
		title="The ids of all the entities (e.g. communities, etc) this obj is shared with.",
		description=" This is a convenience property for reporting the ids of all "
			" entities this object is shared with, directly or indirectly. Note that the ids reported "
			" here are not necessarily globally unique and may not be resolvable as such.",
		value_type=DecodingValidTextLine(title="The entity identifier"),
		required=False,
		default=frozenset(),
		readonly=True)

	def getFlattenedSharingTargetNames():
		"""
		This is a convenience method for reporting the ids of all
		entities this object is shared with. Note that the ids reported
		here are not necessarily globally unique and may not be resolvable as such.

		This method is deprecated in favor of the property.

		:return: Set of ids this object is shared with.
		"""

class IWritableShared(IReadableShared):
	"""
	The writable part of sharing. All mutations are expected to go through
	this interface, not by adjusting the properties directly.
	"""

	def addSharingTarget(target):
		"""
		Allow `target` to see this object. This does not actually make that so,
		simply records the fact that the target should be able to see this
		object.

		:param target: Iterable of entities, or a single entity.
		"""

	def clearSharingTargets():
		"""
		Mark this object as being shared with no one (visible only to the creator).
		Does not actually change any visibilities. Causes `flattenedSharingTargetNames`
		to be empty.
		"""

	def updateSharingTargets(replacement_targets):
		"""
		Mark this object as being shared with exactly the entities provided in ``replacement_targets``.
		Does not actually change any visibilities. Causes `sharingTargets` and `flattenedSharingTargets`
		to reflect these changes.
		"""

class IShareableModeledContent(IWritableShared, IModeledContent):
	"""
	Modeled content that can be shared.
	"""

	sharedWith = UniqueIterable(
		title="The ids of the entities we are shared directly with, taking externalization of local ids into account",
		value_type=DecodingValidTextLine(title="The username or NTIID"),
		required=False,
		default=frozenset())

class IModeledContentFile(IFile,
						  INamed, 
						  IThreadable,
						  ILastModified,
						  IShareableModeledContent):
	name = ValidTextLine(title="Identifier for the file", required=False, default=None)
IContentFile = IModeledContentFile # BWC

# media types

class ICanvas(IShareableModeledContent, IThreadable):
	"""
	A drawing or whiteboard that maintains a Z-ordered list of figures/shapes.
	"""

	def __getitem__(i):
		"""
		Retrieve the figure/shape at index `i`.
		"""

	def append(shape):
		"""
		Adds the shape to the top of the list of shapes.
		"""

class ICanvasShape(IZContained):
	"""
	Marker interface for a canvas shape
	"""

class ICanvasURLShape(ICanvasShape):
	"""
	Marker interface for a URL canvas shape
	"""
	url = interface.Attribute("Shape url")

class IMedia(IShareableModeledContent, IThreadable):
	"""
	A media object
	"""

class IEmbeddedMedia(IMedia):
	embedURL = ValidTextLine(title=u'media URL', required=True)
	type = ValidTextLine(title=u'media type', required=False)

class IEmbeddedVideo(IEmbeddedMedia):
	"""
	A video source object
	"""
	VideoId = ValidTextLine(title=u'the video identifier', required=False)

class IEmbeddedAudio(IEmbeddedMedia):
	"""
	A audio source object
	"""

# schema maker

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

# aux interfaces

class IExternalService(interface.Interface):
	"""
	Base interface for external services
	"""
