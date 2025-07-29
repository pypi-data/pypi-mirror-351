# encoding: utf-8

from imio.schedule.config import DONE
from imio.schedule.config import STARTED
from imio.schedule.config import status_by_state

from plone import api

from Products.Five import BrowserView


class TaskCompletionView(BrowserView):
    """
    View of the popup showing the completion details of a task.
    Display the status of each start/end condition of the task.
    Display if the starting/ending state is matched or not.
    """

    subtask_title_label = "Title"
    subtask_todo_title_label = "Title"
    subtask_status_label = "Status"
    due_date_label = "Due date"
    end_date_label = "End date"
    assigned_user_label = "Assigned to"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.task = context

    def get_conditions_status(self):
        """
        List all the tasks conditions status (except for workflow state).
        """

    def get_state_status(self):
        """ """

    def get_subtasks_status(self):
        """ """
        created = []
        started = []
        done = []
        for subtask in self.task.get_last_subtasks():
            status = status_by_state[self.get_state(subtask)]
            if status is DONE:
                done.append(subtask)
            elif status is STARTED:
                started.append(subtask)
            else:
                created.append(subtask)

        return created, started, done

    def get_state(self, context):
        """
        Return the context workflow state.
        """
        return api.content.get_state(context)

    def display_user_name(self, user_id):
        """
        Return the full name of the given user id.
        """
        user = api.user.get(user_id)
        user_name = user and user.getProperty("fullname") or user_id
        return user_name

    def display_date(self, date):
        """ """
        if not date:
            return "-"
        if date.year == 9999:
            return u"\u221E".encode("utf-8")

        return date.strftime("%d/%m/%Y")


class TaskStartStatusView(TaskCompletionView):
    """
    View of the popup showing the start completion details of a created task.
    Display the status of each start condition of the task.
    Display the status of each subtask.
    Display if the starting state is matched or not.
    """

    def get_conditions_status(self):
        """
        List all the tasks conditions status (except for workflow state).
        """
        return self.task.start_conditions_status()

    def get_state_status(self):
        """ """
        return self.task.starting_states_status()


class TaskStartSimpleStatusView(TaskStartStatusView):
    """
    Same as the above but without subtasks status.
    """

    def get_subtasks_status(self):
        """
        Do not display subtasks.
        """
        return [], [], []


class TaskEndStatusView(TaskCompletionView):
    """
    View of the popup showing the end completion details of a started task.
    Display the status of each end condition of the task.
    Display if the ending state is matched or not.
    """

    def get_conditions_status(self):
        """
        List all the tasks conditions status (except for workflow state).
        """
        return self.task.end_conditions_status()

    def get_state_status(self):
        """ """
        return self.task.ending_states_status()


class TaskEndSimpleStatusView(TaskEndStatusView):
    """
    Same as the above but without subtasks status.
    """

    def get_subtasks_status(self):
        """
        Do not display subtasks.
        """
        return [], [], []
