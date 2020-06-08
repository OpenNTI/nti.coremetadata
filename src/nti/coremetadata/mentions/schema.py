#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.contentfragments.schema import PlainTextLine

from nti.coremetadata.mentions.interfaces import IMentionField

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IMentionField)
class Mention(PlainTextLine):
    """
    Requires its content to be only one plain text word that is lowercase.
    """

    def fromUnicode(self, value):
        return super(Mention, self).fromUnicode(value.lower())

    def constraint(self, value):
        return super(Mention, self).constraint(value) and ' ' not in value
