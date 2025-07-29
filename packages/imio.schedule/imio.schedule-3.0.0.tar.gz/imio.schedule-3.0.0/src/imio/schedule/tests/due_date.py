# -*- coding: utf-8 -*-

from imio.schedule.content.logic import StartDate


class ContainerCreationDate(StartDate):
    """
    Test StartDate returning the creation date of the task container.
    """

    def start_date(self):
        return self.task_container.creation_date
