# -*- coding: utf-8 -*-

from datetime import date

from imio.schedule.testing import ExampleScheduleIntegrationTestCase
from imio.schedule.config import CREATION, STARTED, DONE, status_by_state

from plone import api

from Products.ATContentTypes.interfaces import IATFolder


class TestUtils(ExampleScheduleIntegrationTestCase):
    """
    Test all methods of utils.py module.
    """

    def test_get_all_schedule_configs(self):
        """
        Test the method get_all_schedule_configs.
        """
        from imio.schedule.utils import get_all_schedule_configs

        self.assertEquals(
            [self.empty_schedule_config, self.schedule_config],
            get_all_schedule_configs(),
        )

    def test_get_task_configs(self):
        """
        Test the method get_task_configs.
        """
        from imio.schedule.utils import get_task_configs

        expected_UIDS = [
            task_config.UID()
            for task_config in self.schedule_config.get_all_task_configs()
        ]
        folder = self.portal.config
        task_configs = get_task_configs(folder)
        task_config_UIDS = [task_config.UID() for task_config in task_configs]
        self.assertEqual(set(task_config_UIDS), set(expected_UIDS))

    def test_get_container_open_tasks(self):
        """
        Test the method get_container_open_tasks.
        """
        from imio.schedule.utils import get_container_open_tasks

        task_state = api.content.get_state(self.task)
        self.assertTrue(status_by_state[task_state] in [CREATION, STARTED])
        expected = [self.task]
        open_tasks = get_container_open_tasks(self.task_container)
        self.assertEqual(expected, open_tasks)

    def test_end_all_open_tasks(self):
        """
        Test the method end_all_open_tasks.
        """
        from imio.schedule.utils import end_all_open_tasks

        open_tasks = end_all_open_tasks(self.task_container)
        end_all_open_tasks(self.task_container)
        for task in open_tasks:
            self.assertEqual(status_by_state[api.content.get_state(obj=task)], DONE)

    def test_tuple_to_interface(self):
        """
        Should turn a tuple ('interface.module.path', 'Interface') into
        Interface class.
        """
        from imio.schedule.utils import tuple_to_interface

        expected_interface = IATFolder
        interface_tuple = ("Products.ATContentTypes.interfaces.folder", "IATFolder")
        interface = tuple_to_interface(interface_tuple)
        self.assertEqual(interface, expected_interface)

    def test_interface_to_tuple(self):
        """
        Should turn an Interface class into a tuple:
        ('interface.module.path', 'Interface')
        """
        from imio.schedule.utils import interface_to_tuple

        expected_tuple = ("Products.ATContentTypes.interfaces.folder", "IATFolder")
        interface_tuple = interface_to_tuple(IATFolder)
        self.assertEqual(interface_tuple, expected_tuple)


def TestWorkingDaysCalendar(ExampleScheduleIntegrationTestCase):
    def test_is_working_day(self):
        from imio.schedule.utils import WorkingDaysCalendar

        calendar = WorkingDaysCalendar()
        # Basic holiday
        self.assertTrue(calendar.is_working_day(date(2017, 1, 1)))
        # Test holiday from CalendarExtraHolidays utility
        self.assertTrue(calendar.is_working_day(date(2017, 2, 1)))
