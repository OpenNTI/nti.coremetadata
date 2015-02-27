#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interfaces and support for metadata properties.

.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

from zope.container.interfaces import IContainer as IZContainer
from zope.container.interfaces import IContainerNamesContainer as IZContainerNamesContainer

from zope.location.interfaces import IContained as IZContained

from zope.mimetype.interfaces import mimeTypeConstraint

from zope.schema import Iterable

from nti.schema.field import Number
from nti.schema.field import ValidTextLine
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
					title="The ID (name) of the container to which this object belongs. Should match the __parent__.__name__",
					required=False)
	
	id = DecodingValidTextLine(
					title="The locally unique ID (name) of this object in the container it belongs. Should match the __name__",
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
