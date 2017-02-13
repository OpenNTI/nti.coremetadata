#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import component
from zope import interface

from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAttributeAnnotatable

from zope.container.interfaces import IContainer as IZContainer
from zope.container.interfaces import IContainerNamesContainer as IZContainerNamesContainer

from zope.i18n import translate

from zope.interface.interfaces import ObjectEvent
from zope.interface.interfaces import IObjectEvent

from zope.lifecycleevent import ObjectModifiedEvent

from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from zope.location.interfaces import IContained as IZContained

from zope.mimetype.interfaces import IContentTypeAware

from zope.schema import Iterable

from zope.security.interfaces import IPrincipal

from zope.security.management import system_user

from nti.base.interfaces import IFile
from nti.base.interfaces import INamed
from nti.base.interfaces import ITitled
from nti.base.interfaces import ICreated
from nti.base.interfaces import ILastModified
from nti.base.interfaces import IContentTypeMarker

from nti.contentfragments.schema import Tag
from nti.contentfragments.schema import Title

from nti.coremetadata import MessageFactory as _

from nti.schema.field import Bool
from nti.schema.field import Number
from nti.schema.field import Object
from nti.schema.field import ValidTextLine
from nti.schema.field import ValidDatetime
from nti.schema.field import UniqueIterable
from nti.schema.field import TupleFromObject
from nti.schema.field import DecodingValidTextLine

from nti.schema.interfaces import InvalidValue

SYSTEM_USER_ID = system_user.id
SYSTEM_USER_NAME = getattr(system_user, 'title').lower()

import zope.deferredimport
zope.deferredimport.initialize()

zope.deferredimport.deprecated(
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
_InvalidData = InvalidData


class FieldCannotBeOnlyWhitespace(InvalidData):

    i18n_message = _("The field cannot be blank.")

    def __init__(self, field_name, value, field_external=None):
        super(FieldCannotBeOnlyWhitespace, self).__init__(self.i18n_message,
                                                          field_external or (
                                                              field_name and field_name.capitalize()),
                                                          value,
                                                          value=value)


def checkCannotBeBlank(value):
    if not value or not value.strip():
        raise FieldCannotBeOnlyWhitespace(None, value)
    return True


# principals

class ISystemUserPrincipal(IPrincipal):
    """
    Marker for a system user principal
    """

# recordables


class IRecordable(interface.Interface):
    """
    A marker interface for objects whose changes are to be recorded
    """
    locked = Bool("If this object is locked.", default=False, required=False)
    locked.setTaggedValue('_ext_excluded_out', True)

    def lock(event=True):
        """
        lock this object

        :param event: Notify lock event
        """

    def unlock(event=True):
        """
        unlock this object

        :param event: Notify unlock event
        """

    def isLocked():
        """
        return if this object is locked
        """
    is_locked = isLocked


class IRecordableContainer(IRecordable):
    """
    A marker interface for `IRecordable` container objects.
    """
    child_order_locked = Bool(title="If this children order/set of this container are locked.",
                              default=False, required=False)
    child_order_locked.setTaggedValue('_ext_excluded_out', True)

    def child_order_lock(event=True):
        """
        child order lock this object

        :param event: Notify lock event
        """
    childOrderLock = child_order_lock

    def child_order_unlock(event=True):
        """
        child order unlock this object

        :param event: Notify unlock event
        """
    childOrderUnlock = child_order_unlock

    def is_child_order_locked():
        """
        return if this object is child order locked
        """
    isChildOrderLocked = is_child_order_locked

# published objects


class IDefaultPublished(interface.Interface):
    """
    A marker interface mixed in to an instance to specify
    that it has been "published" by its creator, thus sharing
    it with the default sharing applicable to its creator
    (whatever that means).
    """


class IObjectPublishedEvent(IObjectEvent):
    """
    An event that is sent, when an object has been published
    """


class IObjectUnpublishedEvent(IObjectEvent):
    """
    An event that is sent, when an object has been unpublished
    """


@interface.implementer(IObjectPublishedEvent)
class ObjectPublishedEvent(ObjectEvent):
    pass


@interface.implementer(IObjectUnpublishedEvent)
class ObjectUnpublishedEvent(ObjectEvent):
    pass


class IObjectLockedEvent(IObjectEvent):
    """
    An event that is sent, when an object has been locked
    """


class IObjectUnlockedEvent(IObjectEvent):
    """
    An event that is sent, when an object has been unlocked
    """


@interface.implementer(IObjectLockedEvent)
class ObjectLockedEvent(ObjectEvent):
    pass


@interface.implementer(IObjectUnlockedEvent)
class ObjectUnlockedEvent(ObjectEvent):
    pass


class IObjectChildOrderLockedEvent(IObjectEvent):
    """
    An event that is sent, when an object has been child-order-locked
    """


class IObjectChildOrderUnlockedEvent(IObjectEvent):
    """
    An event that is sent, when an object has been child-order-unlocked
    """


@interface.implementer(IObjectChildOrderLockedEvent)
class ObjectChildOrderLockedEvent(ObjectEvent):
    pass


@interface.implementer(IObjectChildOrderUnlockedEvent)
class ObjectChildOrderUnlockedEvent(ObjectEvent):
    pass


class IPublishable(interface.Interface):

    publishLastModified = Number(title=u"The timestamp at which this object updated its publication state.",
                                 default=0.0,
                                 required=False)

    def publish(event=True):
        """
        Cause this object to provide :class:`IDefaultPublished`

        :param event: Notify unlock event
        """

    def unpublish(event=True):
        """
        Cause this object to no longer provide :class:`IDefaultPublished`

        :param event: Notify unlock event
        """

    def is_published(*args, **kwargs):
        """
        Return if this object is published
        """
    isPublished = is_published


class ICalendarPublishableMixin(interface.Interface):

    publishBeginning = ValidDatetime(
        title="This object is not available before this time",
        description="""When present, this specifies the time instant at which
                       this obj is to be available.""",
        required=False)

    publishEnding = ValidDatetime(
        title="This object is not available after this time",
        description="""When present, this specifies the last instance at which
                       this obj is to be available.""",
        required=False)


class ICalendarPublishable(IPublishable, ICalendarPublishableMixin):
    pass


class ICalendarPublishableModifiedEvent(IObjectModifiedEvent, ICalendarPublishableMixin):
    """
    An event that is sent, when an calendar publishable object is modified
    """


@interface.implementer(ICalendarPublishableModifiedEvent)
class CalendarPublishableModifiedEvent(ObjectModifiedEvent):

    def __init__(self, obj, publishBeginning=None, publishEnding=None, *descriptions):
        super(CalendarPublishableModifiedEvent, self).__init__(
            obj, *descriptions)
        self.publishEnding = publishEnding
        self.publishBeginning = publishBeginning


class INoPublishLink(interface.Interface):
    """
    Marker interface for objects that are publishable but no links to
    publish operations should be provided
    """
INoPublishLink.setTaggedValue('_ext_is_marker_interface', True)


class IPublishablePredicate(interface.Interface):
    """
    Subscriber for publishable objects to determiend if an object
    is published
    """

    def is_published(publishable, principal=None, context=None, *args, **kwargs):
        """
        return if the specified publishable is published for the given 
        principal and context
        """
    isPublished = is_published


class ICalendarPublishablePredicate(interface.Interface):
    """
    Subscriber for calendar-publishable objects to determiend if an object
    is published
    """

    def is_published(publishable, principal=None, context=None, *args, **kwargs):
        """
        return if the specified calendar publishable is published for the given 
        principal and context
        """
    isPublished = is_published


def get_publishable_predicate(publishable, interface=None):
    interface = IPublishablePredicate if interface is None else interface
    predicates = list(component.subscribers((publishable,), interface))

    def uber_filter(publishable, *args, **kwargs):
        return all((p.is_published(publishable, *args, **kwargs) for p in predicates))
    return uber_filter


def get_calendar_publishable_predicate(publishable, interface=None):
    interface = ICalendarPublishablePredicate if interface is None else interface
    predicates = list(component.subscribers((publishable,), interface))

    def uber_filter(publishable, *args, **kwargs):
        return all((p.is_published(publishable, *args, **kwargs) for p in predicates))
    return uber_filter

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
        title="The ID (name) of the container to which this object belongs. "
        "Should match the __parent__.__name__",
        required=False)

    id = DecodingValidTextLine(
        title="The locally unique ID (name) of this object in the container "
        "it belongs. Should match the __name__",
        required=False)


class INamedContainer(IContainer):
    """
    A container with a name.
    """
    container_name = interface.Attribute(
        "The human-readable nome of this container.")


class IHomogeneousTypeContainer(IContainer):
    """
    Things that only want to contain items of a certain type.
    In some cases, an object of this type would be specified
    in an interface as a :class:`zope.schema.List` with a single
    `value_type`.
    """

    contained_type = interface.Attribute(
        """
        The type of objects in the container. May be an Interface type
        or a class type. There should be a ZCA factory to create instances
        of this type associated as tagged data on the type at :data:IHTC_NEW_FACTORY
        """)

IHTC_NEW_FACTORY = 'nti.dataserver.interfaces.IHTCNewFactory'  # BWC


class IContainerIterable(interface.Interface):
    """
    Something that can enumerate the containers (collections)
    it contains.
    """

    # FIXME: This is ill-defined. One would expect it to be all containers,
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
    body = Iterable(title="Content elements")


class ITitledContent(ITitled):
    """
    A piece of content with a title, either human created or potentially
    automatically generated. (This differs from, say, a person's honorrific title.
    """
    title = Title()


class ITaggedContent(interface.Interface):
    """
    Something that can contain tags.
    """

    tags = TupleFromObject(title="Applied Tags",
                           value_type=Tag(min_length=1, title="A single tag",
                                                              description=Tag.__doc__, __name__='tags'),
                           unique=True,
                           default=())

# content types


class IIdentity(interface.Interface):
    """
    Base interface for Identity base objects
    """

zope.deferredimport.deprecated(
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
        title="A set of entities this object is directly shared with (non-recursive, non-flattened)",
        value_type=Object(IIdentity, title="An entity shared with"),
        required=False,
        default=(),
        readonly=True)

    flattenedSharingTargets = UniqueIterable(
        title="A set of entities this object is directly or indirectly shared with (recursive, flattened)",
        value_type=Object(IIdentity, title="An entity shared with"),
        required=False,
        default=(),
        readonly=True)

    flattenedSharingTargetNames = UniqueIterable(
        title="The ids of all the entities (e.g. communities, etc) this obj is shared with.",
        description=" This is a convenience property for reporting the ids of all "
        " entities this object is shared with, directly or indirectly. Note that the ids reported "
                    " here are not necessarily globally unique and may not be resolvable as such.",
        value_type=DecodingValidTextLine(title="The entity identifier"),
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
        title="The ids of the entities we are shared directly with, taking externalization of local ids into account",
        value_type=DecodingValidTextLine(title="The username or NTIID"),
        required=False,
        default=frozenset())


class IUserGeneratedData(ICreated):
    """
    marker interface for user generated data
    """


class IModeledContentFile(IFile,
                          INamed,
                          ILastModified,
                          IShareableModeledContent):
    name = ValidTextLine(title="Identifier for the file",
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

ME_USER_ID = 'me'
EVERYONE_GROUP_NAME = 'system.Everyone'
AUTHENTICATED_GROUP_NAME = 'system.Authenticated'
UNAUTHENTICATED_PRINCIPAL_NAME = 'system.Unknown'

RESERVED_USER_IDS = (SYSTEM_USER_ID, SYSTEM_USER_NAME, EVERYONE_GROUP_NAME,
                     AUTHENTICATED_GROUP_NAME, ME_USER_ID)

LOWER_RESERVED_USER_IDS = tuple((x.lower() for x in RESERVED_USER_IDS))


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
    creator_username = DecodingValidTextLine(
        title=u'The username',
        constraint=valid_entity_username,
        readonly=True
    )


class IEntity(IIdentity, IZContained, IAnnotatable, IShouldHaveTraversablePath,
              INeverStoredInSharedStream):

    username = DecodingValidTextLine(title=u'The username',
                                     constraint=valid_entity_username)


class IMissingEntity(IEntity):
    """
    A proxy object for a missing, unresolved or unresolvable
    entity.
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


class ICommunity(IDynamicSharingTarget):

    public = Bool(title=u'Public flag', required=False, default=True)

    joinable = Bool(title=u'Joinable flag', required=False, default=True)

    username = DecodingValidTextLine(
        title=u'The username',
        constraint=valid_entity_username
    )

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


class IUser(IEntity, IContainerIterable):
    """
    A user of the system. Notice this is not an IPrincipal.
    This interface needs finished and fleshed out.
    """

    username = DecodingValidTextLine(title=u'The username', min_length=5)

    # Note: z3c.password provides a PasswordField we could use here
    # when we're sure what it does and that validation works out
    password = interface.Attribute("The password")


class IUsernameSubstitutionPolicy(interface.Interface):
    """
    Marker interface to register an utility that replaces
    the username value for another
    """

    def replace(username):
        pass


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

        :param friend:     May be another friends list, an entity, a
                                        string naming a user, or even a dictionary containing
                                        a 'Username' property.
        """


class IUseNTIIDAsExternalUsername(interface.Interface):
    """
    A marker interface for IEntity objects that are not globally resolvable
    by their 'username'; instead, everywhere we would write out
    a username we must instead write the NTIID.
    """


class IDynamicSharingTargetFriendsList(IDynamicSharingTarget,
                                       IFriendsList,
                                       IUseNTIIDAsExternalUsername):
    """
    A type of :class:`IDynamicSharingTarget` that is a list of members.
    """

    About = ValidTextLine(
        title='About',
        description="A short description of a grouo",
        max_length=500,
        required=False,
        constraint=checkCannotBeBlank)

    Locked = Bool(
        title='Locked flag. No group code, no removal', required=False, default=False)

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
    context_id = ValidTextLine(title="The ntiid of the context.", default='')


class IContextAnnotatable(IAttributeAnnotatable):
    """
    Marker interface that the given object may have a root
    'context' object, represented by ``IContainerContext``.
    """

# deleted objects


class IDeletedObjectPlaceholder(interface.Interface):
    """
    Marker interface to be applied to things that have actually
    been deleted, but, for whatever reason, some trace object
    has to be left behind. These will typically be rendered specially.
    """

# aux interfaces


class IExternalService(interface.Interface):
    """
    Base interface for external services
    """


class IEnvironmentSettings(interface.Interface):
    pass


class IDataserver(interface.Interface):
    pass
