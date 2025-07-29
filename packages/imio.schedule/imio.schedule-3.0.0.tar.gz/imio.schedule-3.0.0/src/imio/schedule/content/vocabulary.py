# -*- coding: utf-8 -*-

from imio.schedule import _
from imio.schedule.interfaces import ICalculationDelay
from imio.schedule.interfaces import ICreationCondition
from imio.schedule.interfaces import IDefaultTaskGroup
from imio.schedule.interfaces import IDefaultTaskUser
from imio.schedule.interfaces import IEndCondition
from imio.schedule.interfaces import IFreezeCondition
from imio.schedule.interfaces import IMacroTaskCreationCondition
from imio.schedule.interfaces import IMacroTaskEndCondition
from imio.schedule.interfaces import IMacroTaskStartCondition
from imio.schedule.interfaces import IMacroTaskStartDate
from imio.schedule.interfaces import IRecurrenceCondition
from imio.schedule.interfaces import IScheduledContentTypeVocabulary
from imio.schedule.interfaces import IStartCondition
from imio.schedule.interfaces import IStartDate
from imio.schedule.interfaces import ITaskLogic
from imio.schedule.interfaces import ITaskMarkerInterface
from imio.schedule.interfaces import IThawCondition
from imio.schedule.utils import interface_to_tuple
from imio.schedule.utils import dict_list_2_vocabulary

from plone import api

from plone.principalsource.source import PrincipalSource

from Products.CMFPlone import PloneMessageFactory
from Products.CMFPlone.i18nl10n import utranslate

from zope.component import getAdapter
from zope.component import getGlobalSiteManager
from zope.i18n import translate
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


def unify_vocabularies(vocabularies):
    """Remove duplicates from a vocabulary list"""
    dict = {}
    unified = []
    for vocabularie in vocabularies:
        if vocabularie.value in dict:
            dict[vocabularie.value] += 1
        else:
            dict[vocabularie.value] = 1
            unified.append(vocabularie)
    return unified


class BaseVocabularyFactory(object):
    """
    Base class for vocabulary factories.
    """

    def get_portal_type(self, context):
        """
        Return the portal_type of the (future?) context.
        """
        request = context.REQUEST
        try:
            add_view = request.get("PUBLISHED", request["PARENTS"][-1])
            if hasattr(add_view, "form_instance"):
                form = add_view.form_instance
                portal_type = form.portal_type
            else:
                form = add_view.context.form_instance
                portal_type = form.portal_type
        except:
            portal_type = context.portal_type

        return portal_type

    def get_fti(self, context):
        """
        Return the fti of the (future?) context.
        """
        portal_type = self.get_portal_type(context)
        portal_types = api.portal.get_tool("portal_types")
        fti = portal_types.getTypeInfo(portal_type)
        return fti


class ScheduledContentTypeVocabularyFactory(BaseVocabularyFactory):
    """
    Vocabulary factory for 'scheduled_contenttype' field.
    Return all the content types that can be associated
    to a task config (=> should implements IScheduledContentType).
    """

    def __call__(self, context):
        """
        Call the adapter vocabulary for the 'scheduled_contenttype' field
        and returns it.
        """
        portal_type = self.get_portal_type(context)
        fti = self.get_fti(context)
        voc_adapter = getAdapter(fti, IScheduledContentTypeVocabulary, portal_type)
        vocabulary = voc_adapter()

        return vocabulary


class ScheduledContentTypeVocabulary(object):
    """
    Adapts a TaskConfig fti to return a specific
    vocabulary for the 'scheduled_contenttype' field.

    Subclass and override allowed_types() and get_message_factory()
    in products using imio.schedule.
    """

    implements(IScheduledContentTypeVocabulary)

    def __init__(self, fti):
        """ """

    def __call__(self):
        """
        Return a vocabulary from an explicit set content types.
        """

        voc_terms = []
        content_types = self.content_types()
        message_factory = self.get_message_factory()

        for portal_type, interface in content_types.iteritems():
            key = self.to_vocabulary_key(portal_type, interface)
            voc_terms.append(SimpleTerm(key, key, message_factory(portal_type)))

        vocabulary = SimpleVocabulary(voc_terms)

        return vocabulary

    def content_types(self):
        """
        To override.
        Explicitely define here the content types allowed in the field
        'scheduled_contenttype'

        eg:
        from Products.ATContentTypes.interfaces import IATFolder
        return{'Folder': IATFolder}
        """
        return {}

    def get_message_factory(self):
        """
        To override.
        By default return plone MessageFactory.
        """
        return PloneMessageFactory

    def to_vocabulary_key(self, portal_type, interfaces):
        """
        Return the module path of a class.
        """
        if type(interfaces) not in [list, tuple]:
            interfaces = (interfaces,)
        return (portal_type, tuple([interface_to_tuple(i) for i in interfaces]))


class AssignedGroupVocabularyFactory(object):
    """
    Vocabulary factory for 'default_assigned_group' field.
    """

    def __call__(self, context):
        """
        Call the adapter vocabulary for the 'default_assigned_group' field
        Return available groups for a task config.
        """
        gsm = getGlobalSiteManager()
        scheduled_interfaces = context.get_scheduled_interfaces()

        voc_terms = []
        for scheduled_interface in scheduled_interfaces:
            for adapter in gsm.registeredAdapters():
                implements_IGroup = adapter.provided is IDefaultTaskGroup
                specific_enough = adapter.required[0].implementedBy(
                    scheduled_interface
                ) or issubclass(scheduled_interface, adapter.required[0])
                if implements_IGroup and specific_enough:
                    voc_terms.append(
                        SimpleTerm(adapter.name, adapter.name, _(adapter.name))
                    )

        # enrich the vocabulary with available groups
        for group in api.group.get_groups():
            voc_terms.append(
                SimpleTerm(group.id, group.id, group.getGroupTitleOrName())
            )

        vocabulary = SimpleVocabulary(unify_vocabularies(voc_terms))
        return vocabulary


class AssignedUserVocabularyFactory(object):
    """
    Vocabulary factory for 'default_assigned_user' field.
    """

    def __call__(self, context):
        """
        Call the adapter vocabulary for the 'default_assigned_user' field
        Return available users for a task config.
        """
        gsm = getGlobalSiteManager()
        scheduled_interfaces = context.get_scheduled_interfaces()

        voc_terms = []
        for scheduled_interface in scheduled_interfaces:
            for adapter in gsm.registeredAdapters():
                implements_IUser = adapter.provided is IDefaultTaskUser
                specific_enough = adapter.required[0].implementedBy(
                    scheduled_interface
                ) or issubclass(scheduled_interface, adapter.required[0])
                if implements_IUser and specific_enough:
                    voc_terms.append(
                        SimpleTerm(adapter.name, adapter.name, _(adapter.name))
                    )

        # enrich the vocabulary with available users
        for user in api.user.get_users():
            voc_terms.append(
                SimpleTerm(
                    user.id, user.id, user.getProperty("fullname") or user.getUserName()
                )
            )

        vocabulary = SimpleVocabulary(
            sorted(
                unify_vocabularies(voc_terms),
                key=lambda term: term.title.decode("utf-8"),
            )
        )
        return vocabulary


class ContainerStateVocabularyFactory(object):
    """
    Vocabulary factory for 'container_state' field.
    """

    def __call__(self, context):
        """
        Call the adapter vocabulary for the 'container_state' field
        and returns it.
        """
        portal_type = context.get_scheduled_portal_type()
        if not portal_type:
            return SimpleVocabulary([])

        wf_tool = api.portal.get_tool("portal_workflow")
        request = api.portal.get().REQUEST

        workfow = wf_tool.get(wf_tool.getChainForPortalType(portal_type)[0])
        voc_terms = [
            SimpleTerm(
                state_id, state_id, translate(state.title, "plone", context=request)
            )
            for state_id, state in workfow.states.items()
        ]

        vocabulary = SimpleVocabulary(voc_terms)

        return vocabulary


class TaskMarkerInterfacesVocabulary(object):
    """
    Return available custom Task Marker Interface.
    """

    def __call__(self, context):
        gsm = getGlobalSiteManager()
        interfaces = gsm.getUtilitiesFor(ITaskMarkerInterface)
        items = []

        for interface_name, marker_interface in interfaces:
            items.append(
                SimpleTerm(
                    interface_name,
                    marker_interface.__doc__,
                    utranslate(
                        msgid=marker_interface.__doc__,
                        domain="imio.schedule",
                        context=context,
                        default=marker_interface.__doc__,
                    ),
                )
            )

        # sort elements by title
        items.sort(lambda a, b: cmp(a.title, b.title))

        return SimpleVocabulary(items)


class BooleanVocabulary(object):
    """
    Return True/False vocabulary.
    """

    def __call__(self, context):
        request = api.portal.get().REQUEST
        items = [
            SimpleTerm(
                "True",
                "True",
                translate("Doable alone", "imio.schedule", context=request),
            ),
            SimpleTerm(
                "False",
                "False",
                translate("Subtasks dependencies", "imio.schedule", context=request),
            ),
        ]

        return SimpleVocabulary(items)


class TaskLogicVocabularyFactory(object):
    """
    Base class for vocabulary factories listing adapters providing
    some ITaskLogic (sub)interface and adapting a task container
    content type.
    """

    provides_interface = None  # to override in subclass

    def __call__(self, context):
        """
        Look for all the conditions registered for scheduled_contenttype,
        implementing some ITaskLogic (sub)interface and return them as
        a vocabulary.
        """
        gsm = getGlobalSiteManager()
        scheduled_interfaces = context.get_scheduled_interfaces()

        terms = []
        for scheduled_interface in scheduled_interfaces:
            for adapter in gsm.registeredAdapters():
                implements_interface = issubclass(
                    adapter.provided, ITaskLogic
                ) and issubclass(self.provides_interface, adapter.provided)
                specific_enough = adapter.required[0].implementedBy(
                    scheduled_interface
                ) or issubclass(scheduled_interface, adapter.required[0])
                if implements_interface and specific_enough:
                    terms.append(
                        SimpleTerm(adapter.name, adapter.name, _(adapter.name))
                    )

        vocabulary = SimpleVocabulary(unify_vocabularies(terms))
        return vocabulary


class CreationConditionVocabularyFactory(TaskLogicVocabularyFactory):
    """
    Vocabulary factory for 'creation_conditions' field.
    Return available creation conditions of a task config.
    """

    provides_interface = ICreationCondition


class StartConditionVocabularyFactory(TaskLogicVocabularyFactory):
    """
    Vocabulary factory for 'start_conditions' field.
    Return available start conditions of a task config.
    """

    provides_interface = IStartCondition


class EndConditionVocabularyFactory(TaskLogicVocabularyFactory):
    """
    Vocabulary factory for 'end_conditions' field.
    Return available end conditions of a task config.
    """

    provides_interface = IEndCondition


class FreezeConditionVocabularyFactory(TaskLogicVocabularyFactory):
    """
    Vocabulary factory for 'end_conditions' field.
    Return available end conditions of a task config.
    """

    provides_interface = IFreezeCondition


class ThawConditionVocabularyFactory(TaskLogicVocabularyFactory):
    """
    Vocabulary factory for 'end_conditions' field.
    Return available end conditions of a task config.
    """

    provides_interface = IThawCondition


class StartDateVocabularyFactory(TaskLogicVocabularyFactory):
    """
    Vocabulary factory for 'start_date' field.
    Return start date of a task config.
    """

    provides_interface = IStartDate


class RecurrenceConditionVocabularyFactory(TaskLogicVocabularyFactory):
    """
    Vocabulary factory for 'recurrence_conditions' field.
    Return recurrence conditions for a task config.
    """

    provides_interface = IRecurrenceCondition


class CalculationDelayVocabularyFactory(TaskLogicVocabularyFactory):
    """
    Vocabulary factory for 'calculation_delay' field.
    Return calculation delay methods for a task config.
    """

    provides_interface = ICalculationDelay


class MacroTaskCreationConditionVocabularyFactory(TaskLogicVocabularyFactory):
    """
    Vocabulary factory for 'creation_conditions' field.
    Return available creation conditions of a macro task config.
    """

    provides_interface = IMacroTaskCreationCondition


class MacroTaskStartConditionVocabularyFactory(TaskLogicVocabularyFactory):
    """
    Vocabulary factory for 'start_conditions' field.
    Return available start conditions of a macro task config.
    """

    provides_interface = IMacroTaskStartCondition


class MacroTaskEndConditionVocabularyFactory(TaskLogicVocabularyFactory):
    """
    Vocabulary factory for 'end_conditions' field.
    Return available end conditions of a macro task config.
    """

    provides_interface = IMacroTaskEndCondition


class MacroTaskStartDateVocabularyFactory(TaskLogicVocabularyFactory):
    """
    Vocabulary factory for 'start_date' field.
    Return start date of a macro task config.
    """

    provides_interface = IMacroTaskStartDate


class LogicalOperatorVocabularyFactory(BaseVocabularyFactory):
    def __call__(self, context):
        return dict_list_2_vocabulary(
            [
                {"AND": _(u"and")},
                {"OR": _(u"or")},
            ]
        )


class WeekDaysRoundingVocabulary(object):
    """ """

    def __call__(self, context):
        raw_terms = [
            ("0", "0", _("None")),
            ("1", "1", _("Next Monday")),
            ("2", "2", _("Next Tuesday")),
            ("3", "3", _("Next Wednesday")),
            ("4", "4", _("Next Thursday")),
            ("5", "5", _("Next Friday")),
            ("6", "6", _("Next Saturday")),
            ("7", "7", _("Next Sunday")),
            ("-1", "-1", _("Previous Monday")),
            ("-2", "-2", _("Previous Tuesday")),
            ("-3", "-3", _("Previous Wednesday")),
            ("-4", "-4", _("Previous Thursday")),
            ("-5", "-5", _("Previous Friday")),
            ("-6", "-6", _("Previous Saturday")),
            ("-7", "-7", _("Previous Sunday")),
        ]
        voc_terms = [SimpleTerm(*term) for term in raw_terms]
        vocabulary = SimpleVocabulary(voc_terms)

        return vocabulary


class TaskOwnerSource(PrincipalSource):
    def __init__(self, context):
        super(TaskOwnerSource, self).__init__(context)

    def _search(self, id=None, exact_match=True):
        users = api.user.get_users(self.context.assigned_group)
        if id is not None:
            return sorted(
                [{"id": u.id} for u in users if u.id == id], key=lambda u_id: u_id["id"]
            )
        return sorted([{"id": u.id} for u in users], key=lambda u_id: u_id["id"])


class TaskOwnerSourceBinder(object):
    """Bind the principal source with either users or groups"""

    implements(IContextSourceBinder)

    def __call__(self, context):
        return TaskOwnerSource(context)


TaskOwnerVocabulary = TaskOwnerSourceBinder()
