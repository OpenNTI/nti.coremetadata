#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import assert_that
from hamcrest import has_property

import time
import unittest

from nti.coremetadata.interfaces import ICreatedTime
from nti.coremetadata.interfaces import ILastModified
from nti.coremetadata.mixins import CreatedAndModifiedTimeMixin

from nti.coremetadata.tests import SharedConfiguringTestLayer

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

class TestMixins(unittest.TestCase):

    layer = SharedConfiguringTestLayer
    
    def test_plus_extend( self ):
        c = CreatedAndModifiedTimeMixin()
        for iface in (ICreatedTime, ILastModified):
            assert_that(c, validly_provides(iface))
            assert_that(c, verifiably_provides(iface))

        t = time.time() + 100
        c.updateLastMod(t)
        assert_that(c, has_property('lastModified', is_(t)))
        
        c.updateLastModIfGreater(100)
        assert_that(c, has_property('lastModified', is_(t)))