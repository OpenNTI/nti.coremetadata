#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from zope.security.interfaces import NoInteraction
from zope.security.management import getInteraction

from zope.security.management import system_user

from nti.coremetadata.interfaces import IObjectJsonSchemaMaker
from nti.coremetadata.interfaces import get_publishable_predicate
from nti.coremetadata.interfaces import get_calendar_publishable_predicate


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
    result = schemafier.make_schema(schema=schema, user=user)
    return result


def is_published(self, interface=None, *args, **kwargs):
    kwargs['principal'] = kwargs.get('principal') or current_principal()
    predicate = get_publishable_predicate(self, interface)
    return predicate(self, *args, **kwargs)
isPublished = is_published


def is_calendar_published(self, interface=None, *args, **kwargs):
    kwargs['principal'] = kwargs.get('principal') or current_principal()
    predicate = get_calendar_publishable_predicate(self, interface)
    return predicate(self, *args, **kwargs)
isCalendarPublished = is_calendar_published
