#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from datetime import datetime

from zope import component
from zope import interface

from nti.coremetadata.interfaces import IPublishable
from nti.coremetadata.interfaces import IDefaultPublished
from nti.coremetadata.interfaces import ICalendarPublishable
from nti.coremetadata.interfaces import IPublishablePredicate
from nti.coremetadata.interfaces import ICalendarPublishablePredicate

@component.adapter(IPublishable)
@interface.implementer(IPublishablePredicate)
class DefaultPublishablePredicate(object):

    __slots__ = ()

    def __init__(self, *args):
        pass

    def is_published(self, publishable, *args, **kwargs):
        return IDefaultPublished.providedBy(publishable)
    isPublished = is_published

@component.adapter(ICalendarPublishable)
@interface.implementer(ICalendarPublishablePredicate)
class DefaultCalendarPublishablePredicate(object):

    __slots__ = ()

    def __init__(self, *args):
        pass

    def is_published(self, publishable, *args, **kwargs):
        now = datetime.utcnow()
        end = publishable.publishEnding
        start = publishable.publishBeginning
        result =     (   IDefaultPublished.providedBy(publishable)
                      or (start is not None and now > start)) \
                and (end is None or now < end)
        return bool(result)
    isPublished = is_published
