# -*- coding: utf-8 -*-

from DateTime import DateTime

from plone import api

from imio.schedule.config import STARTED
from imio.schedule.config import status_by_state
from imio.schedule.interfaces import IDefaultTaskGroup
from imio.schedule.interfaces import IDefaultTaskUser
from imio.schedule.interfaces import IMacroTaskStartDate
from imio.schedule.interfaces import IStartDate
from imio.schedule.interfaces import ITaskLogic

from zope.interface import implements


class CreationTaskLogic(object):
    """
    Base class for any object adapting a task container into
    some task logic (condition, user assigment, due date..)
    called during the task craetion.
    """

    implements(ITaskLogic)

    def __init__(self, task_container, task_config):
        self.task_container = task_container
        self.task_config = task_config


class TaskLogic(object):
    """
    Base class for any object adapting a task container and a task
    into some logic (condition, user assigment, due date..).
    """

    implements(ITaskLogic)

    def __init__(self, task_container, task):
        self.task_container = task_container
        self.task = task
        self.task_config = task.get_task_config()


class StartDate(TaskLogic):
    """
    Base class for TaskConfig due dates.
    """

    implements(IStartDate)

    def start_date(self):
        """
        To override.
        Compute a due date from task_container
        then return it.
        """


class MacroTaskStartDate(StartDate):
    """
    Base class for TaskConfig due dates.
    """

    implements(IMacroTaskStartDate)

    def start_date(self):
        """
        To override.
        Compute a due date from task_container
        then return it.
        """


class TaskStartingDate(StartDate):
    """
    Return the date when the task started.
    """

    def start_date(self):
        """
        Return the date when the task started.
        """
        history = self.task.workflow_history.values()[0]
        for state_history in history:
            if status_by_state[state_history.get("review_state")] is STARTED:
                return state_history["time"]


class SubtaskHighestDueDate(MacroTaskStartDate):
    """
    Return the highest due date of the subtasks.
    """

    def start_date(self):
        """
        Return the highest due date of the subtasks.
        """
        subtasks = self.task.get_subtasks()
        if not subtasks:
            return None
        due_dates = [DateTime(str(t.due_date)) for t in subtasks if t.due_date]
        return due_dates and max(due_dates) or None


class AssignTaskUser(TaskLogic):
    """
    Base class for adapters adapting a TaskContainer to return a user to
    assign to its tasks.
    Register adapters inheriting this class in the products using
    imio.schedule and override 'user_id' method.
    """

    implements(IDefaultTaskUser)

    def user_id(self):
        """
        To override.
        """


class AssignCurrentUser(AssignTaskUser):
    """
    Return the current connected user to assign it as default assigned
    user of a new AutomatedTask.
    """

    def user_id(self):
        """
        Return the id of the current user.
        """
        user = api.user.get_current()
        user_id = user.getUserName()
        return user_id


class AssignOwnerOfLastSimilarTask(AssignTaskUser):
    """
    Return the current connected user to assign it as default assigned
    user of a new AutomatedTask.
    """

    def user_id(self):
        """
        Return the id of the current user.
        """
        user = api.user.get_current()
        user_id = user.getUserName()
        return user_id


class AssignTaskGroup(TaskLogic):
    """
    Base class for adapters adapting a TaskContainer to return a group to
    assign to its tasks.
    Register adapters inheriting this class in the products using
    imio.schedule and override 'group_id' method.
    """

    implements(IDefaultTaskGroup)

    def group_id(self):
        """
        To override.
        """
