#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

from zope.container.interfaces import IContainer as IZContainer
from zope.container.interfaces import IContainerNamesContainer as IZContainerNamesContainer

from zope.location.interfaces import IContained as IZContained

from zope.mimetype.interfaces import IContentTypeAware
from zope.mimetype.interfaces import mimeTypeConstraint

from zope.schema import Iterable

from nti.schema.field import Number
from nti.schema.field import Object
from nti.schema.field import ListOrTuple
from nti.schema.field import ValidTextLine
from nti.schema.field import UniqueIterable
from nti.schema.field import ValidChoice as Choice
from nti.schema.field import DecodingValidTextLine

### Core

class IEnvironmentSettings(interface.Interface):
	pass

class IDataserver(interface.Interface):
	pass

class IIdentity(interface.Interface):
	pass

### Links

class ILink(interface.Interface):
	"""
	A relationship between the containing entity and
	some other entity.
	"""

	rel = Choice(
		title=u'The type of relationship',
		values=('related', 'alternate', 'self', 'enclosure', 'edit', 'like',
				'unlike', 'content'))

	target = interface.Attribute(
		"""
		The target of the relationship.

		May be an actual object of some type or may be a string. If a string,
		will be interpreted as an absolute or relative URI.
		""")

	elements = Iterable(
		title="Additional path segments to put after the `target`",
		description="""Each element must be a string and will be a new URL segment.

		This is useful for things like view names or namespace traversals.""")

	target_mime_type = DecodingValidTextLine(
		title='Target Mime Type',
		description="The mime type explicitly specified for the target object, if any",
		constraint=mimeTypeConstraint,
		required=False)

	method = DecodingValidTextLine(
		title='HTTP Method',
		description="The HTTP method most suited for this link relation",
		required=False)

	title = ValidTextLine(
		title="Human readable title",
		required=False)

class ILinkExternalHrefOnly(ILink):
	"""
	A marker interface intended to be used when a link
	object should be externalized as its 'href' value only and
	not the wrapping object.
	"""

class ILinked(interface.Interface):
	"""
	Something that possess links to other objects.
	"""
	links = Iterable(
		title=u'Iterator over the ILinks this object contains.')


### Containers

# TODO: Very much of our home-grown container
# stuff can be replaced by zope.container
IContainer = IZContainer

# Recall that IContainer is an IReadContainer and IWriteContainer, providing:
# __setitem__, __delitem__, __getitem__, keys()/values()/items()
IContainerNamesContainer = IZContainerNamesContainer

class INamedContainer(IContainer):
	"""
	A container with a name.
	"""
	container_name = interface.Attribute(
		"""
		The human-readable nome of this container.
		""")

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

### Time tracking

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

class ICreated(interface.Interface):
	"""
	Something created by an identified entity.
	"""
	creator = interface.Attribute("The creator of this object.")

### markers

class IShouldHaveTraversablePath(interface.Interface):
	"""
	A marker interface for things that should have a resource
	path that can be traversed. This is a temporary measure (everything
	*should* eventually have a resource path) and a non-disruptive
	way to start requiring ILink externalization to use resource paths
	exclusively.
	"""

class INeverStoredInSharedStream(interface.Interface):
	"""
	A marker interface used when distributing changes to show that this
	object should not be stored in shared streams.
	"""

class IMutedInStream(interface.Interface):
	"""
	A marker interface used when distributed changes to keep this
	object out of the local stream cache.
	"""

class INotModifiedInStreamWhenContainerModified(interface.Interface):
	"""
	When applied to :class:`IContainer` instances, this is a marker
	interface that says when a :class:`IContainerModifiedEvent` is fired,
	as is done when children are added or removed from the container,
	the stream is not updated. This prevents spurious changing of
	shared/created events into (newer) modified events.
	"""

class IContentTypeMarker(interface.Interface):
	"""
	Marker interface for deriving mimetypes from class names.
	"""

### content

class IContent(ILastModified, ICreated):
	"""
	It's All Content.
	"""

class IModeledContent(IContent, IContained, IContentTypeMarker):
	"""
	Content accessible as objects.
	Interfaces that extend this MUST directly provide IContentTypeAware.
	"""

class IEnclosedContent(IContent, IContained, IContentTypeAware, IShouldHaveTraversablePath):
	"""
	Content accessible logically within another object.
	This typically serves as a wrapper around another object, whether
	modeled content or unmodeled content. In the case of modeled content,
	its `__parent__` should be this object, and the `creator` should be the same
	as this object's creator.
	"""
	name = interface.Attribute("The human-readable name of this content.")
	data = interface.Attribute("The actual enclosed content.")

### content types

class IThreadable(interface.Interface):
	"""
	Something which can be used in an email-like threaded fashion.

	.. note:: All the objects should be IThreadable, but it is not possible
		to put that in a constraint without having infinite recursion
		problems.
	"""

	inReplyTo = Object( interface.Interface,
						title="""The object to which this object is directly a reply.""",
						required=False)

	references = ListOrTuple( title="""A sequence of objects this object transiently references, in order up to the root""",
							  value_type=Object(interface.Interface, title="A reference"),
							  default=())

	replies = UniqueIterable( title="All the direct replies of this object",
							  description="This property will be automatically maintained.",
							  value_type=Object(interface.Interface, title="A reply") )
	replies.setTaggedValue( '_ext_excluded_out', True ) # Internal use only

	referents = UniqueIterable( title="All the direct and indirect replies to this object",
								description="This property will be automatically maintained.",
								value_type=Object(interface.Interface, title="A in/direct reply") )
	referents.setTaggedValue( '_ext_excluded_out', True ) # Internal use only

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
		"Is this object directly shared with the given target?"

	def isSharedIndirectlyWith(principal):
		"Is this object indirectly shared with the given target?"

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

### media types

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

class IEmbeddedAudio(IEmbeddedMedia):
	"""
	A video source object
	"""
