# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from imio.schedule.config import CREATION
from imio.schedule.interfaces import ScheduleConfigNotFound
from imio.schedule.interfaces import TaskConfigNotFound
from imio.schedule.testing import ExampleScheduleFunctionalTestCase
from imio.schedule.testing import ExampleScheduleIntegrationTestCase
from imio.schedule.testing import MacroTaskScheduleIntegrationTestCase
from imio.schedule.testing import TEST_INSTALL_INTEGRATION

from plone import api

import unittest
import transaction


class TestAutomatedTask(unittest.TestCase):
    """
    Test AutomatedTask content type.
    """

    layer = TEST_INSTALL_INTEGRATION

    def test_AutomatedTask_portal_type_is_registered(self):
        portal_types = api.portal.get_tool("portal_types")
        registered_types = portal_types.listContentTypes()
        self.assertTrue("AutomatedTask" in registered_types)


class TestAutomatedTaskFields(ExampleScheduleIntegrationTestCase):
    """
    Test schema fields declaration.
    """

    def test_class_registration(self):
        """
        Check if the class of the content type AutomatedTask is the
        correct one.
        """
        from imio.schedule.content.task import AutomatedTask

        self.assertTrue(self.task.__class__ == AutomatedTask)

    def test_schema_registration(self):
        """
        Check if the schema Interface of the content type AutomatedTask is the
        correct one.
        """
        portal_types = api.portal.get_tool("portal_types")
        taskconfig_type = portal_types.get(self.task.portal_type)
        self.assertTrue("IAutomatedTask" in taskconfig_type.schema)


class TestAutomatedTaskIntegration(ExampleScheduleFunctionalTestCase):
    """
    Test AutomatedTask methods.
    """

    def test_get_container(self):
        """
        Should return the task container of the task.
        """
        task_container = self.task.get_container()
        expected_container = self.task_container
        self.assertEquals(task_container, expected_container)

    def test_get_schedule_config(self):
        """
        Should return the schedule config of the task.
        """
        task = self.task

        schedule_config = task.get_schedule_config()
        expected_config = self.schedule_config
        self.assertEquals(schedule_config, expected_config)

        api.content.delete(self.schedule_config)
        with self.assertRaises(ScheduleConfigNotFound):
            task.get_schedule_config()

    def test_get_task_config(self):
        """
        Should return the associated TaskConfig.
        """
        task = self.task

        config = task.get_task_config()
        expected_config = self.task_config
        self.assertEquals(config, expected_config)

        api.content.delete(self.task_config)
        task.id = "{0}_test".format(task.id)  # This reset the cache
        with self.assertRaises(TaskConfigNotFound):
            task.get_task_config()

    def test_get_status(self):
        """
        Should return CREATION, STARTED or DONE depending
        on the task workflow state.
        """
        task = self.task
        expected_status = CREATION
        self.assertEquals(task.get_status(), expected_status)

    def test_start_conditions_status(self):
        """
        Check that the implementation is delegated to the
        'start_conditions_status' method of the task config.
        """
        task_config = self.task_config
        task_container = self.task_container
        task = self.task

        expected_status = task_config.start_conditions_status(task_container, task)
        status = task.start_conditions_status()

        msg = "implementation should just call the method 'start_conditions_status' from the task config"
        self.assertTrue(expected_status == status, msg)

    def test_starting_states_status(self):
        """
        Should return the following tuple:
        (task_container state, [starting states of the task])
        """
        task_config = self.task_config
        task_container = self.task_container
        task = self.task

        task_container_state, starting_states = task.starting_states_status()
        self.assertEquals(task_container_state, api.content.get_state(task_container))
        self.assertEquals(starting_states, task_config.starting_states)

    def test_end_conditions_status(self):
        """
        Check that the implementation is delegated to the
        'end_conditions_status' method of the task config.
        """
        task_config = self.task_config
        task_container = self.task_container
        task = self.task

        expected_status = task_config.end_conditions_status(task_container, task)
        status = task.end_conditions_status()

        msg = "implementation should just call the method 'end_conditions_status' from the task config"
        self.assertTrue(expected_status == status, msg)

    def test_ending_states_status(self):
        """
        Should return the following tuple:
        (task_container state, [ending states of the task])
        """
        task_config = self.task_config
        task_container = self.task_container
        task = self.task

        task_container_state, ending_states = task.ending_states_status()
        self.assertEquals(task_container_state, api.content.get_state(task_container))
        self.assertEquals(ending_states, task_config.ending_states)

    def test_get_state(self):
        """
        Should return the current workflow state of the task.
        """
        task = self.task
        self.assertEquals(task.get_state(), api.content.get_state(task))

    def test_get_subtasks(self):
        """
        Should return an empty list since a basic task has no subtasks.
        """
        task = self.task
        self.assertEquals(task.get_subtasks(), [])

    def test_end_date(self):
        """
        Should return the date of the ending of the task.
        """
        task = self.task
        task_config = self.task_config

        self.assertEquals(task.end_date, None)

        task_config.start_task(task)
        self.assertEquals(task.end_date, None)

        task_config.end_task(task)
        end_date = task.end_date
        expected_date = datetime.now(end_date.tzinfo)
        self.assertTrue(relativedelta(expected_date, end_date).seconds < 1)

    def test_start(self):
        """
        Should start a task.
        """
        task = self.task
        msg = "task should not be started yet (for the sake of the test..)"
        self.assertEquals(api.content.get_state(task), "created", msg)
        task._start()
        msg = "task should have been started"
        self.assertEquals(api.content.get_state(task), "to_do", msg)

    def test_end(self):
        """
        Should end a task.
        """
        task = self.task
        msg = "task should not be ended yet (for the sake of the test..)"
        self.assertEquals(api.content.get_state(task), "created", msg)
        task._end()
        msg = "task should have been ended"
        self.assertEquals(api.content.get_state(task), "closed", msg)

    def test_freeze(self):
        """
        Should freeze a task.
        """
        task = self.task
        msg = "task should not be frozen yet (for the sake of the test..)"
        self.assertEquals(api.content.get_state(task), "created", msg)
        task._freeze()
        msg = "task should have been frozen"
        self.assertEquals(api.content.get_state(task), "frozen", msg)

    def test_thaw(self):
        """
        Should thaw a task.
        """
        task = self.task
        msg = "task should be in created state"
        self.assertEquals(api.content.get_state(task), "created", msg)
        # freeze task befor thaw tests
        task._freeze()
        msg = "task should not be thawed yet (for the sake of the test..)"
        self.assertEquals(api.content.get_state(task), "frozen", msg)

        task._thaw()

        msg = "task should have been thawed and put back in its original state"
        self.assertEquals(api.content.get_state(task), "created", msg)


class TestAutomatedMacroTask(unittest.TestCase):
    """
    Test AutomatedMacroTask content type.
    """

    layer = TEST_INSTALL_INTEGRATION

    def test_AutomatedMacroTask_portal_type_is_registered(self):
        portal_types = api.portal.get_tool("portal_types")
        registered_types = portal_types.listContentTypes()
        self.assertTrue("AutomatedMacroTask" in registered_types)


class TestAutomatedMacroTaskFields(MacroTaskScheduleIntegrationTestCase):
    """
    Test schema fields declaration.
    """

    def test_class_registration(self):
        """
        Check if the class of the content type AutomatedMacroTask is the
        correct one.
        """
        from imio.schedule.content.task import AutomatedMacroTask

        self.assertTrue(self.macro_task.__class__ == AutomatedMacroTask)

    def test_schema_registration(self):
        """
        Check if the schema Interface of the content type AutomatedMacroTask is the
        correct one.
        """
        portal_types = api.portal.get_tool("portal_types")
        taskconfig_type = portal_types.get(self.macro_task.portal_type)
        self.assertTrue("IAutomatedTask" in taskconfig_type.schema)


class TestAutomatedMacroTaskIntegration(MacroTaskScheduleIntegrationTestCase):
    """
    Test AutomatedMacroTask methods.
    """

    def test_get_container(self):
        """
        Should return the task container of the task.
        """
        task_container = self.sub_task.get_container()
        expected_container = self.task_container
        self.assertEquals(task_container, expected_container)

    def test_get_task_config(self):
        """
        Should return the associated MacroTaskConfig.
        """
        config = self.macro_task.get_task_config()
        expected_config = self.macrotask_config
        self.assertEquals(config, expected_config)

    def test_get_subtasks(self):
        """
        Should return the subtasks of this macro task.
        """
        subtasks = self.macro_task.get_subtasks()
        self.assertEquals(len(subtasks), 1)
        self.assertEquals(subtasks[0], self.sub_task)

    def test_get_last_subtasks(self):
        """
        Should return the unique subtasks of this macro task.
        """
        subtasks = self.macro_task.get_subtasks()
        self.assertEquals(len(subtasks), 1)
        self.assertEquals(subtasks[0], self.sub_task)
