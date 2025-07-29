# -*- coding: utf-8 -*-

from imio.schedule.content.logic import AssignTaskGroup

from plone import api


class AssignAuthenticatedUsersGroup(AssignTaskGroup):
    """
    Return the AuthenticatedUsers group as the default group
    to assign on a new AutomatedTask.
    """

    def group_id(self):
        """
        Return the id of AuthenticatedUsers group.
        """
        return api.group.get("AuthenticatedUsers")
