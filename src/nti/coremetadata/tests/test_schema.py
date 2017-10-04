#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_not
does_not = is_not

import unittest

from nti.coremetadata.tests import SharedConfiguringTestLayer


class TestSchema(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_foo(self):
        pass
