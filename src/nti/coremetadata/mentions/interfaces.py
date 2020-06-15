#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from nti.contentfragments.interfaces import IPlainTextLineField


class IMentionField(IPlainTextLineField):
    """
    Requires its content to be only one plain text word that is lowercase.

    .. versionadded:: 1.2.0
    """
