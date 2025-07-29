# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from plone.supermodel import model
from zope import schema
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant
from zope.interface.interfaces import IInterface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from imio.schedule import _


class IImioScheduleLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IScheduledContentTypeVocabulary(Interface):
    """
    Adapts a ScheduleConfig instance into a vocabulary.
    """


class ITaskLogic(Interface):
    """
    Base interface for the following TaskConfig logic items:
        - conditions,
        - date computation
        - user assignment
    """


class IDefaultEndingStates(Interface):
    """
    Adapts a TaskContainer into a list of default ending states.
    """


class IDefaultFreezeStates(Interface):
    """
    Adapts a TaskContainer into a list of default freeze states.
    """


class IDefaultThawStates(Interface):
    """
    Adapts a TaskContainer into a list of default freeze states.
    """


class IDefaultTaskGroup(ITaskLogic):
    """
    Adapts a TaskContainer into a plone group to assign to a task.
    """


class IDefaultTaskUser(ITaskLogic):
    """
    Adapts a TaskContainer into a plone user to assign to a task.
    """


class ICondition(ITaskLogic):
    """
    Condition object adapting a TaskContainer and task.
    """

    def evaluate(self):
        """
        evaluate if the condition is True or False
        """


class ICreationCondition(ICondition):
    """
    Creation condition of task.
    """


class IStartCondition(ICondition):
    """
    Start condition of task.
    """


class IEndCondition(ICondition):
    """
    End condition of task.
    """


class IFreezeCondition(ICondition):
    """
    Freeze condition of task.
    """


class IThawCondition(ICondition):
    """
    Thaw condition of task.
    """


class IStartDate(ITaskLogic):
    """
    Adapts a TaskContainer into the start date used to compute
    the task due date.
    """


class IMacroTaskCreationCondition(ICreationCondition):
    """
    Creation condition of macro task.
    """


class IMacroTaskStartCondition(IStartCondition):
    """
    Start condition of macro task.
    """


class IMacroTaskEndCondition(IEndCondition):
    """
    End condition of macro task.
    """


class IMacroTaskFreezeCondition(IFreezeCondition):
    """
    Freeze condition of macro task.
    """


class IMacroTaskThawCondition(IThawCondition):
    """
    Thaw condition of macro task.
    """


class IMacroTaskStartDate(IStartDate):
    """
    Adapts a TaskContainer into the start date used to compute
    the macro task due date.
    """


class IToTaskConfig(Interface):
    """
    Interface for adapters returning the task config of
    a context providing ITaskContainer.
    """


class IScheduleView(Interface):
    """
    Marker interface to provides on folderish with the schedule faceted view.
    """


class IScheduleCollection(Interface):
    """
    Marker interface for collections associated to schedule/task config.
    """


class ITaskMarkerInterface(IInterface):
    """
    Marker interface for for AutomatedTask custom marker interfaces vocabulary.
    """


class ScheduleConfigNotFound(Exception):
    """
    Raised when a ScheduleConfig is not found.
    """


class TaskConfigNotFound(Exception):
    """
    Raised when a TaskConfig is not found.
    """


class TaskAlreadyExists(Exception):
    """
    Raised when a Task already exists.
    """


class IRecurrenceCondition(ITaskLogic):
    """
    Base interface for the TaskConfig recurrence conditions
    """


class ICalculationDelay(ITaskLogic):
    """
    Base interface for the TaskConfig calculation delay methods
    """


class IFreezeDuration(Interface):
    """
    Base interface for freeze duration adapters.
    """


class IToIcon(Interface):
    """
    Adapts an object into an icon.
    """

    def get_icon_url(self):
        """
        Return the icon url.
        """


class ISettings(model.Schema):

    working_days = schema.List(
        title=_(u"List of working days"),
        value_type=schema.Choice(
            title=_(u"Day"),
            vocabulary="imio.schedule.working_days",
        ),
        required=True,
    )


class IDueDateSettings(Interface):
    """ """

    color_orange_x_days_before_due_date = schema.Int(
        title=_("Color due date in orange if it comes close to X days"),
        description=_("Leave empty to disable"),
        required=False,
        default=10,
        min=0,
    )

    color_red_x_days_before_due_date = schema.Int(
        title=_("Color due date in red if it comes close to X days"),
        description=_("Overrides orange color, leave empty to disable"),
        required=False,
        default=5,
        min=0,
    )

    @invariant
    def orange_is_before_red_invariant(data):
        if (
            data.color_orange_x_days_before_due_date is None
            or data.color_red_x_days_before_due_date is None
        ):
            return
        if (
            data.color_orange_x_days_before_due_date
            < data.color_red_x_days_before_due_date
        ):
            raise Invalid(
                _(
                    u"The orange value should be higher than the red one, as it is used as a first warning."
                )
            )


class ICalendarExtraHolidays(Interface):
    """Interface for extra holidays utility"""

    def get_holidays(self, year):
        """
        Return a tuple with the holidays for the given year
        format: ((<date object>, 'holiday_name'), ...)
        """
