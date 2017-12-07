#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import contains_string
does_not = is_not

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import pickle
import unittest

from zope.security.interfaces import IPrincipal

from nti.coremetadata.interfaces import ANONYMOUS_USER_NAME

from nti.coremetadata.interfaces import IAnonymousUser

from nti.coremetadata.interfaces import InvalidData
from nti.coremetadata.interfaces import AnonymousUser
from nti.coremetadata.interfaces import ObjectSharingModifiedEvent
from nti.coremetadata.interfaces import FieldCannotBeOnlyWhitespace

from nti.coremetadata.interfaces import checkCannotBeBlank
from nti.coremetadata.interfaces import valid_entity_username

from nti.coremetadata.tests import SharedConfiguringTestLayer


class TestInterfaces(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_invalid_data(self):
        m = InvalidData()
        str(m)  # coverage
        assert_that(m.doc(), contains_string('Invalid Value'))

    def test_checkCannotBeBlank(self):
        checkCannotBeBlank('aizen')
        with self.assertRaises(FieldCannotBeOnlyWhitespace) as e:
            checkCannotBeBlank('\t')
        str(e.exception)  # coverage
        assert_that(e.exception.doc(), contains_string('cannot be blank'))

    def test_valid_entity_username(self):
        assert_that(valid_entity_username('system.'), is_(False))

    def test_anonymous_user(self):
        user = AnonymousUser()
        assert_that(user, validly_provides(IPrincipal))
        assert_that(user, validly_provides(IAnonymousUser))
        assert_that(user, verifiably_provides(IAnonymousUser))

        assert_that(user, has_property('createdTime', is_(0)))
        assert_that(user, has_property('lastModified', is_(0)))
        assert_that(user, has_property('id', is_(ANONYMOUS_USER_NAME)))
        assert_that(user, has_property('username', is_(ANONYMOUS_USER_NAME)))

        assert_that(user.iter_containers(), is_(()))

        with self.assertRaises(TypeError):
            pickle.dumps(user)

        with self.assertRaises(TypeError):
            user.__reduce__()

    def test_event(self):
        m = ObjectSharingModifiedEvent(object(), oldSharingTargets=['a'])
        assert_that(m, has_property('oldSharingTargets', is_(['a'])))
