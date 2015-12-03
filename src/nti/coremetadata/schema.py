#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six
from datetime import date
from datetime import datetime

import isodate
from isodate import ISO8601Error

from zope import interface

from zope.interface.common.idatetime import IDate
from zope.interface.common.idatetime import IDateTime

from zope.schema.interfaces import InvalidURI
from zope.schema.interfaces import IFromUnicode

from nti.common import dataurl

from nti.schema.field import ValidURI as _ValidURI
from nti.schema.field import ValidDatetime as _ValidDatetime

class DataURI(_ValidURI):
	"""
	A URI field that ensures and requires its value to be
	a data URI. The field value is a :class:`.DataURL`.
	"""

	@classmethod
	def is_valid_data_uri(cls, value):
		return value and value.startswith(b'data:')

	def _validate(self, value):
		super(DataURI, self)._validate(value)
		if not self.is_valid_data_uri(value):
			self._reraise_validation_error(InvalidURI(value),
										   value,
										   _raise=True)

	def fromUnicode(self, value):
		if isinstance(value, dataurl.DataURL):
			return value

		super(DataURI, self).fromUnicode(value)
		return dataurl.DataURL(value)

def parse_datetime(value, default=None):
	value = default if value is None else value
	if value is None:
		return None
	elif isinstance(value, (int, float)):
		value = datetime.fromtimestamp(value)
	elif isinstance(value, six.string_types):
		# check if there are any adapters in context
		for schema in (IDateTime, IDate):
			try:
				adapted = schema(value, None)
				if adapted is not None:
					break
			except Exception:
				adapted = None # ignore

		# try raw isodate
		if adapted is None:
			try:
				value = isodate.parse_datetime(value)
			except (ISO8601Error, ValueError):
				value = isodate.parse_date(value)
				value = datetime.fromordinal(value.toordinal())
		elif isinstance(adapted, date):
			value = datetime.fromordinal(adapted.toordinal())
		else:
			value = adapted
	return value

@interface.implementer(IFromUnicode)
class Datetime(_ValidDatetime):

	def _validate(self, value):
		try:
			if value is not None and not isinstance(value, self._type):
				parse_datetime(value)
				return
		except Exception:
			pass # let super handle it
		super(_ValidDatetime, self)._validate(value)

	def fromUnicode(self, value):
		try:
			v = parse_datetime(value)
		except Exception:
			raise ValueError('invalid literal for Datetime(): %s' % value)
		self.validate(v)
		return v

	def set(self, obj, value):
		value = parse_datetime(value)
		super(_ValidDatetime, self).set(obj, value)
