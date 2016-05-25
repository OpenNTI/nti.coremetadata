#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.coremetadata.interfaces import IObjectJsonSchemaMaker

def make_schema(schema, user=None, maker=IObjectJsonSchemaMaker):
    name = schema.queryTaggedValue('_ext_jsonschema') or u''
    schemafier = component.getUtility(maker, name=name)
    result = schemafier.make_schema(schema=schema, user=user)
    return result
