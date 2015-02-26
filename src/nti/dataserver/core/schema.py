#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope.schema.interfaces import InvalidURI

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
