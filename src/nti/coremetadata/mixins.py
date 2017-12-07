#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time
import isodate

from datetime import datetime

from zope import interface
from zope import deferredimport

from zope.container.contained import Contained

from nti.base._compat import text_

from nti.coremetadata.interfaces import IContained
from nti.coremetadata.interfaces import IVersioned

from nti.property.property import alias

from nti.schema.fieldproperty import UnicodeConvertingFieldProperty

logger = __import__('logging').getLogger(__name__)


# base

deferredimport.initialize()
deferredimport.deprecated(
    "Import from nti.base.mixins instead",
    CreatedTimeMixin='nti.base.mixins:CreatedTimeMixin',
    ModifiedTimeMixin='nti.base.mixins:ModifiedTimeMixin',
    CreatedAndModifiedTimeMixin='nti.base.mixins:ModifiedTimeMixin',)


# recordables


deferredimport.deprecated(
    "Import from nti.recorder.mixins instead",
    RecordableMixin='nti.recorder.mixins:RecordableMixin',
    RecordableContainerMixin='nti.recorder.mixins:RecordableContainerMixin')


# publishing


deferredimport.deprecated(
    "Import from nti.publishing.mixins instead",
    PublishableMixin='nti.publishing.mixins:PublishableMixin',
    CalendarPublishableMixin='nti.publishing.mixins:CalendarPublishableMixin')


# contained


@interface.implementer(IContained)
class ContainedMixin(Contained):
    """
    Defines something that can be logically contained inside another unit
    by reference. Two properties are defined, id and containerId.
    """

    # It is safe to use these properties in persistent objects because
    # they read/write to the __dict__ with the same name as the field,
    # and setattr on the persistent object is what set _p_changed, so
    # assigning to them still changes the object correctly
    containerId = UnicodeConvertingFieldProperty(IContained['containerId'])

    id = UnicodeConvertingFieldProperty(IContained['id'])

    # __name__ is NOT automatically defined as an id alias, because that could lose
    # access to existing data that has a __name__ in its instance dict

    def __init__(self, *args, **kwargs):
        containerId = kwargs.pop('containerId', None)
        containedId = kwargs.pop('containedId', None)
        super(ContainedMixin, self).__init__(*args, **kwargs)
        if containerId is not None:
            self.containerId = containerId
        if containedId is not None:
            self.id = containedId
_ContainedMixin = ZContainedMixin = ContainedMixin


# Versioning


@interface.implementer(IVersioned)
class VersionedMixin(object):

    version = None  # Default to None
    Version = alias('version')

    # pylint: disable=useless-super-delegation
    def __init__(self, *args, **kwargs):
        super(VersionedMixin, self).__init__(*args, **kwargs)

    def _get_version_timestamp(self):
        value = datetime.fromtimestamp(time.time())
        return text_(isodate.datetime_isoformat(value))

    def update_version(self, version=None):
        self.version = version if version else self._get_version_timestamp()
        return self.version
