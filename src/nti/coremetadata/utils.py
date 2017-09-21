#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import deferredimport

from zope.security.interfaces import NoInteraction
from zope.security.management import getInteraction

from zope.security.management import system_user

from nti.coremetadata.interfaces import IObjectJsonSchemaMaker

logger = __import__('logging').getLogger(__name__)


def current_principal(system=True):
    try:
        result = getInteraction().participations[0].principal
    except (NoInteraction, IndexError, AttributeError):
        result = system_user if system else None
    return result
currentPrincipal = current_principal


def make_schema(schema, user=None, maker=IObjectJsonSchemaMaker, name=u''):
    name = schema.queryTaggedValue('_ext_jsonschema') or name
    schemafier = component.getUtility(maker, name=name)
    result = schemafier.make_schema(schema, user)
    return result


# deprecations


deferredimport.initialize()
deferredimport.deprecated(
    "Import from nti.publishing.utils instead",
    isPublished='nti.publishing.utils:is_published',
    is_published='nti.publishing.utils:is_published',
    isCalendarPublished='nti.publishing.utils:is_calendar_published',
    is_calendar_published='nti.publishing.utils:is_calendar_published')
