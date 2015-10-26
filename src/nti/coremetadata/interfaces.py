#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

from nti.schema.field import Number

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
	locked = interface.Attribute("If this object is locked.")
	locked.setTaggedValue('_ext_excluded_out', True)
