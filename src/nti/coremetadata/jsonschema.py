#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from zope.schema.interfaces import IList
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import IObject

from nti.coremetadata.interfaces import ICreated
from nti.coremetadata.interfaces import IRecordable
from nti.coremetadata.interfaces import ICreatedTime
from nti.coremetadata.interfaces import ILastModified
from nti.coremetadata.interfaces import IRecordableContainer

from nti.schema.interfaces import IVariant

from nti.schema.jsonschema import get_ui_types_from_field
from nti.schema.jsonschema import get_ui_type_from_interface
from nti.schema.jsonschema import get_ui_type_from_field_interface

from nti.schema.jsonschema import JsonSchemafier

class CoreJsonSchemafier(JsonSchemafier):

	IGNORE_INTERFACES = (ICreated, IRecordable, ICreatedTime, 
						 ILastModified, IRecordableContainer)

	def allow_field(self, name, field):
		result = name.startswith('_') 
		if not result:
			for iface in self.IGNORE_INTERFACES:
				result = name in iface
				if result:
					break
		return result

	def _process_object(self, field):
		if	  IObject.providedBy(field) \
			and field.schema is not interface.Interface:
			base =      field.schema.queryTaggedValue('_ext_mime_type') \
					or  get_ui_type_from_field_interface(field.schema) \
					or  get_ui_type_from_interface(field.schema)
			return base
		return None

	def _process_variant(self, field, ui_type):
		base_types = set()
		for field in field.fields:
			base = get_ui_types_from_field(field)[1]
			if not base:
				if IObject.providedBy(field):
					base = self._process_object(field)
				if IChoice.providedBy(field):
					_, base = self.get_data_from_choice_field(field)
			if base:
				base_types.add(base.lower())
		if base_types:
			base_types = sorted(base_types, reverse=True)
			ui_base_type = base_types[0] if len(base_types) == 1 else base_types
		else:
			ui_base_type = ui_type
		return ui_base_type

	def get_ui_types_from_field(self, field):
		ui_type, ui_base_type = super(CoreJsonSchemafier, self).get_ui_types_from_field(field)
		if IVariant.providedBy(field) and not ui_base_type:
			ui_base_type = self._process_variant(field, ui_type)
		elif IList.providedBy(field) and not ui_base_type:
			if IObject.providedBy(field.value_type):
				ui_base_type = self._process_object(field.value_type)
			elif IChoice.providedBy(field.value_type):
				_, ui_base_type = self.get_data_from_choice_field(field.value_type)
			elif IVariant.providedBy(field.value_type):
				ui_base_type = self._process_variant(field.value_type, ui_type)
		return ui_type, ui_base_type
	
	def post_process_field(self, name, field, item_schema):
		super(CoreJsonSchemafier, self).post_process_field(name, field, item_schema)