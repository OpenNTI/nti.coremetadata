#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods
import fudge
from hamcrest import calling
from hamcrest import contains
from hamcrest import has_item
from hamcrest import has_length
from hamcrest import instance_of
from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import raises
from hamcrest.core.core import isinstanceof
from nti.coremetadata.interfaces import IMentionable
from nti.coremetadata.mentions.schema import Mention
from nti.coremetadata.mixins import MentionableMixin

from nti.contentfragments.interfaces import PlainTextContentFragment
from zope.schema._bootstrapinterfaces import ConstraintNotSatisfied
from zope.schema._bootstrapinterfaces import WrongContainedType

does_not = is_not

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import unittest

from zope.location.interfaces import IContained as IZContained

from nti.coremetadata.interfaces import IContained
from nti.coremetadata.interfaces import IVersioned

from nti.coremetadata.mixins import ContainedMixin
from nti.coremetadata.mixins import VersionedMixin

from nti.coremetadata.tests import SharedConfiguringTestLayer


class TestMixins(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_contained(self):
        c = ContainedMixin(containerId=u"100", containedId=u"200")
        assert_that(c, validly_provides(IContained))
        assert_that(c, verifiably_provides(IContained))
        assert_that(c, verifiably_provides(IZContained))
        assert_that(c, has_property('containerId', is_("100")))
        assert_that(c, has_property('id', is_("200")))
        
    def test_versioned(self):
        c = VersionedMixin()
        c.update_version(u"100")
        assert_that(c, validly_provides(IVersioned))
        assert_that(c, verifiably_provides(IVersioned))
        assert_that(c, has_property('Version', is_("100")))
        c.update_version()
        assert_that(c, has_property('version', is_not(none())))
        assert_that(c, has_property('version', is_not("100")))


class TestMentionableMixin(unittest.TestCase):
    layer = SharedConfiguringTestLayer

    def test_mentions(self):
        m = MentionableMixin()
        m.mentions = (PlainTextContentFragment(u"user1"),)

        assert_that(m, validly_provides(IMentionable))
        assert_that(m, verifiably_provides(IMentionable))
        assert_that(m, has_property('mentions', is_((u"user1",))))

        assert_that(calling(setattr).with_args(m,
                                               "mentions",
                                               (PlainTextContentFragment(u"user 1"),)),
                    raises(WrongContainedType, "user 1.*mentions"))

        m.mentions = IMentionable["mentions"].fromObject((u"USER1",))
        assert_that(m, has_property('mentions', is_((u"user1",))))

    def test_mentioned(self):
        m = MentionableMixin()
        robert = fudge.Fake("User").has_attr(username="robert")
        tony = fudge.Fake("User").has_attr(username="tony")

        # No mentions
        assert_that(m.isMentionedDirectly(robert), is_(False))

        # Usernames should work as well
        assert_that(m.isMentionedDirectly(robert.username), is_(False))

        m.mentions = (PlainTextContentFragment(u"robert"),)
        assert_that(m.isMentionedDirectly(robert), is_(True))
        assert_that(m.isMentionedDirectly(robert.username), is_(True))
        assert_that(m.isMentionedDirectly(tony), is_(False))
        assert_that(m.isMentionedDirectly(tony.username), is_(False))

