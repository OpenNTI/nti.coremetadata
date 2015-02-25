#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interfaces and support for metadata properties.

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
