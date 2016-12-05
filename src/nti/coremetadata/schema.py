#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope.schema.interfaces import InvalidURI

from nti.property.schema import DataURI as ProDataURI

from nti.schema.field import ValidURI as _ValidURI

class DataURI(_ValidURI, ProDataURI): # order matters

	def _validate(self, value):
		super(DataURI, self)._validate(value)
		if not self.is_valid_data_uri(value):
			self._reraise_validation_error(InvalidURI(value),
										   value,
										   _raise=True)