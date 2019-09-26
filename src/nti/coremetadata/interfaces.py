#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class,inconsistent-mro

import time

from zope import interface
from zope import deferredimport

from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAttributeAnnotatable

from zope.container.interfaces import IContainer as IZContainer
from zope.container.interfaces import IContainerNamesContainer as IZContainerNamesContainer

from zope.dublincore.interfaces import IDCDescriptiveProperties

from zope.i18n import translate

from zope.interface.common.mapping import IEnumerableMapping

from zope.interface.interfaces import ObjectEvent
from zope.interface.interfaces import IObjectEvent

from zope.lifecycleevent import ObjectModifiedEvent

from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from zope.location.interfaces import IContained as IZContained

from zope.mimetype.interfaces import IContentTypeAware

from zope.schema import Iterable

from zope.security.interfaces import IPrincipal
from zope.security.interfaces import ISystemPrincipal

from zope.security.management import system_user

from nti.base.interfaces import ITitled
from nti.base.interfaces import ICreated
from nti.base.interfaces import INamedFile
from nti.base.interfaces import ILastModified
from nti.base.interfaces import ITitledDescribed

from nti.contentfragments.schema import Tag
from nti.contentfragments.schema import Title
from nti.contentfragments.schema import PlainText

from nti.contenttypes.reports.interfaces import IReportContext

from nti.coremetadata import MessageFactory as _

from nti.mimetype.interfaces import IContentTypeMarker

from nti.property.property import alias

from nti.schema.field import Bool
from nti.schema.field import Number
from nti.schema.field import Object
from nti.schema.field import TextLine
from nti.schema.field import DateTime
from nti.schema.field import ListOrTuple
from nti.schema.field import ValidTextLine
from nti.schema.field import UniqueIterable
from nti.schema.field import TupleFromObject
from nti.schema.field import DecodingValidTextLine

from nti.schema.interfaces import InvalidValue

from nti.schema.jsonschema import TAG_HIDDEN_IN_UI
from nti.schema.jsonschema import TAG_REQUIRED_IN_UI
from nti.schema.jsonschema import TAG_READONLY_IN_UI

SYSTEM_USER_ID = system_user.id
SYSTEM_USER_NAME = getattr(system_user, 'title').lower()

deferredimport.initialize()
deferredimport.deprecated(
    "Import from nti.base.interfaces instead",
    ILastViewed='nti.base.interfaces:ILastViewed',
    ICreatedTime='nti.base.interfaces:ICreatedTime',)


# pylint: disable=E0213,E0211


class InvalidData(InvalidValue):
    """
    Invalid Value
    """

    i18n_message = None

    def __str__(self):
        if self.i18n_message:
            return translate(self.i18n_message)
        return super(InvalidData, self).__str__()

    def doc(self):
        if self.i18n_message:
            return self.i18n_message
        return self.__class__.__doc__
_InvalidData = InvalidData  # BWC


class FieldCannotBeOnlyWhitespace(InvalidData):

    i18n_message = _(u"The field cannot be blank.")

    def __init__(self, field_name, value, field_external=None):
        external = field_external or (field_name and field_name.capitalize())
        super(FieldCannotBeOnlyWhitespace, self).__init__(self.i18n_message, external,
                                                          value, value=value)


def checkCannotBeBlank(value):
    if not value or not value.strip():
        raise FieldCannotBeOnlyWhitespace(None, value)
    return True


# principals

#: Alias for principal that represents the system (application) itself.
ISystemUserPrincipal = ISystemPrincipal # BWC

# recordables


deferredimport.deprecated(
    "Import from nti.recorder.interfaces instead",
    IRecordable='nti.recorder.interfaces:IRecordable',
    IRecordableContainer='nti.recorder.interfaces:IRecordableContainer')

deferredimport.deprecated(
    "Import from nti.recorder.interfaces instead",
    ObjectLockedEvent='nti.recorder.interfaces:ObjectLockedEvent',
    IObjectLockedEvent='nti.recorder.interfaces:IObjectLockedEvent',
    ObjectUnlockedEvent='nti.recorder.interfaces:ObjectUnlockedEvent',
    IObjectUnlockedEvent='nti.recorder.interfaces:IObjectUnlockedEvent',
    ObjectChildOrderLockedEvent='nti.recorder.interfaces:ObjectChildOrderLockedEvent',
    IObjectChildOrderLockedEvent='nti.recorder.interfaces:IObjectChildOrderLockedEvent',
    ObjectChildOrderUnlockedEvent='nti.recorder.interfaces:ObjectChildOrderUnlockedEvent',
    IObjectChildOrderUnlockedEvent='nti.recorder.interfaces:IObjectChildOrderUnlockedEvent',)


# published objects


deferredimport.deprecated(
    "Import from nti.publishing.interfaces instead",
    IDefaultPublished='nti.publishing.interfaces:IDefaultPublished',
    ObjectPublishedEvent='nti.publishing.interfaces:ObjectPublishedEvent',
    IObjectPublishedEvent='nti.publishing.interfaces:IObjectPublishedEvent',
    ObjectUnpublishedEvent='nti.publishing.interfaces:ObjectUnpublishedEvent',
    IObjectUnpublishedEvent='nti.publishing.interfaces:IObjectUnpublishedEvent',)

deferredimport.deprecated(
    "Import from nti.publishing.interfaces instead",
    IPublishable='nti.publishing.interfaces:IPublishable',
    ICalendarPublishable='nti.publishing.interfaces:ICalendarPublishable',
    ICalendarPublishableMixin='nti.publishing.interfaces:ICalendarPublishableMixin',
    CalendarPublishableModifiedEvent='nti.publishing.interfaces:CalendarPublishableModifiedEvent',
    ICalendarPublishableModifiedEvent='nti.publishing.interfaces:ICalendarPublishableModifiedEvent')

deferredimport.deprecated(
    "Import from nti.publishing.interfaces instead",
    INoPublishLink='nti.publishing.interfaces:INoPublishLink',
    IPublishablePredicate='nti.publishing.interfaces:IPublishablePredicate',
    ICalendarPublishablePredicate='nti.publishing.interfaces:ICalendarPublishableMixin')

deferredimport.deprecated(
    "Import from nti.publishing.interfaces instead",
    get_publishable_predicate='nti.publishing.interfaces:get_publishable_predicate',
    get_calendar_publishable_predicate='nti.publishing.interfaces:get_calendar_publishable_predicate')


# containers

# Very much of our home-grown container
# stuff can be replaced by zope.container
IContainer = IZContainer

# Recall that IContainer is an IReadContainer and IWriteContainer, providing:
# __setitem__, __delitem__, __getitem__, keys()/values()/items()
IContainerNamesContainer = IZContainerNamesContainer


class IShouldHaveTraversablePath(interface.Interface):
    """
    A marker interface for things that should have a resource
    path that can be traversed. This is a temporary measure (everything
    *should* eventually have a resource path) and a non-disruptive
    way to start requiring ILink externalization to use resource paths
    exclusively.
    """


class INeverStoredInSharedStream(interface.Interface):
    """
    A marker interface used when distributing changes to show that this
    object should not be stored in shared streams.
    """


class IMutedInStream(interface.Interface):
    """
    A marker interface used when distributed changes to keep this
    object out of the local stream cache.
    """


class INotModifiedInStreamWhenContainerModified(interface.Interface):
    """
    When applied to :class:`IContainer` instances, this is a marker
    interface that says when a :class:`IContainerModifiedEvent` is fired,
    as is done when children are added or removed from the container,
    the stream is not updated. This prevents spurious changing of
    shared/created events into (newer) modified events.
    """


class IContained(IZContained):
    """
    Something logically contained inside exactly one (named) :class:`IContainer`.
    Most uses of this should now use :class:`zope.container.interfaces.IContained`.
    (This class previously did not extend that interface; it does now.)
    """

    # For BWC, these are not required
    containerId = DecodingValidTextLine(
        title=u"The ID (name) of the container to which this object belongs. "
        u"Should match the __parent__.__name__",
        required=False)

    id = DecodingValidTextLine(
        title=u"The locally unique ID (name) of this object in the container "
        u"it belongs. Should match the __name__",
        required=False)


class INamedContainer(IContainer):
    """
    A container with a name.
    """
    container_name = interface.Attribute(
        "The human-readable nome of this container.")


deferredimport.deprecated(
    "Import from nti.datastructures.interfaces instead",
    IHTC_NEW_FACTORY='nti.datastructures.interfaces:IHTC_NEW_FACTORY',
    IHomogeneousTypeContainer='nti.datastructures.interfaces:IHomogeneousTypeContainer')


class IContainerIterable(interface.Interface):
    """
    Something that can enumerate the containers (collections)
    it contains.
    """

    # This is ill-defined. One would expect it to be all containers,
    # but the only implementation (users.User) actually limits it to named
    # containers
    def iter_containers():
        """
        :return: An iteration across the containers held in this object.
        """
    itercontainers = iter_containers


# content


class IContent(ILastModified, ICreated):
    """
    It's All Content.
    """


class IModeledContent(IContent, IContained, IContentTypeMarker):
    """
    Content accessible as objects.
    Interfaces that extend this MUST directly provide IContentTypeAware.
    """


class IEnclosedContent(IContent, IContained, IContentTypeAware,
                       IShouldHaveTraversablePath):
    """
    Content accessible logically within another object.
    This typically serves as a wrapper around another object, whether
    modeled content or unmodeled content. In the case of modeled content,
    its `__parent__` should be this object, and the `creator` should be the same
    as this object's creator.
    """
    name = interface.Attribute("The human-readable name of this content.")
    data = interface.Attribute("The actual enclosed content.")


class IModeledContentBody(interface.Interface):
    """
    Marker interface for objects that have a iterable `body` attrbute
    with content
    """
    body = Iterable(title=u"Content elements")


class ITitledContent(ITitled):
    """
    A piece of content with a title, either human created or potentially
    automatically generated. (This differs from, say, a person's honorrific title.
    """
    title = Title()


class ITitledDescribedContent(ITitledContent, ITitledDescribed, IDCDescriptiveProperties):
    """
    Extend this class to add the ``title`` and ``description`` properties.
    This class overrides the :mod:`zope.dublincore` properties with more specific
    versions.
    """

    description = PlainText(
        title=u"The human-readable description of this object."
    )


class ITaggedContent(interface.Interface):
    """
    Something that can contain tags.
    """

    tags = TupleFromObject(title=u"Applied Tags",
                           value_type=Tag(min_length=1,
                                          title=u"A single tag",
                                          __name__=u'tags'),
                           unique=True,
                           default=())


# content types


class IIdentity(interface.Interface):
    """
    Base interface for Identity base objects
    """


deferredimport.deprecated(
    "Import from nti.threadable.interfaces instead",
    IThreadable='nti.threadable.interfaces:IThreadable',
    IWeakThreadable='nti.threadable.interfaces:IWeakThreadable',
    IInspectableWeakThreadable='nti.threadable.interfaces:IInspectableWeakThreadable')


class IReadableShared(interface.Interface):
    """
    Something that can be shared with others (made visible to
    others than its creator. This interface exposes the read side of sharing.
    """

    def isSharedWith(principal):
        """
        Is this object directly or indirectly shared with the given principal?
        """

    def isSharedDirectlyWith(principal):
        """
        Is this object directly shared with the given target?
        """

    def isSharedIndirectlyWith(principal):
        """
        Is this object indirectly shared with the given target?
        """

    sharingTargets = UniqueIterable(
        title=u"A set of entities this object is directly shared with (non-recursive, non-flattened)",
        value_type=Object(IIdentity, title=u"An entity shared with"),
        required=False,
        default=(),
        readonly=True)

    flattenedSharingTargets = UniqueIterable(
        title=u"A set of entities this object is directly or indirectly shared with (recursive, flattened)",
        value_type=Object(IIdentity, title=u"An entity shared with"),
        required=False,
        default=(),
        readonly=True)

    flattenedSharingTargetNames = UniqueIterable(
        title=u"The ids of all the entities (e.g. communities, etc) this obj is shared with.",
        description=u"This is a convenience property for reporting the ids of all "
        u" entities this object is shared with, directly or indirectly. Note that the ids reported "
        u" here are not necessarily globally unique and may not be resolvable as such.",
        value_type=DecodingValidTextLine(title=u"The entity identifier"),
        required=False,
        default=frozenset(),
        readonly=True)

    def getFlattenedSharingTargetNames():
        """
        This is a convenience method for reporting the ids of all
        entities this object is shared with. Note that the ids reported
        here are not necessarily globally unique and may not be resolvable as such.

        This method is deprecated in favor of the property.

        :return: Set of ids this object is shared with.
        """


class IWritableShared(IReadableShared):
    """
    The writable part of sharing. All mutations are expected to go through
    this interface, not by adjusting the properties directly.
    """

    def addSharingTarget(target):
        """
        Allow `target` to see this object. This does not actually make that so,
        simply records the fact that the target should be able to see this
        object.

        :param target: Iterable of entities, or a single entity.
        """

    def clearSharingTargets():
        """
        Mark this object as being shared with no one (visible only to the creator).
        Does not actually change any visibilities. Causes `flattenedSharingTargetNames`
        to be empty.
        """

    def updateSharingTargets(replacement_targets):
        """
        Mark this object as being shared with exactly the entities provided in ``replacement_targets``.
        Does not actually change any visibilities. Causes `sharingTargets` and `flattenedSharingTargets`
        to reflect these changes.
        """


class IShareableModeledContent(IWritableShared, IModeledContent):
    """
    Modeled content that can be shared.
    """

    sharedWith = UniqueIterable(
        title=u"The ids of the entities we are shared directly with, "
              u"taking externalization of local ids into account",
        value_type=DecodingValidTextLine(title=u"The username or NTIID"),
        required=False,
        default=frozenset())


class IUserGeneratedData(ICreated):
    """
    marker interface for user generated data
    """


class IModeledContentFile(INamedFile,
                          ILastModified,
                          IShareableModeledContent):
    name = ValidTextLine(title=u"Identifier for the file",
                         required=False,
                         default=None)
IContentFile = IModeledContentFile  # BWC


# media types


class ICanvas(IShareableModeledContent):
    """
    A drawing or whiteboard that maintains a Z-ordered list of figures/shapes.
    """

    def __getitem__(i):
        """
        Retrieve the figure/shape at index `i`.
        """

    def append(shape):
        """
        Adds the shape to the top of the list of shapes.
        """


class ICanvasShape(IZContained):
    """
    Marker interface for a canvas shape
    """


class ICanvasURLShape(ICanvasShape):
    """
    Marker interface for a URL canvas shape
    """
    url = interface.Attribute("Shape url")

    file = interface.Attribute("Shape url file")
    file.setTaggedValue('_ext_excluded_out', True)


class IMedia(IShareableModeledContent):
    """
    A media object
    """


class IEmbeddedMedia(IMedia):
    embedURL = ValidTextLine(title=u'media URL', required=True)
    type = ValidTextLine(title=u'media type', required=False)


class IEmbeddedVideo(IEmbeddedMedia):
    """
    A video source object
    """
    VideoId = ValidTextLine(title=u'the video identifier', required=False)


class IEmbeddedAudio(IEmbeddedMedia):
    """
    A audio source object
    """

# entity


ME_USER_ID = u'me'
EVERYONE_GROUP_NAME = u'system.Everyone'
AUTHENTICATED_GROUP_NAME = u'system.Authenticated'
UNAUTHENTICATED_PRINCIPAL_NAME = u'system.Unknown'

RESERVED_USER_IDS = (SYSTEM_USER_ID, SYSTEM_USER_NAME, EVERYONE_GROUP_NAME,
                     AUTHENTICATED_GROUP_NAME, ME_USER_ID)

LOWER_RESERVED_USER_IDS = tuple((x.lower() for x in RESERVED_USER_IDS))


class IUnauthenticatedPrincipal(IPrincipal):
    pass


@interface.implementer(IUnauthenticatedPrincipal)
class UnauthenticatedPrincipal(object):
    id = UNAUTHENTICATED_PRINCIPAL_NAME
    title = UNAUTHENTICATED_PRINCIPAL_NAME
    description = UNAUTHENTICATED_PRINCIPAL_NAME


def username_is_reserved(username):
    return username and (username.lower() in LOWER_RESERVED_USER_IDS
                         or username.lower().startswith('system.'))


def valid_entity_username(entity_name):
    return not username_is_reserved(entity_name)


class ICreatedUsername(interface.Interface):
    """
    Something created by an identified entity, expressed
    as a (globally unique) username.
    """
    creator_username = DecodingValidTextLine(title=u'The username',
                                             constraint=valid_entity_username,
                                             readonly=True)


class IEntity(IIdentity, IZContained, IAnnotatable, IShouldHaveTraversablePath,
              INeverStoredInSharedStream):

    username = DecodingValidTextLine(title=u'The username',
                                     constraint=valid_entity_username)


class IMissingEntity(IEntity):
    """
    A proxy object for a missing, unresolved or unresolvable
    entity.
    """


class IMissingUser(IMissingEntity):
    """
    A proxy object for a missing user.
    """


class IDynamicSharingTarget(IEntity):
    """
    These objects reverse the normal sharing; instead of being
    pushed at sharing time to all the named targets, shared data
    is instead *pulled* at read time by an individual member of this
    entity. As such, these objects represent collections of members,
    but not necessarily enumerable collections (e.g., communities
    are not enumerable).
    """


class IAutoSubscribeMembershipPredicate(ICreated, ILastModified):
    """
    Handles auto-subscription logic for a membership entity (e.g. ICommunity).
    """

    def accept_user(user):
        """
        Returns a bool whether or not this user should be accepted.
        """


class ICommunity(IDynamicSharingTarget):

    public = Bool(title=u'Public flag', required=False, default=True)

    joinable = Bool(title=u'Joinable flag', required=False, default=True)

    username = DecodingValidTextLine(title=u'The username',
                                     constraint=valid_entity_username)

    auto_subscribe = Object(IAutoSubscribeMembershipPredicate,
                            title=u"The auto-subscribe object for this community.",
                            required=False)

    def iter_members():
        """
        Return an iterable of the entity objects that are a member
        of this community.
        """

    def iter_member_usernames():
        """
        Return an iterable of the usernames of members of this community.
        """


class IUnscopedGlobalCommunity(ICommunity):
    """
    A community that is visible across the entire "world". One special case of this
    is the ``Everyone`` or :const:`EVERYONE_USER_NAME` community. These
    are generally not considered when computing relationships or visibility between users.
    """


class ISiteCommunity(ICommunity):
    """
    A :class:`ICommunity` that is associated with a site.
    """


class IUser(IEntity, IContainerIterable, IReportContext):
    """
    A user of the system. Notice this is not an IPrincipal.
    This interface needs finished and fleshed out.
    """

    username = DecodingValidTextLine(title=u'The username', min_length=5)

    # Note: z3c.password provides a PasswordField we could use here
    # when we're sure what it does and that validation works out
    password = interface.Attribute("The password")

    lastLoginTime = interface.Attribute("The last login time")
    lastLoginTime.setTaggedValue(TAG_READONLY_IN_UI, True)

    lastSeenTime = interface.Attribute("The last seen time")
    lastSeenTime.setTaggedValue(TAG_READONLY_IN_UI, True)


ANONYMOUS_USER_NAME = UNAUTHENTICATED_PRINCIPAL_NAME


class IAnonymousUser(IUser):
    """
    The anonymous user, which is not persistent.
    """


@interface.implementer(IAnonymousUser, IAttributeAnnotatable)
class AnonymousUser(UnauthenticatedPrincipal):

    username = __name__ = alias('id')

    lastModified = createdTime = lastSeenTime = lastLoginTime = 0

    def __init__(self, parent=None):
        self.__parent__ = parent

    @property
    def password(self):
        return None

    def iter_containers(self):
        return ()
    itercontainers = iter_containers

    def __reduce_ex__(self, protocol):
        raise TypeError(u"Not allowed to pickle %s" % self.__class__)

    def __reduce__(self):
        return self.__reduce_ex__(0)
UnauthenticatedUser = AnonymousUser  # alias


class IUsernameSubstitutionPolicy(interface.Interface):
    """
    Marker interface to register an utility that replaces
    the username value for another
    """

    def replace(username):
        """
        return a substituted name for the specifed username
        """


class IFriendsList(IModeledContent, IEntity,
                   INotModifiedInStreamWhenContainerModified):
    """
    Define a list of users.

    .. note:: The inheritance from :class:`IEntity` is probably a mistake to be changed;
            these are not globally named.
    """

    def __iter__():
        """
        Iterating over a FriendsList iterates over its friends
        (as Entity objects), resolving weak refs.
        """

    def __contains__(friend):
        """
        Is the given entity a member of this friends list?
        """

    def addFriend(friend):
        """
        Adding friends causes our creator to follow them.

        :param friend: May be another friends list, an entity, a
                       string naming a user, or even a dictionary containing
                       a 'Username' property.
        """


class IUseNTIIDAsExternalUsername(interface.Interface):
    """
    A marker interface for IEntity objects that are not globally resolvable
    by their 'username'; instead, everywhere we would write out
    a username we must instead write the NTIID.
    """


class IUserEvent(IObjectEvent):
    """
    An object event where the object is a user.
    """

    object = Object(IUser,
                    title=u"The User (an alias for user). You can add event listeners "
                    u"based on the interfaces of this object.")
    user = Object(IUser,
                  title=u"The User (an alias for object). You can add event listeners "
                  u"based on the interfaces of this object.")


@interface.implementer(IUserEvent)
class UserEvent(ObjectEvent):
    user = alias('object')


class IUserLastSeenEvent(IObjectEvent):
    """
    Fired after a user has been last seen.
    """
    request = interface.Attribute(u"Request")
    timestamp = interface.Attribute(u"Timestamp")


@interface.implementer(IUserLastSeenEvent)
class UserLastSeenEvent(ObjectEvent):

    def __init__(self, obj, timestamp=None, request=None):
        super(UserLastSeenEvent, self).__init__(obj)
        self.request = request
        self.timestamp = timestamp or time.time()


class IUserProcessedContextsEvent(IObjectEvent):
    """
    Fired after a user has seen[visted] a context.
    """
    request = interface.Attribute(u"Request")
    timestamp = interface.Attribute(u"Timestamp")
    context_ids = interface.Attribute(u"Context [nti]ids")


@interface.implementer(IUserProcessedContextsEvent)
class UserProcessedContextsEvent(ObjectEvent):

    def __init__(self, obj, context_ids, timestamp=None, request=None):
        super(UserProcessedContextsEvent, self).__init__(obj)
        self.request = request
        self.context_ids = context_ids
        self.timestamp = timestamp or time.time()


class IEntityFollowingEvent(IObjectEvent):
    """
    Fired when an entity begins following another entity.
    The ``object`` is the entity that is now following the other entity.
    """

    object = Object(IEntity,
                    title=u"The entity now following the other entity")

    now_following = Object(IEntity,
                           title=u"The entity that is now being followed by the object.")


class IFollowerAddedEvent(IObjectEvent):
    """
    Fired when an entity is followed by another entity.

    The ``object`` is the entity that is now being followed.
    """

    object = Object(IEntity, title=u"The entity now being followed.")

    followed_by = Object(IEntity,
                         title=u"The entity that is now following the object.")


@interface.implementer(IEntityFollowingEvent)
class EntityFollowingEvent(ObjectEvent):

    def __init__(self, entity, now_following):
        ObjectEvent.__init__(self, entity)
        self.now_following = now_following


@interface.implementer(IFollowerAddedEvent)
class FollowerAddedEvent(ObjectEvent):

    def __init__(self, entity, followed_by):
        ObjectEvent.__init__(self, entity)
        self.followed_by = followed_by


class IStopFollowingEvent(IObjectEvent):
    """
    Fired when an entity stop following another entity.
    The ``object`` is the entity that is no longer follows the other entity.
    """
    object = Object(IEntity,
                    title=u"The entity not longer following the other entity")

    not_following = Object(IEntity,
                           title=u"The entity that is no longer being followed by the object.")


@interface.implementer(IStopFollowingEvent)
class StopFollowingEvent(ObjectEvent):

    def __init__(self, entity, not_following):
        ObjectEvent.__init__(self, entity)
        self.not_following = not_following


class IStartDynamicMembershipEvent(IObjectEvent):
    """
    Fired when an dynamic membershis (i.e. join a community is recorded)
    The ``object`` is the entity that is is recording the membership.
    """
    object = Object(IEntity, title=u"The entity joining the dynamic target")
    target = Object(IDynamicSharingTarget, title=u"The dynamic target to join")


@interface.implementer(IStartDynamicMembershipEvent)
class StartDynamicMembershipEvent(ObjectEvent):

    def __init__(self, entity, target):
        ObjectEvent.__init__(self, entity)
        self.target = target


class IStopDynamicMembershipEvent(IObjectEvent):
    """
    Fired when an dynamic membershis (i.e. unjoin a community) is removed
    The ``object`` is the entity that is is leaving the membership.
    """
    object = Object(IEntity, title=u"The entity unjoining the dynamic target")

    target = Object(IDynamicSharingTarget,
                    title=u"The dynamic target to be leaving")


@interface.implementer(IStopDynamicMembershipEvent)
class StopDynamicMembershipEvent(ObjectEvent):

    def __init__(self, entity, target):
        ObjectEvent.__init__(self, entity)
        self.target = target


class IDynamicSharingTargetFriendsList(IDynamicSharingTarget,
                                       IFriendsList,
                                       IUseNTIIDAsExternalUsername):
    """
    A type of :class:`IDynamicSharingTarget` that is a list of members.
    """

    About = ValidTextLine(title=u'About',
                          description=u"A short description of a group",
                          max_length=500,
                          required=False,
                          constraint=checkCannotBeBlank)

    Locked = Bool(title=u'Locked flag. No group code, no removal',
                  required=False,
                  default=False)


class IObjectSharingModifiedEvent(IObjectModifiedEvent):
    """
    An event broadcast when we know that the sharing settings of
    an object have been changed.
    """

    oldSharingTargets = UniqueIterable(
        title=u"A set of entities this object is directly shared with, before the "
              u"change (non-recursive, non-flattened)",
        value_type=Object(IEntity, title=u"An entity shared with"),
        required=False,
        default=(),
        readonly=True)


@interface.implementer(IObjectSharingModifiedEvent)
class ObjectSharingModifiedEvent(ObjectModifiedEvent):

    def __init__(self, obj, *descriptions, **kwargs):
        super(ObjectSharingModifiedEvent, self).__init__(obj, *descriptions)
        self.oldSharingTargets = kwargs.pop('oldSharingTargets', ())


class IUsernameIterable(interface.Interface):
    """
    Something that can iterate across usernames belonging to system :class:`IUser`, typically
    usernames somehow contained in or stored in this object (or its context).
    """

    def __iter__():
        """
        Return iterator across username strings. The usernames may refer to users
        that have already been deleted.
        """


class IIntIdIterable(interface.Interface):
    """
    Something that can iterate across intids.
    Typically this will be used as a mixin interface,
    with the containing object defining what sort of
    reference the intid will be to.

    In general, the caller cannot assume that the intids
    are entirely valid, and should use ``queryObject``
    instead of ``getObject``.
    """

    def iter_intids():
        """
        Return an iterable across intids.
        """


class IEntityUsernameIterable(interface.Interface):
    """
    A specific way to iterate across usernames.
    """

    def iter_usernames():
        """
        Return an iterable across the usernames
        of this object.
        """


class IEntityIterable(interface.Interface):
    """
    Something that can iterate across entities (usually but not always :class:`IUser`), typically
    entities somehow contained in or stored in this object (or its context).
    """

    def __iter__():
        """
        Return iterator across entity objects.
        """


class ISharingTargetEntityIterable(IEntityIterable):
    """
    Something that can iterate across entities that should be expanded
    for sharing purposes.
    """


class IEntityContainer(interface.Interface):
    """
    Something that can report whether an entity "belongs" to it.
    """

    def __contains__(entity):
        """
        Is the entity a member of this container?
        """


# entity index

#: The name of the utility that the Zope Catalog
#: for users should be registered under
ENTITY_CATALOG_NAME = 'nti.dataserver.++etc++entity-catalog'


IX_SITE = 'site'
IX_ALIAS = 'alias'
IX_EMAIL = 'email'
IX_TOPICS = 'topics'
IX_MIMETYPE = 'mimeType'
IX_REALNAME = 'realname'
IX_USERNAME = 'username'
IX_DISPLAYNAME = 'displayname'
IX_CONTACT_EMAIL = 'contact_email'
IX_REALNAME_PARTS = 'realname_parts'
IX_LASTSEEN = IX_LASTSEEN_TIME = 'lastSeenTime'
IX_CONTACT_EMAIL_RECOVERY_HASH = 'contact_email_recovery_hash'
IX_PASSWORD_RECOVERY_EMAIL_HASH = 'password_recovery_email_hash'

IX_IS_COMMUNITY = 'is_community'
IX_EMAIL_VERIFIED = 'email_verified'
IX_IS_DEACTIVATED = 'is_deactivated'
IX_OPT_IN_EMAIL_COMMUNICATION = 'opt_in_email_communication'
IX_INVALID_EMAIL = 'invalid_email'


# last seen context


class IContextLastSeenRecord(interface.Interface):

    username = DecodingValidTextLine(title=u"The username.",
                                     required=False)

    context = DecodingValidTextLine(title=u"The context id.",
                                    required=True)

    timestamp = Number(title=u"The timestamp", required=True)


class IContextLastSeenContainer(IEnumerableMapping):
    """
    Something that is an unordered bag of context ntiid and
    the last timestamp they were visited (seen)
    """

    def append(item, timestamp=None):
        """
        Add an item to this container
        """

    def extend(items, timestamp=None):
        """
        Add the specified items to this container
        """

    def contexts():
        """
        return an iterable with all context ntiids in this container
        """

    def pop(k, default):
        """
        remove specified key and return the corresponding value
        """

    def get_timestamp(item):
        """
        Return the timestamp for the specified key
        """

# schema maker


class IObjectJsonSchemaMaker(interface.Interface):
    """
    Marker interface for an object Json Schema maker utility
    """

    def make_schema(schema, user=None):
        """
        Create the JSON schema.

        :param schema The zope schema to use.
        :param user The user (optional)
        """

# context objects


class IContainerContext(interface.Interface):
    """
    An object that represents the context of the given container.
    """
    context_id = ValidTextLine(title=u"The ntiid of the context.",
                               default=u'')


class IContextAnnotatable(IAttributeAnnotatable):
    """
    Marker interface that the given object may have a root
    'context' object, represented by ``IContainerContext``.
    """

# deleted objects

class IDeleteLockedEntity(interface.Interface):
    """
    A marker interface that prevents an entity from being being deleted
    or deactivated. This is used to keep high-value entity objects from
    being deleted unintentionally.
    """


class IDeleteLockedCommunity(interface.Interface):
    """
    A marker interface that prevents a community from being being deleted
    or deactivated. This is used to keep high-value entity objects from
    being deleted unintentionally.
    """


class IDeactivatedObject(interface.Interface):
    """
    The base marker interface for a deactivated object.
    """


class IDeactivatedEntity(IDeactivatedObject):
    """
    The base marker interface for a deactivated entity.
    """


class IDeactivatedUser(IDeactivatedEntity):
    """
    The marker interface for a deactivated user.
    """


class IDeactivatedCommunity(IDeactivatedEntity):
    """
    The marker interface for a deactivated community.
    """


class IDeletedObjectPlaceholder(IDeactivatedObject):
    """
    Marker interface to be applied to things that have actually
    been deleted, but, for whatever reason, some trace object
    has to be left behind. These will typically be rendered specially.
    """


class IDeactivatedObjectEvent(IObjectEvent):
    """
    Fired when an entity is deactivated
    """


class IDeactivatedEntityEvent(IDeactivatedObjectEvent):
    """
    Fired when an object is deactivated
    """


class IDeactivatedUserEvent(IDeactivatedEntityEvent):
    """
    Fired when a user is deactivated
    """


class IDeactivatedCommunityEvent(IDeactivatedEntityEvent):
    """
    Fired when a community is deactivated
    """

@interface.implementer(IDeactivatedObjectEvent)
class DeactivatedObjectEvent(ObjectEvent):
    pass


@interface.implementer(IDeactivatedEntityEvent)
class DeactivatedEntityEvent(DeactivatedObjectEvent):
    pass


@interface.implementer(IDeactivatedUserEvent)
class DeactivatedUserEvent(DeactivatedEntityEvent):
    pass


@interface.implementer(IDeactivatedCommunityEvent)
class DeactivatedCommunityEvent(DeactivatedEntityEvent):
    pass


class IReactivatedObjectEvent(IObjectEvent):
    """
    Fired when an entity is reactivated
    """


class IReactivatedEntityEvent(IReactivatedObjectEvent):
    """
    Fired when an object is reactivated
    """


class IReactivatedUserEvent(IReactivatedEntityEvent):
    """
    Fired when a user is reactivated
    """


class IReactivatedCommunityEvent(IReactivatedEntityEvent):
    """
    Fired when a community is reactivated
    """

@interface.implementer(IReactivatedObjectEvent)
class ReactivatedObjectEvent(ObjectEvent):
    pass


@interface.implementer(IReactivatedEntityEvent)
class ReactivatedEntityEvent(ReactivatedObjectEvent):
    pass


@interface.implementer(IReactivatedUserEvent)
class ReactivatedUserEvent(ReactivatedEntityEvent):
    pass


@interface.implementer(IReactivatedCommunityEvent)
class ReactivatedCommunityEvent(ReactivatedEntityEvent):
    pass


# aux interfaces


class IExternalService(interface.Interface):
    """
    Base interface for external services
    """


class IRedisClient(IExternalService):
    """
    A very poor abstraction of a :class:`redis.StrictRedis` client.
    In general, this should only be used in the lowest low level code and
    abstractions should be built on top of this.

    When creating keys to use in the client, try to use traversal-friendly
    keys, the same sorts of keys that can be found in the ZODB: unicode names
    separated by the ``/`` character.
    """


class IMemcachedClient(IExternalService):
    """
    A very poor abstraction of a :class:`memcache.Client` client.
    In general, this should only be used in the lowest low level code and
    abstractions should be built on top of this.

    When creating keys to use in the client, try to use traversal-friendly
    keys, the same sorts of keys that can be found in the ZODB: unicode names
    separated by the ``/`` character.

    The values you set must be picklable.
    """

    def get(key):
        """
        Return the unpickled value, or None
        """

    def set(key, value, time=0):
        """
        Pickle the value and store it, returning True on success.
        """

    def delete(key):
        """
        Remove the key from the cache.
        """


class IEnvironmentSettings(interface.Interface):
    pass


class IDataserver(interface.Interface):
    pass


class IVersioned(interface.Interface):
    """
    An interface containing version information. Useful when guarding
    against overwrites when editing an object.
    """

    version = TextLine(
        title=u"The structural version of this object.",
        description=u"An artificial string signifying the 'structural version' "
        u"of this object.",
        required=False)

    def update_version(version=None):
        """
        Update the version for this object. If no arg given, the
        default algorithm will be used.
        """
IVersioned['version'].setTaggedValue(TAG_HIDDEN_IN_UI, True)
IVersioned['version'].setTaggedValue(TAG_REQUIRED_IN_UI, False)
IVersioned['version'].setTaggedValue(TAG_READONLY_IN_UI, True)


# ACLs


class IACE(interface.Interface):
    """
    An Access Control Entry (one item in an ACL).

    An ACE is an iterable holding three items: the
    *action*, the *actor*, and the *permissions*. (Typically,
    it is implemented as a three-tuple).

    The *action* is either :const:`ACE_ACT_ALLOW` or :const:`ACE_ACT_DENY`. The former
    specifically grants the actor the permission. The latter specifically denies
    it (useful in a hierarchy of ACLs or actors [groups]). The *actor* is the
    :class:`IPrincipal` that the ACE refers to. Finally, the *permissions* is one (or
    a list of) :class:`IPermission`, or the special value :const:`ALL_PERMISSIONS`
    """

    def __iter__():
        """
        Returns three items.
        """


class IACL(interface.Interface):
    """
    Something that can iterate across :class:`IACE` objects.
    """

    def __iter__():
        """
        Iterates across :class:`IACE` objects.
        """


class IACLProvider(interface.Interface):
    """
    Something that can provide an ACL for itself.
    """

    __acl__ = interface.Attribute("An :class:`IACL`")


class ISupplementalACLProvider(interface.Interface):
    """
    Some that that can provide a supplemental ACL to the
    primary :class:`IACLProvider` of an object.
    """

    __acl__ = interface.Attribute("An :class:`IACL`")


class IACLProviderCacheable(interface.Interface):
    """
    A marker interface (usually added through configuration) that states
    that the results of adapting an object to an :class:`IACLProvider` can
    be cached on the object itself, making it its own provider.

    Do not do this for persistent objects or objects who's ACL provider
    may differ in various sites due to configuration, or which makes decisions
    to produce a partial ACL based on the current user (or anything else that
    could be considered "current" such as a current request). In summary, it is
    generally only safe to do when the ACL information comes from external sources
    such as files or strings.
    """

class ILastSeenProvider(interface.Interface):
    """
    Something that can provide a last seem time for a specific user on course/book etc.
    """
    lastSeenTime = DateTime(title=u"The latest date when a user accessed to something",
                            required=True,
                            default=None)


class IUserDefinedOrderedContent(interface.Interface):
    """
    An object that allows it's underlying order to be defined by users.
    """

    ordered_keys = ListOrTuple(value_type=ValidTextLine(title=u"object id"),
                               title=u"ordered keys", required=True)
