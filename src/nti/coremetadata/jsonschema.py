#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from zope.schema.interfaces import IList
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import IObject
from zope.schema.interfaces import ISequence
from zope.schema.interfaces import IFromUnicode

from nti.base.interfaces import ICreated
from nti.base.interfaces import ICreatedTime
from nti.base.interfaces import ILastModified

from nti.coremetadata.interfaces import IObjectJsonSchemaMaker

from nti.schema.interfaces import IVariant
from nti.schema.interfaces import IListOrTuple

from nti.schema.jsonschema import get_ui_types_from_field
from nti.schema.jsonschema import get_ui_type_from_interface
from nti.schema.jsonschema import get_ui_type_from_field_interface

from nti.schema.jsonschema import JsonSchemafier

#: Fields attribute
FIELDS = u'Fields'

logger = __import__('logging').getLogger(__name__)


class CoreJsonSchemafier(JsonSchemafier):

    IGNORE_INTERFACES = (ICreated, ILastModified, ICreatedTime)

    def allow_field(self, name, field):
        result = not(   name.startswith('_')
                     or field.queryTaggedValue('_ext_excluded_out'))
        if result:
            for iface in self.IGNORE_INTERFACES:
                if name in iface:
                    result = False
                    break
        return result

    def process_object(self, field):
        if      IObject.providedBy(field) \
            and field.schema is not interface.Interface:
            base = field.schema.queryTaggedValue('_ext_mime_type') \
                or get_ui_type_from_field_interface(field.schema) \
                or get_ui_type_from_interface(field.schema)
            return base
        return None
    _process_object = process_object

    def process_variant(self, field, ui_type):
        base_types = set()
        for field in field.fields:
            base = get_ui_types_from_field(field)[1]
            if not base:
                if IObject.providedBy(field):
                    base = self.process_object(field)
                if IChoice.providedBy(field):
                    _, base = self.get_data_from_choice_field(field)
            if base:
                base_types.add(base.lower())
        if base_types:
            ui_base_type = base_types = sorted(base_types, reverse=True)
            if len(base_types) == 1:
                ui_base_type = base_types[0]
        else:
            ui_base_type = ui_type
        return ui_base_type
    _process_variant = process_variant

    def get_ui_types_from_field(self, field):
        result = JsonSchemafier.get_ui_types_from_field(self, field)
        ui_type, ui_base_type = result # start
        # handle variant
        if IVariant.providedBy(field) and not ui_base_type:
            ui_base_type = self.process_variant(field, ui_type)
        # handle list types
        elif   (   IListOrTuple.providedBy(field) 
                or IList.providedBy(field) 
                or ISequence.providedBy(field)) \
            and not ui_base_type:
            if IObject.providedBy(field.value_type):
                ui_base_type = self.process_object(field.value_type)
            elif IChoice.providedBy(field.value_type):
                value_type = field.value_type
                _, ui_base_type = self.get_data_from_choice_field(value_type)
            elif IVariant.providedBy(field.value_type):
                ui_base_type = self.process_variant(field.value_type, ui_type)
            elif IFromUnicode.providedBy(field.value_type):
                ui_base_type = 'string'
            # check for Sequence
            ui_type = 'List' if ui_type == 'Sequence' else ui_type
            ui_type = ui_type or 'List'
            ui_type = ui_type.title()
        # handle objects
        elif IObject.providedBy(field) and not ui_base_type:
            ui_base_type = self.process_object(field)
            ui_type = ui_type or 'Object'
        return ui_type, ui_base_type


@interface.implementer(IObjectJsonSchemaMaker)
class DefaultObjectJsonSchemaMaker(object):

    maker = CoreJsonSchemafier

    def make_schema(self, schema, unused_user=None):
        result = dict()
        maker = self.maker(schema)
        result[FIELDS] = maker.make_schema()
        return result
