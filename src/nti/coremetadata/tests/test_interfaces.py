#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import unittest

from zope.security.interfaces import IPrincipal

from nti.coremetadata.interfaces import ANONYMOUS_USER_NAME

from nti.coremetadata.interfaces import IAnonymousUser

from nti.coremetadata.interfaces import AnonymousUser

from nti.coremetadata.tests import SharedConfiguringTestLayer


class TestInterfaces(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_anonymous_user(self):
        user = AnonymousUser()
        assert_that(user, validly_provides(IPrincipal))
        assert_that(user, validly_provides(IAnonymousUser))
        assert_that(user, verifiably_provides(IAnonymousUser))
        assert_that(user, has_property('createdTime', is_(0)))
        assert_that(user, has_property('lastModified', is_(0)))
        assert_that(user, has_property('id', is_(ANONYMOUS_USER_NAME)))
        assert_that(user, has_property('username', is_(ANONYMOUS_USER_NAME)))
