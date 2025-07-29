# -*- coding: utf-8 -*-

from collective.task import _ as CTMF
from collective.task.behaviors import ITask
from collective.task.behaviors import get_parent_assigned_group
from collective.task.behaviors import get_users_vocabulary
from collective.task.field import LocalRoleMasterSelectField
from imio.schedule.config import CREATION
from imio.schedule.config import DONE
from imio.schedule.config import STARTED
from imio.schedule.config import status_by_state
from imio.schedule.interfaces import ScheduleConfigNotFound
from imio.schedule.interfaces import TaskConfigNotFound
from plone import api
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.dexterity.content import Item
from plone.memoize.request import cache
from zope.interface import implements

import logging
import os

logger = logging.getLogger("imio.schedule")


class IAutomatedTask(ITask):
    """
    AutomatedTask dexterity schema.
    """

    directives.order_before(assigned_group="assigned_user")
    directives.order_before(assigned_group="ITask.assigned_user")
    assigned_group = LocalRoleMasterSelectField(
        title=CTMF(u"Assigned group"),
        required=True,
        vocabulary="collective.task.AssignedGroups",
        slave_fields=(
            {
                "name": "ITask.assigned_user",
                "slaveID": "#form-widgets-ITask-assigned_user",
                "action": "vocabulary",
                "vocab_method": get_users_vocabulary,
                "control_param": "group",
            },
        ),
        defaultFactory=get_parent_assigned_group,
    )


class BaseAutomatedTask(object):
    """
    Base class for AutomatedTask content types.
    """

    task_config_UID = ""
    schedule_config_UID = ""
    _debug_category = None
    _previous_category = None
    _debug_data = None  # Variable usefull for debugging computation

    def get_container(self):
        """
        Return the task container.
        """
        container = self
        while IAutomatedTask.providedBy(container):
            container = container.getParentNode()

        return container

    def level(self):
        """
        Return the task depth contenance level.
        """
        container = self
        level = -1
        while IAutomatedTask.providedBy(container):
            container = container.getParentNode()
            level = level + 1

        return level

    def get_schedule_config(self):
        """
        Return associated schedule config.
        """
        catalog = api.portal.get_tool("portal_catalog")
        brains = catalog(UID=self.schedule_config_UID)
        if brains:
            return brains[0].getObject()
        else:
            raise ScheduleConfigNotFound("UID {}".format(self.schedule_config_UID))

    @cache(get_key=lambda m, task: task.id, get_request="self.REQUEST")
    def get_task_config(self):
        """
        Return associated task config.
        """
        catalog = api.portal.get_tool("portal_catalog")
        with api.env.adopt_roles(["Manager"]):
            brains = catalog.unrestrictedSearchResults(UID=self.task_config_UID)
            if brains:
                return brains[0].getObject()
            else:
                raise TaskConfigNotFound("UID {}".format(self.task_config_UID))

    def get_status(self):
        """
        Return the status of the task
        """
        return status_by_state[self.get_state()]

    @cache(get_key=lambda m, task: task.id, get_request="self.REQUEST")
    def start_conditions_status(self):
        """
        See start_conditions_status of TaskConfig.
        """
        task_config = self.get_task_config()
        container = self.get_container()
        status = task_config.start_conditions_status(container, self)
        return status

    @cache(get_key=lambda m, task: task.id, get_request="self.REQUEST")
    def starting_states_status(self):
        """ """
        config = self.get_task_config()
        starting_states = config.starting_states
        if not starting_states:
            return

        container = self.get_container()
        container_state = api.content.get_state(container)
        return (container_state, starting_states)

    @cache(get_key=lambda m, task: task.id, get_request="self.REQUEST")
    def end_conditions_status(self):
        """
        See end_conditions_status of TaskConfig.
        """
        task_config = self.get_task_config()
        container = self.get_container()
        status = task_config.end_conditions_status(container, self)
        return status

    def ending_states_status(self):
        """ """
        config = self.get_task_config()
        ending_states = config.ending_states
        if not ending_states:
            return

        container = self.get_container()
        container_state = api.content.get_state(container)
        return (container_state, ending_states)

    def get_state(self):
        return api.content.get_state(self)

    def get_subtasks(self):
        """
        A normal task has no sub tasks.
        """
        return []

    @property
    def end_date(self):
        """ """
        if self.get_status() == DONE:
            wf_history = self.workflow_history["task_workflow"][::-1]
            for action in wf_history:
                if status_by_state[action["review_state"]] is DONE:
                    end_date = action["time"]
                    return end_date.asdatetime()
        return None

    def reindex_parent_tasks(self, idxs=[]):
        """
        Reindex 'idxs' indexes of all the parent tasks of this task.
        """
        # reindex parent tasks
        parent_task = self.getParentNode()
        while IAutomatedTask.providedBy(parent_task):
            parent_task.reindexObject(idxs)
            parent_task = parent_task.getParentNode()

    @property
    def is_solvable(self):
        """
        Return True if this task and its OPEN (sub-)subtasks have the same assigned_user.
        """
        subtasks = self.get_subtasks()
        while subtasks:
            subtask = subtasks.pop()
            if subtask.get_status() in [CREATION, STARTED]:
                if subtask.assigned_user != self.assigned_user:
                    return False
                subtasks.extend(subtask.get_subtasks())

        return True

    def _start(self):
        """
        Delegate start operation to the task_config
        """
        task_config = self.get_task_config()
        task_config.start_task(self)

    def _end(self):
        """
        Delegate end operation to the task_config
        """
        task_config = self.get_task_config()
        with api.env.adopt_roles(["Manager"]):
            task_config.end_task(self)

    def _freeze(self):
        """
        Delegate freeze operation to the task_config
        """
        task_config = self.get_task_config()
        task_config.freeze_task(self)

    def _thaw(self):
        """
        Delegate thaw operation to the task_config
        """
        task_config = self.get_task_config()
        task_config.thaw_task(self)

    def _log_debug(self, **kwargs):
        """Compute debug informations for the current task"""
        if self._debug_category is None:
            # logger.debug("Can not log without a log category")
            return
        self._debug_data[self._debug_category].update(kwargs)

    def _set_log_debug(self, category, type=None):
        """initialize debug log for a specific category"""
        if not hasattr(self, "_debug_data") or self._debug_data is None:
            self._debug_data = {}
        if category not in self._debug_data:
            if type == "condition":
                self._debug_data[category] = {
                    "status": None,
                    "reason": "",
                }
            else:
                self._debug_data[category] = {}
        if self._debug_category is not None:
            self._previous_category = self._debug_category
        self._debug_category = category

    def _unset_log_debug(self):
        if self._previous_category is not None:
            self._debug_category = self._previous_category
            self._previous_category = None
        else:
            self._debug_category = None


class AutomatedTask(Item, BaseAutomatedTask):
    """ """

    implements(IAutomatedTask)


class IAutomatedMacroTask(IAutomatedTask):
    """
    AutomatedTask dexterity schema.
    """


class AutomatedMacroTask(Container, BaseAutomatedTask):
    """ """

    implements(IAutomatedMacroTask)

    def get_subtasks(self):
        """
        Return all sub tasks of this macro task.
        """
        sub_tasks = [obj for obj in self.objectValues() if ITask.providedBy(obj)]
        return sub_tasks

    def get_last_subtasks(self):
        """
        Return each last unique sub task of this macro task.
        """
        subtask_type = set()
        sub_tasks = []

        for obj in reversed(self.objectValues()):
            if ITask.providedBy(obj):
                subtask = obj
                if subtask.task_config_UID not in subtask_type:
                    subtask_type.add(subtask.task_config_UID)
                    sub_tasks.append(subtask)

        return reversed(sub_tasks)
