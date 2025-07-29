# -*- coding: utf-8 -*-

from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from zope.annotation import IAnnotations
from zope.component import queryMultiAdapter

from imio.schedule.content.logic import TaskLogic
from imio.schedule.interfaces import IStartDate


class BaseCalculationDelay(TaskLogic):

    start_date_interface = IStartDate

    @property
    def start_date(self):
        """Return the start date for the task container and the task"""
        date_adapter = queryMultiAdapter(
            (self.task_container, self.task),
            interface=self.start_date_interface,
            name=self.task_config.start_date,
        )
        start_date = date_adapter and date_adapter.start_date()
        if not start_date:
            start_date = date(9999, 1, 1)
        if not isinstance(start_date, date):
            start_date = start_date.asdatetime().date()
        return start_date

    @property
    def delta(self):
        """Return the calculated delay + the extra delay"""
        return self.calculate_delay()

    @property
    def due_date(self):
        """Return the due date calculated with the delay"""
        return self.start_date + relativedelta(days=+self.delta)

    def calculate_delay(self):
        """Method that must be overrided to calculate the delay"""
        raise NotImplementedError

    def compute_due_date(self, date):
        """Return the addition of the given date and the extra delay"""
        return date + relativedelta(days=+self.delta)


class CalculationDefaultDelay(BaseCalculationDelay):
    """ """

    def calculate_delay(self):
        return 0


class DefaultFreezeDuration(object):
    """ """

    def __init__(self, task_container, task):
        self.container = task_container
        self.task = task

    @property
    def freeze_duration(self):
        annotations = IAnnotations(self.task)
        freeze_infos = annotations["imio.schedule.freeze_task"]
        freeze_date = datetime.strptime(freeze_infos["freeze_date"], "%Y-%m-%d")
        freeze_delta = datetime.now().date() - freeze_date.date()
        new_freeze_duration = (
            freeze_infos["previous_freeze_duration"] + freeze_delta.days
        )
        return new_freeze_duration
