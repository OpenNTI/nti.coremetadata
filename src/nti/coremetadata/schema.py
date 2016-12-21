#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope.schema.interfaces import InvalidURI

from nti.base.interfaces import INamed

from nti.contentfragments.schema import PlainText
from nti.contentfragments.schema import SanitizedHTMLContentFragment

from nti.coremetadata.interfaces import IMedia
from nti.coremetadata.interfaces import ICanvas

from nti.property.schema import DataURI as ProDataURI

from nti.schema.field import Object
from nti.schema.field import Variant
from nti.schema.field import ListOrTupleFromObject
from nti.schema.field import ValidURI as _ValidURI

class DataURI(_ValidURI, ProDataURI): # order matters

	def _validate(self, value):
		super(DataURI, self)._validate(value)
		if not self.is_valid_data_uri(value):
			self._reraise_validation_error(InvalidURI(value),
										   value,
										   _raise=True)

def legacyModeledContentBodyTypes():
	return [SanitizedHTMLContentFragment(min_length=1,
										 description="HTML content that is sanitized and non-empty"),
			PlainText(min_length=1, description="Plain text that is sanitized and non-empty"),
			Object(ICanvas, description="A :class:`.ICanvas`"),
			Object(IMedia, description="A :class:`.IMedia`")]

def bodySchemaField(fields, required=False):
	value_type = Variant(fields=fields, title="A body part", __name__='body')
	return ListOrTupleFromObject(title="The body of this object",
								 description="""
								 An ordered sequence of body parts
								 (:class:`nti.contentfragments.interfaces.IUnicodeContentFragment`
								 or some kinds of :class:`.IModeledContent` such as :class:`.ICanvas`.)
								 """,
								 value_type=value_type,
								 min_length=1,
								 required=required,
								 __name__='body')

def CompoundModeledContentBody(required=False, fields=()):
	"""
	Returns a :class:`zope.schema.interfaces.IField` representing
	the way that a compound body of user-generated content is modeled.
	"""
	fields = legacyModeledContentBodyTypes() if not fields else fields
	return bodySchemaField(fields, required)

def ExtendedCompoundModeledContentBody(required=False):
	fields = legacyModeledContentBodyTypes()
	fields.append(Object(INamed, description="A :class:`.IPloneNamed`"))
	return bodySchemaField(fields, required)
