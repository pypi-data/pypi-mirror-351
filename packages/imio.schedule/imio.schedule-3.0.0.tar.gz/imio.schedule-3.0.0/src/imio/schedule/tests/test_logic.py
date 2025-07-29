# -*- coding: utf-8 -*-

from DateTime import DateTime

from imio.schedule.interfaces import IMacroTaskStartDate
from imio.schedule.interfaces import IStartDate
from imio.schedule.testing import ExampleScheduleIntegrationTestCase
from imio.schedule.testing import MacroTaskScheduleIntegrationTestCase

from zope.component import queryMultiAdapter
from zope.component import getMultiAdapter


class TestTaskLogicIntegration(ExampleScheduleIntegrationTestCase):
    """
    Test some logic for tasks.
    """

    def test_task_starting_date_registration(self):
        """
        Content types voc factory should be registered as a named utility.
        """
        logic_name = "schedule.start_date.task_starting_date"

        duedate_adapter = queryMultiAdapter(
            (self.task_container, self.task), IStartDate, name=logic_name
        )
        self.assertTrue(duedate_adapter)

    def test_task_starting_date_logic(self):
        """
        Check if the SubtaskHighestDueDate adapter return the highest
        due date amongst all the subtasks of a AutomatedMacroTask.
        """
        task_config = self.task_config
        task = self.task
        logic_name = "schedule.start_date.task_starting_date"

        duedate_adapter = getMultiAdapter(
            (self.task_container, task), IStartDate, name=logic_name
        )

        task_config.start_task(task)
        due_date = duedate_adapter.start_date()
        expected_date = task.workflow_history.values()[0][-1]["time"]
        self.assertEquals(due_date, expected_date)


class TestMacroTaskLogicIntegration(MacroTaskScheduleIntegrationTestCase):
    """
    Test MacroTaskConfig methods.
    """

    def test_subtask_highest_due_date_registration(self):
        """
        Content types voc factory should be registered as a named utility.
        """
        logic_name = "schedule.start_date.subtask_highest_due_date"

        duedate_adapter = queryMultiAdapter(
            (self.task_container, self.macro_task), IMacroTaskStartDate, name=logic_name
        )
        self.assertTrue(duedate_adapter)

    def test_subtask_highest_due_date_logic(self):
        """
        Check if the SubtaskHighestDueDate adapter return the highest
        due date amongst all the subtasks of a AutomatedMacroTask.
        """
        logic_name = "schedule.start_date.subtask_highest_due_date"

        duedate_adapter = getMultiAdapter(
            (self.task_container, self.macro_task), IMacroTaskStartDate, name=logic_name
        )

        highest_due_date = duedate_adapter.start_date()
        expected_date = DateTime(str(self.sub_task.due_date))
        self.assertEquals(highest_due_date, expected_date)
