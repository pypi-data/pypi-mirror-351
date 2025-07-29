# -*- coding: utf-8 -*-

from Products.CMFCore.Expression import Expression
from Products.PageTemplates.Expressions import getEngine
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from imio.schedule import _
from imio.schedule.config import CREATION
from imio.schedule.config import DONE
from imio.schedule.config import FROZEN
from imio.schedule.config import STARTED
from imio.schedule.config import states_by_status
from imio.schedule.content.subform_context_choice import SubFormContextChoice
from imio.schedule.content.task import IAutomatedTask
from imio.schedule.interfaces import ICalculationDelay
from imio.schedule.interfaces import ICreationCondition
from imio.schedule.interfaces import IDefaultEndingStates
from imio.schedule.interfaces import IDefaultFreezeStates
from imio.schedule.interfaces import IDefaultTaskGroup
from imio.schedule.interfaces import IDefaultTaskUser
from imio.schedule.interfaces import IDefaultThawStates
from imio.schedule.interfaces import IEndCondition
from imio.schedule.interfaces import IFreezeCondition
from imio.schedule.interfaces import IFreezeDuration
from imio.schedule.interfaces import IStartCondition
from imio.schedule.interfaces import IThawCondition
from imio.schedule.interfaces import TaskAlreadyExists
from imio.schedule.utils import WorkingDaysCalendar
from imio.schedule.utils import round_to_weekday
from plone import api
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter
from zope.component import queryAdapter
from zope.component import queryMultiAdapter
from zope.component.interface import getInterface
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import invariant

import logging
import os
import copy


logger = logging.getLogger("imio.schedule")


class ICreationConditionSchema(Interface):

    condition = SubFormContextChoice(
        title=_(u"Condition"),
        vocabulary="schedule.creation_conditions",
        required=True,
    )

    operator = schema.Choice(
        title=_(u"Operator"),
        vocabulary="schedule.logical_operator",
        default="AND",
    )

    display_status = schema.Bool(
        title=_(u"display_status"),
        default=True,
    )


class IStartConditionSchema(Interface):

    condition = SubFormContextChoice(
        title=_(u"Condition"),
        vocabulary="schedule.start_conditions",
        required=True,
    )

    operator = schema.Choice(
        title=_(u"Operator"),
        vocabulary="schedule.logical_operator",
        default="AND",
    )

    display_status = schema.Bool(
        title=_(u"display_status"),
        default=True,
    )


class IEndConditionSchema(Interface):

    condition = SubFormContextChoice(
        title=_(u"Condition"),
        vocabulary="schedule.end_conditions",
        required=True,
    )

    operator = schema.Choice(
        title=_(u"Operator"),
        vocabulary="schedule.logical_operator",
        default="AND",
    )

    display_status = schema.Bool(
        title=_(u"display_status"),
        default=True,
    )


class IRecurrenceConditionSchema(Interface):

    condition = SubFormContextChoice(
        title=_(u"Condition"),
        vocabulary="schedule.creation_conditions",
        required=True,
    )

    operator = schema.Choice(
        title=_(u"Operator"),
        vocabulary="schedule.logical_operator",
        default="AND",
    )

    display_status = schema.Bool(
        title=_(u"display_status"),
        default=True,
    )


class IFreezeConditionSchema(Interface):

    condition = SubFormContextChoice(
        title=_(u"Condition"),
        vocabulary="schedule.freeze_conditions",
        required=True,
    )

    operator = schema.Choice(
        title=_(u"Operator"),
        vocabulary="schedule.logical_operator",
        default="AND",
    )

    display_status = schema.Bool(
        title=_(u"display_status"),
        default=True,
    )


class IThawConditionSchema(Interface):

    condition = SubFormContextChoice(
        title=_(u"Condition"),
        vocabulary="schedule.thaw_conditions",
        required=True,
    )

    operator = schema.Choice(
        title=_(u"Operator"),
        vocabulary="schedule.logical_operator",
        default="AND",
    )

    display_status = schema.Bool(
        title=_(u"display_status"),
        default=True,
    )


class ITaskConfig(model.Schema):
    """
    TaskConfig dexterity schema.
    """

    model.fieldset(
        "general",
        label=_(u"General informations"),
        fields=[
            "enabled",
            "default_assigned_group",
            "default_assigned_user",
            "marker_interfaces",
        ],
    )

    enabled = schema.Bool(
        title=_(u"Enabled"),
        default=True,
        required=False,
    )

    default_assigned_group = schema.Choice(
        title=_(u"Assigned group"),
        description=_(u"Select default group assigned to this task."),
        vocabulary="schedule.assigned_group",
        required=False,
    )

    default_assigned_user = schema.Choice(
        title=_(u"Assigned user"),
        description=_(u"Select default user assigned to this task."),
        vocabulary="schedule.assigned_user",
        required=True,
    )

    marker_interfaces = schema.Set(
        title=_(u"Marker interfaces"),
        description=_(u"Custom marker interfaces for this task."),
        value_type=schema.Choice(source="schedule.task_marker_interfaces"),
        required=False,
    )

    model.fieldset(
        "creation",
        label=_(u"Creation"),
        fields=["creation_state", "creation_conditions"],
    )

    creation_state = schema.Set(
        title=_(u"Task container creation state"),
        description=_(
            u"Select the state of the container where the task is automatically created."
        ),
        value_type=schema.Choice(source="schedule.container_state"),
        required=False,
    )

    creation_conditions = schema.List(
        title=_(u"Creation conditions"),
        description=_(u"Select creation conditions of the task"),
        value_type=schema.Object(
            title=_(u"Conditions"),
            schema=ICreationConditionSchema,
        ),
        required=False,
    )

    model.fieldset(
        "start", label=_(u"Start"), fields=["starting_states", "start_conditions"]
    )

    starting_states = schema.Set(
        title=_(u"Task container start states"),
        description=_(
            u"Select the state of the container where the task is automatically started."
        ),
        value_type=schema.Choice(source="schedule.container_state"),
        required=False,
    )

    start_conditions = schema.List(
        title=_(u"Start conditions"),
        description=_(u"Select start conditions of the task"),
        value_type=schema.Object(
            title=_(u"Conditions"),
            schema=IStartConditionSchema,
        ),
        required=False,
    )

    model.fieldset(
        "ending", label=_(u"Ending"), fields=["ending_states", "end_conditions"]
    )

    ending_states = schema.Set(
        title=_(u"Task container end states"),
        description=_(
            u"Select the states of the container where the task is automatically closed."
        ),
        value_type=schema.Choice(source="schedule.container_state"),
        required=False,
    )

    end_conditions = schema.List(
        title=_(u"End conditions"),
        description=_(u"Select end conditions of the task."),
        value_type=schema.Object(
            title=_(u"Conditions"),
            schema=IEndConditionSchema,
        ),
        required=False,
    )

    model.fieldset(
        "delay",
        label=_(u"Calculation delay"),
        fields=[
            "start_date",
            "warning_delay",
            "calculation_delay",
            "additional_delay",
            "additional_delay_tal",
            "additional_delay_type",
            "round_to_day",
        ],
    )

    start_date = schema.Choice(
        title=_(u"Start date"),
        description=_(u"Select the start date used to compute the due date."),
        vocabulary="schedule.start_date",
        required=True,
    )

    warning_delay = schema.Int(
        title=_(u"Warning delay"),
        required=False,
    )

    calculation_delay = schema.List(
        title=_(u"Calculation delay method"),
        value_type=schema.Choice(
            title=_(u"Calculation delay"),
            vocabulary="schedule.calculation_delay",
            default="schedule.calculation_default_delay",
        ),
        required=True,
    )

    additional_delay = schema.TextLine(
        title=_(u"Additional delay"),
        description=_(u"This delay is added to the due date of the task."),
        required=False,
        default=u"0",
    )

    additional_delay_tal = schema.Bool(
        title=_(u"Additional delay is a tal expression?"),
        description=_(
            u"Define if the additional delay should be interpreted as a tal expression"
        ),
        required=False,
        default=False,
    )

    @invariant
    def validate_additional_delay(task_config):
        if task_config.additional_delay_tal is False:
            try:
                int(task_config.additional_delay)
            except ValueError:
                raise Invalid(_("The additional delay is not a valid integer"))

    additional_delay_type = schema.Choice(
        title=_(u"Additional delay type"),
        description=_(u"Define the calculation method for the additional delay"),
        vocabulary="imio.schedule.additional_delay_type",
        required=True,
    )

    round_to_day = schema.Choice(
        title=_(u"Round to week day"),
        vocabulary="schedule.vocabulary.week_days_rounding",
        default="0",
        required=True,
    )

    model.fieldset(
        "freeze",
        label=_(u"Freeze"),
        fields=[
            "freeze_states",
            "freeze_conditions",
        ],
    )

    freeze_states = schema.Set(
        title=_(u"Task container freeze states"),
        description=_(
            u"Select the states of the container where the task is automatically closed."
        ),
        value_type=schema.Choice(source="schedule.container_state"),
        required=False,
    )

    freeze_conditions = schema.List(
        title=_(u"Freeze conditions"),
        description=_(u"Select freeze conditions of the task."),
        value_type=schema.Object(
            title=_(u"Conditions"),
            schema=IFreezeConditionSchema,
        ),
        required=False,
    )

    model.fieldset(
        "thaw",
        label=_(u"Thaw"),
        fields=[
            "thaw_states",
            "thaw_conditions",
        ],
    )

    thaw_states = schema.Set(
        title=_(u"Task container thaw states"),
        description=_(
            u"Select the states of the container where the task is automatically closed."
        ),
        value_type=schema.Choice(source="schedule.container_state"),
        required=False,
    )

    thaw_conditions = schema.List(
        title=_(u"Thaw conditions"),
        description=_(u"Select thaw conditions of the task."),
        value_type=schema.Object(
            title=_(u"Conditions"),
            schema=IThawConditionSchema,
        ),
        required=False,
    )

    model.fieldset(
        "recurrence",
        label=_(u"Recurrence"),
        fields=[
            "activate_recurrency",
            "recurrence_states",
            "recurrence_conditions",
        ],
    )

    activate_recurrency = schema.Bool(
        title=_(u"Activate recurrency"),
        required=False,
        default=False,
    )

    recurrence_states = schema.Set(
        title=_(u"Task container recurrence states"),
        description=_(
            u"Select the state of the container where the task should be recurred"
        ),
        value_type=schema.Choice(source="schedule.container_state"),
        required=False,
    )

    recurrence_conditions = schema.List(
        title=_(u"Recurrence condition"),
        description=_(u"Select recurrence conditions of the task."),
        value_type=schema.Object(
            title=_("Conditions"),
            schema=IRecurrenceConditionSchema,
        ),
        required=False,
    )


class BaseTaskConfig(object):
    """
    TaskConfig dexterity class.
    """

    @property
    def _debug_mode(self):
        debug_mode = os.environ.get("SCHEDULE_DEBUG", "0")
        return debug_mode.lower() in ("on", "1", "true")

    def get_task_type(self):
        """
        To override.
        Return the content type of task to create.
        """

    def level(self):
        """
        Return depth contenance level.
        """
        level = self.aq_parent.level() + 1
        return level

    def is_main_taskconfig(self):
        """
        Tells wheter this task config is a sub task or not.
        """
        return self.level() == 1

    def get_schedule_config(self):
        """
        Return the parent ScheduleConfig.
        """
        from imio.schedule.content.schedule_config import IScheduleConfig

        context = self
        while not IScheduleConfig.providedBy(context):
            context = context.getParentNode()

        return context

    def get_scheduled_portal_type(self):
        """
        Return the portal_type of the selected scheduled_contenttype.
        """
        schedule_config = self.get_schedule_config()
        return schedule_config.get_scheduled_portal_type()

    def get_scheduled_interfaces(self):
        """
        Return the registration interface of the selected scheduled_contenttype.
        """
        schedule_config = self.get_schedule_config()
        return schedule_config.get_scheduled_interfaces()

    def group_to_assign(self, task_container, task):
        """
        Returns a default group to assign to the AutomatedTask.
        """
        # the value could be either the name of an adapter to call or the id
        # of an existing group
        group_id = self.default_assigned_group
        # try to get the adapter named 'group_id'
        default_group = None
        assign_group = queryMultiAdapter(
            (task_container, task), IDefaultTaskGroup, name=group_id
        )
        if assign_group:
            default_group = assign_group.group_id()

        # if no group was found use group_id
        group_id = default_group or group_id
        return group_id

    def user_to_assign(self, task_container, task):
        """
        Returns a default user to assign to the AutomatedTask.
        """
        # the value could be either the name of an adapter to call or the id
        # of an existing user
        user_id = self.default_assigned_user
        # try to get the adapter named 'user_id'
        default_user = None
        assign_user = queryMultiAdapter(
            (task_container, task), IDefaultTaskUser, name=user_id
        )
        if assign_user:
            default_user = assign_user.user_id()

        # if no user was found use user_id
        user_id = default_user or user_id
        return user_id

    def get_task_instances(self, root_container, states=[]):
        """
        Catalog query to return every AutomatedTask created
        from this TaskConfig contained in 'root_container'.
        """
        tasks = []
        to_explore = [root_container]
        while to_explore:
            current = to_explore.pop()
            if (
                IAutomatedTask.providedBy(current)
                and current.task_config_UID == self.UID()
            ):
                if not states:
                    tasks.append(current)
                elif api.content.get_state(current) in states:
                    tasks.append(current)
            if hasattr(current, "objectValues"):
                to_explore.extend(current.objectValues())
        tasks = sorted(tasks, key=lambda x: x.created())
        return tasks

    def get_task(self, task_container):
        """
        Return the unique AutomatedTask object created from this
        TaskConfig in 'task_container' if it exists.
        """
        tasks = self.get_task_instances(task_container)
        task_instance = tasks and tasks[0] or None
        return task_instance

    def get_created_task(self, task_container):
        """
        Return the unique AutomatedTask object created from this
        TaskConfig in 'task_container' if it exists and is not started yet..
        """
        tasks = self.get_task_instances(
            task_container, states=states_by_status[CREATION]
        )
        task_instance = tasks and tasks[0] or None
        return task_instance

    def get_started_task(self, task_container):
        """
        Return the unique AutomatedTask object created from this
        TaskConfig in 'task_container' if it exists and is started.
        """
        tasks = self.get_task_instances(
            task_container, states=states_by_status[STARTED]
        )
        task_instance = tasks and tasks[0] or None
        return task_instance

    def get_open_task(self, task_container):
        """
        Return the unique AutomatedTask object created from this
        TaskConfig in 'task_container' if it exists and is not closed yet.
        """
        states = states_by_status[CREATION] + states_by_status[STARTED]
        tasks = self.get_task_instances(task_container, states=states)
        task_instance = tasks and tasks[0] or None
        return task_instance

    def get_closed_tasks(self, task_container):
        """
        Return all the closed automatedTask objects created from this
        TaskConfig in 'task_container' .
        """
        tasks = self.get_task_instances(task_container, states=states_by_status[DONE])
        return tasks

    def get_closed_task(self, task_container):
        """
        Return the unique AutomatedTask object created from this
        TaskConfig in 'task_container' if it exists and is closed.
        """
        tasks = self.get_closed_tasks(task_container)
        task_instance = tasks and tasks[0] or None
        return task_instance

    def get_frozen_task(self, task_container):
        """
        Return the unique AutomatedTask object created from this
        TaskConfig in 'task_container' if it exists and is frozen.
        """
        tasks = self.get_task_instances(task_container, states=states_by_status[FROZEN])
        task_instance = tasks and tasks[0] or None
        return task_instance

    def task_already_exists(self, task_container):
        """
        Check if the task_container already has a task from this config.
        """
        return self.get_task_instances(task_container)

    def _eval(self, current_evaluation, conditions):
        """Return an evaluation based on current evaluated conditions
        This avoid to do too much computation if not necessary"""
        operators = [c.operator.lower() for c in conditions][:-1]
        evaluation = copy.deepcopy(current_evaluation)
        if len(evaluation) < len(operators) + 1:
            # Fill current_evaluation with False
            evaluation.extend(
                [False for i in range(len(evaluation), len(operators) + 1)]
            )
        eval_str = str(evaluation[0])
        for i, element in enumerate(evaluation[1:]):
            eval_str = "{0} {1} {2}".format(eval_str, str(operators[i]), str(element))
        return eval(eval_str)

    def evaluate_conditions(self, conditions, to_adapt, interface):
        """ """
        value = True
        task = None
        if self._debug_mode:
            task = to_adapt[-1]
            if not hasattr(task, "_log_debug"):
                task = None
        evaluation = []
        for condition_object in conditions or []:
            condition_name = condition_object.condition
            evaluation.append(
                self.evaluate_one_condition(
                    to_adapt=to_adapt,
                    interface=interface,
                    name=condition_name,
                )
            )
            if task:
                task._log_debug(
                    conditions={
                        condition_name: {
                            "operator": condition_object.operator,
                            "status": evaluation[-1]
                        }
                    }
                )
            value = self._eval(evaluation, conditions)
            if value is True:
                # Stop further computation
                return True

        return value

    def evaluate_one_condition(self, to_adapt, interface, name):
        """ """
        condition = getMultiAdapter(to_adapt, interface=interface, name=name)
        value = condition.evaluate() and True or False
        return value

    def get_conditions_status(self, conditions, to_adapt, interface):
        """
        Return two lists of all conditions status for a given task
        and task container.
        The first list is all the matched conditions, the second is
        all the unmatched conditions.
        """
        matched = []
        not_matched = []
        for condition_object in conditions or []:
            if not getattr(condition_object, "display_status", True):
                continue
            value = self.evaluate_one_condition(
                to_adapt=to_adapt,
                interface=interface,
                name=condition_object.condition,
            )
            if value:
                matched.append(condition_object.condition)
            else:
                not_matched.append(condition_object.condition)

        return matched, not_matched

    def should_create_task(self, task_container, parent_container=None):
        """
        Evaluate:
         - If the task container is on the state selected on 'starting_states'
         - All the creation conditions of a task with 'kwargs'.
           Returns True only if ALL the conditions are matched.
        This should be checked in a zope event to automatically create a task.
        """
        # schedule config should be enabled
        schedule_config = self.get_schedule_config()
        if not schedule_config.enabled:
            return False

        # config should be enabled
        if not self.enabled:
            return False

        # does the Task already exists?
        if self.task_already_exists(parent_container or task_container):
            return False

        # task container state match creation_state value?
        if not self.match_creation_state(task_container):
            return False

        # each conditions is matched?
        if not self.match_creation_conditions(task_container):
            return False

        return True

    def match_creation_state(self, task_container):
        """ """
        if not self.creation_state:
            return True

        container_state = api.content.get_state(task_container)
        return container_state in (self.creation_state or [])

    def match_creation_conditions(self, task_container):
        """ """
        return self.evaluate_conditions(
            conditions=self.creation_conditions,
            to_adapt=(task_container, self),
            interface=ICreationCondition,
        )

    def should_start_task(self, task_container, task):
        """
        Evaluate:
         - If the task container is on the state selected on 'starting_states'
         - All the starting conditions of a task with 'kwargs'.
           Returns True only if ALL the conditions are matched.
        This should be checked in a zope event to automatically start a task.
        """

        if self._debug_mode:
            task._set_log_debug("start", type="condition")
        # task container state match starting_states value?
        if not self.match_starting_states(task_container, task):
            return False

        # each conditions is matched?
        if not self.match_start_conditions(task_container, task):
            return False

        if not task.assigned_user:
            if self._debug_mode:
                task._log_debug(status=False, reason="no assigned user")
            return False

        if self._debug_mode:
            task._log_debug(status=True, reason="all conditions met")
            task._unset_log_debug()

        return True

    def match_starting_states(self, task_container, task):
        """ """
        if not self.starting_states:
            task._log_debug(
                start_state_condition=True,
                reason="no starting states",
                starting_states=self.starting_states,
            )
            return True

        container_state = api.content.get_state(task_container)
        status = container_state in (self.starting_states or [])

        task._log_debug(
            start_state_condition=status,
            reason=(
                status and "state in starting states"
                or "state not in starting states"
            ),
            starting_states=self.starting_states,
        )

        return status

    def match_start_conditions(self, task_container, task):
        """ """
        if self._debug_mode:
            task._set_log_debug("start_conditions")

        result = self.evaluate_conditions(
            conditions=self.start_conditions,
            to_adapt=(task_container, task),
            interface=IStartCondition,
        )
        if self._debug_mode:
            task._log_debug(
                status=result,
                reason=(
                    result and "all conditions met"
                    or "not all conditions met"
                ),
            )
            task._unset_log_debug()
        return result

    def start_conditions_status(self, task_container, task):
        """
        Return status of each start condition.
        """
        return self.get_conditions_status(
            conditions=self.start_conditions,
            to_adapt=(task_container, task),
            interface=IStartCondition,
        )

    def should_end_task(self, task_container, task):
        """
        Evaluate:
         - If the task has an assigned user
         - If the task container is on the state selected on 'ending_states'
         - All the existence conditions of a task.
           Returns True only if ALL the conditions are matched.
        This should be checked in a zope event to automatically close a task.
        """
        if self._debug_mode:
            task._set_log_debug("end", type="condition")

        if not task.assigned_user:
            if self._debug_mode:
                task._log_debug(status=False, reason="no assigned user")
            return False

        # task container state match any ending_states value?
        if not self.match_ending_states(task_container, task):
            return False

        if not self.match_end_conditions(task_container, task):
            return False

        if self._debug_mode:
            task._log_debug(status=True, reason="all conditions met")
            task._unset_log_debug()

        return True

    def match_ending_states(self, task_container, task):
        """ """
        default_ending_states = queryAdapter(task_container, IDefaultEndingStates)
        default_ending_states = default_ending_states and default_ending_states() or []

        ending_states = (
            self.ending_states
            and list(default_ending_states) + list(self.ending_states)
            or []
        )

        if not ending_states:
            task._log_debug(
                end_state_condition=True,
                reason="no ending states",
                ending_states=self.ending_states,
            )
            return True

        container_state = api.content.get_state(task_container)
        status = container_state in ending_states

        task._log_debug(
            end_state_condition=status,
            reason=(
                status and "state in ending states"
                or "state not in ending states"
            ),
            ending_states=self.ending_states,
            default_ending_states=default_ending_states,
        )

        return status

    def match_end_conditions(self, task_container, task):
        """ """
        if self._debug_mode:
            task._set_log_debug("end_conditions")
        result = self.evaluate_conditions(
            conditions=self.end_conditions,
            to_adapt=(task_container, task),
            interface=IEndCondition,
        )
        if self._debug_mode:
            task._log_debug(
                status=result,
                reason=(
                    result and "all conditions met"
                    or "not all conditions met"
                ),
            )
            task._unset_log_debug()
        return result

    def end_conditions_status(self, task_container, task):
        """
        Return status of each end condition.
        """
        if self._debug_mode:
            task._set_log_debug("end_conditions")

        result = self.get_conditions_status(
            conditions=self.end_conditions,
            to_adapt=(task_container, task),
            interface=IEndCondition,
        )
        if self._debug_mode:
            task._log_debug(
                status=result,
                reason=(
                    result and "all conditions met"
                    or "not all conditions met"
                ),
            )
            task._unset_log_debug()
        return result

    def should_freeze_task(self, task_container, task):
        """
        Evaluate:
         - If the task has an assigned user
         - If the task container is on the state selected on 'freeze_states'
         - All the existence conditions of a task.
           Returns True only if ALL the conditions are matched.
        This should be checked in a zope event to automatically close a task.
        """

        if not task.assigned_user:
            return False

        # task is already frozen or done
        if task.get_status() in [FROZEN, DONE]:
            return False

        # task container state match any freeze_states value?
        if not self.match_freeze_states(task_container):
            return False

        if not self.match_freeze_conditions(task_container, task):
            return False

        return True

    def match_freeze_states(self, task_container):
        """ """
        default_freeze_states = queryAdapter(task_container, IDefaultFreezeStates)
        default_freeze_states = default_freeze_states and default_freeze_states() or []
        freeze_states = (
            list(default_freeze_states) + list(self.freeze_states or []) or []
        )

        container_state = api.content.get_state(task_container)
        return container_state in freeze_states

    def match_freeze_conditions(self, task_container, task):
        """ """
        return self.evaluate_conditions(
            conditions=self.freeze_conditions,
            to_adapt=(task_container, task),
            interface=IFreezeCondition,
        )

    def freeze_conditions_status(self, task_container, task):
        """
        Return status of each freeze condition.
        """
        return self.get_conditions_status(
            conditions=self.freeze_conditions,
            to_adapt=(task_container, task),
            interface=IFreezeCondition,
        )

    def should_thaw_task(self, task_container, task):
        """
        Evaluate:
         - If the task has an assigned user
         - If the task container is on the state selected on 'thaw_states'
         - All the existence conditions of a task.
           Returns True only if ALL the conditions are matched.
        This should be checked in a zope event to automatically close a task.
        """
        if task.get_status() is not FROZEN:
            return False

        if not task.assigned_user:
            return False

        # task container state match any thaw_states value?
        if not self.match_thaw_states(task_container):
            return False

        if not self.match_thaw_conditions(task_container, task):
            return False

        return True

    def match_thaw_states(self, task_container):
        """ """
        default_thaw_states = queryAdapter(task_container, IDefaultThawStates)
        default_thaw_states = default_thaw_states and default_thaw_states() or []
        thaw_states = list(default_thaw_states) + list(self.thaw_states or []) or []

        container_state = api.content.get_state(task_container)
        return container_state in thaw_states

    def match_thaw_conditions(self, task_container, task):
        """ """
        return self.evaluate_conditions(
            conditions=self.thaw_conditions,
            to_adapt=(task_container, task),
            interface=IThawCondition,
        )

    def thaw_conditions_status(self, task_container, task):
        """
        Return status of each thaw condition.
        """
        return self.get_conditions_status(
            conditions=self.thaw_conditions,
            to_adapt=(task_container, task),
            interface=IThawCondition,
        )

    def should_recurred(self, task_container):
        """
        Evaluate if the a new task should be created for the task container
        depending on the recurrence condition
        """
        # schedule config should be enabled
        schedule_config = self.get_schedule_config()
        if not schedule_config.enabled:
            return False

        if getattr(self, "activate_recurrency", False) is False:
            return False

        if self.match_recurrence_states(task_container) is False:
            return False

        if not getattr(self, "recurrence_conditions", None):
            return True

        return self.evaluate_conditions(
            conditions=self.recurrence_conditions,
            to_adapt=(task_container, self),
            interface=ICreationCondition,
        )

    def match_recurrence_states(self, task_container):
        """ """
        if not self.recurrence_states:
            return True

        container_state = api.content.get_state(task_container)
        return container_state in (self.recurrence_states or [])

    def create_task(self, task_container):
        """
        To implements in subclasses.
        """

    def start_task(self, task):
        """
        Default implementation is to put the task on the state 'to_do'.
        """
        with api.env.adopt_roles(["Manager"]):
            if api.content.get_state(task) == "created":
                api.content.transition(obj=task, transition="do_to_assign")
            if api.content.get_state(task) == "to_assign" and task.assigned_user:
                api.content.transition(obj=task, transition="do_to_do")
        task.reindex_parent_tasks(idxs=["is_solvable_task"])

    def end_task(self, task):
        """
        Default implementation is to put the task on the state 'closed'.
        """
        if api.content.get_state(task) == "created":
            api.content.transition(obj=task, transition="do_to_assign")
        if api.content.get_state(task) == "to_assign":
            api.content.transition(obj=task, transition="do_to_do")
        if api.content.get_state(task) == "to_do":
            api.content.transition(obj=task, transition="do_realized")
        if api.content.get_state(task) == "realized":
            with api.env.adopt_roles(["Reviewer"]):
                api.content.transition(obj=task, transition="do_closed")
        task.reindex_parent_tasks(idxs=["is_solvable_task"])

    def freeze_task(self, task):
        """
        Default implementation is to put the task on the state 'frozen'.
        """
        annotations = IAnnotations(task)
        freeze_infos = annotations.get(
            "imio.schedule.freeze_task",
            {
                "freeze_date": None,
                "previous_state": task.get_state(),
                "previous_freeze_duration": 0,
            },
        )
        freeze_infos["freeze_date"] = str(datetime.now().date())
        freeze_infos["freeze_state"] = task.get_state()
        annotations["imio.schedule.freeze_task"] = freeze_infos

        portal_workflow = api.portal.get_tool("portal_workflow")
        workflow_def = portal_workflow.getWorkflowsFor(task)[0]
        workflow_id = workflow_def.getId()
        workflow_state = portal_workflow.getStatusOf(workflow_id, task)
        workflow_state["review_state"] = "frozen"
        portal_workflow.setStatusOf(workflow_id, task, workflow_state.copy())

        task.reindex_parent_tasks(idxs=["is_solvable_task"])

    def thaw_task(self, task):
        """
        Default implementation is to put the task on the state 'frozen'.
        """

        annotations = IAnnotations(task)
        freeze_infos = annotations["imio.schedule.freeze_task"]
        calculator = getMultiAdapter(
            (task.get_container(), task),
            interface=IFreezeDuration,
            name="schedule.freeze_duration",
        )
        new_freeze_duration = calculator.freeze_duration
        new_freeze_infos = freeze_infos.copy()
        new_freeze_infos["previous_freeze_duration"] = new_freeze_duration
        annotations["imio.schedule.freeze_task"] = new_freeze_infos

        portal_workflow = api.portal.get_tool("portal_workflow")
        workflow_def = portal_workflow.getWorkflowsFor(task)[0]
        workflow_id = workflow_def.getId()
        workflow_state = portal_workflow.getStatusOf(workflow_id, task)
        workflow_state["review_state"] = freeze_infos["previous_state"]
        portal_workflow.setStatusOf(workflow_id, task, workflow_state.copy())

        task.reindex_parent_tasks(idxs=["is_solvable_task"])

    def compute_due_date(self, task_container, task):
        """
        Evaluate 'task_container' and 'task' to compute the due date of a task.
        This should be checked in a zope event to automatically compute and set the
        due date of 'task'.
        """
        adapters = getattr(self, "calculation_delay", [])
        # Backward compatibility
        if not adapters:
            adapters = ["schedule.calculation_default_delay"]
        if self._debug_mode:
            task._set_log_debug("due_date")
        due_date = None
        for adapter in adapters:
            calculator = getMultiAdapter(
                (task_container, task),
                interface=ICalculationDelay,
                name=adapter,
            )
            due_date = calculator.due_date
            task._log_debug(base_due_date=due_date)

        additional_delay = self.additional_delay or "0"
        additional_delay_tal = getattr(self, "additional_delay_tal", False)
        if additional_delay_tal is True:
            data = {
                "nothing": None,
                "licence": task_container,
                "task": task,
                "request": getattr(task_container, "REQUEST", None),
            }
            ctx = getEngine().getContext(data)
            try:
                additional_delay = Expression(additional_delay)(ctx)
            except Exception as e:
                logger.warn(
                    "The condition '%s' defined for element at '%s' is wrong!  Message is : %s"
                    % (additional_delay, task.absolute_url(), e)
                )
                additional_delay = 0
        else:
            additional_delay = int(additional_delay)
        delay_type = getattr(self, "additional_delay_type", "absolute")
        task._log_debug(
            additional_delay=additional_delay,
            delay_type=delay_type,
        )
        if additional_delay and delay_type == "working_days":
            calendar = WorkingDaysCalendar()
            due_date = calendar.add_working_days(due_date, additional_delay)
        elif additional_delay:
            due_date = due_date + relativedelta(days=+additional_delay)
        task._log_debug(with_additional_delay_date=due_date)

        annotations = IAnnotations(task)
        freeze_infos = annotations.get("imio.schedule.freeze_task", None)
        if freeze_infos:
            task._log_debug(
                freeze_infos=freeze_infos,
                before_freeze_date=due_date,
            )
            due_date = due_date + relativedelta(
                days=+freeze_infos["previous_freeze_duration"]
            )

        round_day = int(self.round_to_day)
        if round_day:
            task._log_debug(round_day=round_day, before_rounded_date=due_date)
            due_date = round_to_weekday(due_date, round_day)

        # frozen tasks have infinite due date
        if task.get_status() in FROZEN:
            task._log_debug(is_frozen=True)
            due_date = date(9999, 1, 1)

        if self._debug_mode:
            task._log_debug(due_date=due_date)
            task._unset_log_debug()
        return due_date

    def _create_task_instance(self, creation_place, task_id):
        """
        Helper method to use to implement 'create_task'.
        """
        if task_id in creation_place.objectIds():
            raise TaskAlreadyExists(task_id)

        task_portal_type = self.get_task_type()
        portal_types = api.portal.get_tool("portal_types")
        type_info = portal_types.getTypeInfo(task_portal_type)

        task = type_info._constructInstance(
            container=creation_place,
            id=task_id,
            title=self.Title(),
            schedule_config_UID=self.get_schedule_config().UID(),
            task_config_UID=self.UID(),
        )

        marker_interfaces = [getInterface("", i) for i in self.marker_interfaces or []]
        alsoProvides(task, *marker_interfaces)

        return task

    @property
    def default_task_id(self):
        return "TASK_{0}".format(self.id)

    def create_recurring_task(self, task_container, creation_place=None):
        """
        Create a recurring task
        """
        creation_place = creation_place or task_container
        object_ids = creation_place.objectIds()
        related_ids = [
            i
            for i in object_ids
            if i.startswith(self.default_task_id)
            and creation_place[i].get_task_config() == self
        ]
        if len(related_ids) > 0:
            object_id = related_ids[-1]
            if api.content.get_state(creation_place[object_id]) != "closed":
                return
        if self.default_task_id in object_ids:
            task_id = "{0}-{1}".format(
                self.default_task_id,
                len(related_ids),
            )
        else:
            task_id = self.default_task_id
        return self.create_task(
            task_container,
            creation_place=creation_place,
            task_id=task_id,
        )


class TaskConfig(Container, BaseTaskConfig):
    """
    TaskConfig dexterity class.
    """

    implements(ITaskConfig)

    def get_task_type(self):
        """
        Return the content type of task to create.
        """
        return "AutomatedTask"

    def create_task(self, task_container, creation_place=None, task_id=None):
        """
        Just create the task and return it.
        """
        creation_place = creation_place or task_container
        task_id = task_id or self.default_task_id
        task = self._create_task_instance(creation_place, task_id)

        task.assigned_group = self.group_to_assign(task_container, task)
        task.assigned_user = self.user_to_assign(task_container, task)
        task.due_date = self.compute_due_date(task_container, task)
        task.reindexObject()
        task.reindex_parent_tasks(idxs=["is_solvable_task"])

        return task


class IMacroCreationConditionSchema(Interface):

    condition = SubFormContextChoice(
        title=_(u"Condition"),
        vocabulary="schedule.macrotask_creation_conditions",
        required=True,
    )

    operator = schema.Choice(
        title=_(u"Operator"),
        vocabulary="schedule.logical_operator",
        default="AND",
    )

    display_status = schema.Bool(
        title=_(u"display_status"),
        default=True,
    )


class IMacroStartConditionSchema(Interface):

    condition = SubFormContextChoice(
        title=_(u"Condition"),
        vocabulary="schedule.macrotask_start_conditions",
        required=True,
    )

    operator = schema.Choice(
        title=_(u"Operator"),
        vocabulary="schedule.logical_operator",
        default="AND",
    )

    display_status = schema.Bool(
        title=_(u"display_status"),
        default=True,
    )


class IMacroEndConditionSchema(Interface):

    condition = SubFormContextChoice(
        title=_(u"Condition"),
        vocabulary="schedule.macrotask_end_conditions",
        required=True,
    )

    operator = schema.Choice(
        title=_(u"Operator"),
        vocabulary="schedule.logical_operator",
        default="AND",
    )

    display_status = schema.Bool(
        title=_(u"display_status"),
        default=True,
    )


class IMacroFreezeConditionSchema(Interface):

    condition = SubFormContextChoice(
        title=_(u"Condition"),
        vocabulary="schedule.macrotask_freeze_conditions",
        required=True,
    )

    operator = schema.Choice(
        title=_(u"Operator"),
        vocabulary="schedule.logical_operator",
        default="AND",
    )

    display_status = schema.Bool(
        title=_(u"display_status"),
        default=True,
    )


class IMacroThawConditionSchema(Interface):

    condition = SubFormContextChoice(
        title=_(u"Condition"),
        vocabulary="schedule.macrotask_thaw_conditions",
        required=True,
    )

    operator = schema.Choice(
        title=_(u"Operator"),
        vocabulary="schedule.logical_operator",
        default="AND",
    )

    display_status = schema.Bool(
        title=_(u"display_status"),
        default=True,
    )


class IMacroRecurrenceConditionSchema(Interface):

    condition = SubFormContextChoice(
        title=_(u"Condition"),
        vocabulary="schedule.macrotask_creation_conditions",
        required=True,
    )

    operator = schema.Choice(
        title=_(u"Operator"),
        vocabulary="schedule.logical_operator",
        default="AND",
    )

    display_status = schema.Bool(
        title=_(u"display_status"),
        default=True,
    )


class IMacroTaskConfig(ITaskConfig):
    """
    TaskConfig dexterity schema.
    """

    start_date = schema.Choice(
        title=_(u"Start date"),
        description=_(u"Select the start date used to compute the due date."),
        vocabulary="schedule.macrotask_start_date",
        required=True,
    )

    creation_conditions = schema.List(
        title=_(u"Creation conditions"),
        description=_(u"Select creation conditions of the task"),
        value_type=schema.Object(
            title=_(u"Conditions"),
            schema=IMacroCreationConditionSchema,
        ),
        required=False,
    )

    start_conditions = schema.List(
        title=_(u"Start conditions"),
        description=_(u"Select start conditions of the task"),
        value_type=schema.Object(
            title=_(u"Conditions"),
            schema=IMacroStartConditionSchema,
        ),
        required=False,
    )

    end_conditions = schema.List(
        title=_(u"End conditions"),
        description=_(u"Select end conditions of the task."),
        value_type=schema.Object(
            title=_(u"Conditions"),
            schema=IMacroEndConditionSchema,
        ),
        required=False,
    )

    freeze_conditions = schema.List(
        title=_(u"Freeze conditions"),
        description=_(u"Select freeze conditions of the task."),
        value_type=schema.Object(
            title=_(u"Conditions"),
            schema=IMacroFreezeConditionSchema,
        ),
        required=False,
    )

    thaw_conditions = schema.List(
        title=_(u"Thaw conditions"),
        description=_(u"Select thaw conditions of the task."),
        value_type=schema.Object(
            title=_(u"Conditions"),
            schema=IMacroThawConditionSchema,
        ),
        required=False,
    )

    recurrence_conditions = schema.List(
        title=_(u"Recurrence condition"),
        description=_(u"Select recurrence conditions of the task."),
        value_type=schema.Object(
            title=_("Conditions"),
            schema=IMacroRecurrenceConditionSchema,
        ),
        required=False,
    )


class MacroTaskConfig(Container, BaseTaskConfig):
    """
    MacroTaskConfig dexterity class.
    """

    implements(IMacroTaskConfig)

    def get_task_type(self):
        """
        Return the content type of task to create.
        """
        return "AutomatedMacroTask"

    def get_subtask_configs(self):
        """
        Return all the subtasks configs of this macro task.
        """
        catalog = api.portal.get_tool("portal_catalog")
        config_path = "/".join(self.getPhysicalPath())

        query = {
            "object_provides": ITaskConfig.__identifier__,
            "path": {"query": config_path, "depth": 1},
            "sort_on": "getObjPositionInParent",
        }

        config_brains = catalog(**query)
        subtask_configs = [brain.getObject() for brain in config_brains]

        return subtask_configs

    def create_task(self, task_container, creation_place=None, task_id=None):
        """
        Create the macrotask and subtasks.
        """
        creation_place = creation_place or task_container
        task_id = task_id or self.default_task_id
        macrotask = self._create_task_instance(creation_place, task_id)

        for config in self.get_subtask_configs():
            if config.should_create_task(task_container):
                config.create_task(task_container, creation_place=macrotask)

        # compute some fields only after all substasks are created
        macrotask.assigned_group = self.group_to_assign(task_container, macrotask)
        macrotask.assigned_user = self.user_to_assign(task_container, macrotask)
        macrotask.due_date = self.compute_due_date(task_container, macrotask)
        macrotask.reindexObject()

        return macrotask

    def should_end_task(self, task_container, task):
        """
        See 'should_end_task' in BaseTaskConfig
        Evaluate:
         - If the task has an assigned user
         - If the task container is on the state selected on 'ending_states'
         - All the existence conditions of a task with 'task' and 'kwargs'.
           Returns True only if ALL the conditions are matched.
         - If all the subtasks are ended.
        This should be checked in a zope event to automatically close a task.
        """
        task_done = super(MacroTaskConfig, self).should_end_task(task_container, task)
        if not task_done:
            return False

        subtasks_done = all(
            [subtask.get_status() == DONE for subtask in task.get_subtasks()]
        )
        if not subtasks_done:
            return False

        return True

    def freeze_task(self, task):
        """
        Default implementation is to put the task  and all its subtasks on the
        state 'frozen'.
        """
        subtasks_to_freeze = [
            tsk for tsk in task.get_subtasks() if tsk.get_status() not in [FROZEN, DONE]
        ]
        for subtask in subtasks_to_freeze:
            subtask_config = subtask.get_task_config()
            subtask_config.freeze_task(subtask)

        super(MacroTaskConfig, self).freeze_task(task)

    def thaw_task(self, task):
        """
        Default implementation is to resume the task and all its subtasks on their
        previous state.
        """
        subtasks_to_thaw = [
            tsk for tsk in task.get_subtasks() if tsk.get_status() == FROZEN
        ]
        for subtask in subtasks_to_thaw:
            subtask_config = subtask.get_task_config()
            subtask_config.thaw_task(subtask)

        super(MacroTaskConfig, self).thaw_task(task)
