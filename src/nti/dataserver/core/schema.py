#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope.schema.interfaces import InvalidURI
from zope.schema.interfaces import ValidationError
from zope.schema.fieldproperty import FieldProperty

from nti.common import dataurl

from nti.schema.field import ValidURI as _ValidURI

class DataURI(_ValidURI):
	"""
	A URI field that ensures and requires its value to be
	a data URI. The field value is a :class:`.DataURL`.
	"""

	def _validate(self, value):
		super(DataURI,self)._validate(value)
		if not value.startswith(b'data:'):
			self._reraise_validation_error( InvalidURI(value),
											value,
											_raise=True )

	def fromUnicode( self, value ):
		if isinstance(value, dataurl.DataURL):
			return value

		super(DataURI, self).fromUnicode(value)
		return dataurl.DataURL(value)

class AbstractFieldProperty(FieldProperty):

	def __init__( self, field, name=None ):
		super(AbstractFieldProperty, self).__init__( field, name=name )
		self._field = field

	def _to_tuple(self, value):
		if value and isinstance( value, list ):
			value = tuple(value)
		return value

	def _adapt(self, value):
		return self._field.fromObject( value )
	
	def __set__( self, inst, value ):
		value = self._to_tuple(value)
		try:
			super(AbstractFieldProperty,self).__set__( inst, value )
		except ValidationError:
			## Hmm. try to adapt
			value = self._adapt(value)
			super(AbstractFieldProperty, self).__set__( inst, value )

class BodyFieldProperty(AbstractFieldProperty):

	def _adapt(self, value):
		## allow ascii strings for old app tests
		value = [x.decode('utf-8') if isinstance(x, str) else x for x in value]
		value = tuple( (self._field.value_type.fromObject(x) for x in value ) )
		return value
NoteBodyFieldProperty = BodyFieldProperty

class MessageInfoBodyFieldProperty(AbstractFieldProperty):

	def _to_tuple(self, value):
		# Turn bytes into text
		if isinstance( value, str ):
			value = value.decode( 'utf-8' )
		# Wrap single strings automatically
		if isinstance( value, unicode ):
			value = (value,)
		# Make immutable
		if value and isinstance( value, list ):
			value = tuple(value)
		return value
