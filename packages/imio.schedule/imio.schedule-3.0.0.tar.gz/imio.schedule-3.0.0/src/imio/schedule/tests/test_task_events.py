# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from imio.schedule.content.delay import CalculationDefaultDelay
from imio.schedule.content.task import IAutomatedTask
from imio.schedule.testing import ExampleScheduleFunctionalTestCase
from imio.schedule.testing import MacroTaskScheduleFunctionalTestCase

from mock import Mock

from plone import api

from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.globalrequest import setRequest


class TestTaskCreation(ExampleScheduleFunctionalTestCase):
    """
    Test task creation with different changes of TaskContainer.
    """

    def setUp(self):
        super(TestTaskCreation, self).setUp()
        self._adapter_computed_due_date = CalculationDefaultDelay.compute_due_date
        setRequest(self.portal.REQUEST)

    def tearDown(self):
        CalculationDefaultDelay.compute_due_date = self._adapter_computed_due_date
        super(TestTaskCreation, self).tearDown()

    def test_task_creation_on_container_modification(self):
        """
        When modifying a contentype scheduled with a ScheduleConfig
        Task should created automatically depending on start conditions
        and starting_states.
        """
        empty_task_container = self.empty_task_container
        msg = "so far, no task should have been created"
        self.assertEquals(len(empty_task_container.objectValues()), 0, msg)

        # simulate modification
        notify(ObjectModifiedEvent(empty_task_container))

        created = empty_task_container.objectValues()
        created = created and created[0]

        # a task should have been created
        msg = "A task should have been created"
        self.assertTrue(created, msg)

        msg = "The object created should have been a Task but is {}".format(
            created.portal_type
        )
        self.assertTrue(IAutomatedTask.providedBy(created), msg)

    def test_task_creation_on_container_workflow_modification(self):
        """
        When changing state of a contentype scheduled with a ScheduleConfig
        Task should created automatically depending on start conditions
        and starting_states.
        """
        empty_task_container = self.empty_task_container
        msg = "so far, no task should have been created"
        self.assertEquals(len(empty_task_container.objectValues()), 0, msg)

        # do workflow change
        api.content.transition(empty_task_container, transition="submit")
        api.content.transition(empty_task_container, transition="retract")

        created = empty_task_container.objectValues()
        created = created and created[0]

        # a task should have been created
        msg = "A task should have been created"
        self.assertTrue(created, msg)

        msg = "The object created should have been a Task but is {}".format(
            created.portal_type
        )
        self.assertTrue(IAutomatedTask.providedBy(created), msg)

    def test_task_creation_on_container_creation(self):
        """
        When creating a contentype scheduled with a ScheduleConfig
        Task should created automatically depending on start conditions
        and starting_states.
        """
        new_task_container = api.content.create(
            type="Folder", id="new_task_container", container=self.portal
        )

        created = new_task_container.objectValues()
        created = created and created[0]

        # a task should have been created
        msg = "A task should have been created"
        self.assertTrue(created, msg)

        msg = "The object created should have been a Task but is {}".format(
            created.portal_type
        )
        self.assertTrue(IAutomatedTask.providedBy(created), msg)

    def test_assigned_user_is_set_on_created_task(self):
        """
        Check that the assigned user is set on an
        automatically created task.
        """
        msg = "default assigned user should have been admin"
        self.assertEquals(self.task.assigned_user, "admin", msg)

    def test_due_date_is_set_on_created_task(self):
        """
        Check that the computed due date is set on an
        automatically created task.
        """
        msg = "default du date should have been today + 10 days"
        due_date = self.task.due_date
        expected_date = self.task_container.creation_date
        delay = relativedelta(days=self.task_config.additional_delay)
        expected_date = expected_date.asdatetime().date() + delay
        self.assertEquals(due_date, expected_date, msg)

    def test_schedule_config_UID_is_set_on_created_task(self):
        """
        Check that schedule_config_UID attribute is set on an
        automatically created task.
        """
        task = self.task
        schedule_config = self.schedule_config
        msg = "schedule_config_UID attribute should have been set"
        self.assertEquals(task.schedule_config_UID, schedule_config.UID(), msg)

    def test_task_config_UID_is_set_on_created_task(self):
        """
        Check that task_config_UID attribute is set on an
        automatically created task.
        """
        task = self.task
        task_config = self.task_config
        msg = "task_config_UID attribute should have been set"
        self.assertEquals(task.task_config_UID, task_config.UID(), msg)


class TestTaskStarting(ExampleScheduleFunctionalTestCase):
    """
    Test task starting with different changes of TaskContainer.
    """

    def test_task_starting_on_container_modification(self):
        """
        When modifying a contentype scheduled with a ScheduleConfig
        Task should started automatically depending on start conditions
        and starting_states.
        """
        task_container = self.task_container
        task = self.task

        # put the task container on 'pending' state to match 'starting states'
        api.content.transition(task_container, transition="submit")
        # reopen the task to be sure it was not closed before the container
        # modification
        if api.content.get_state(task) == "to_do":
            api.content.transition(task, "back_in_to_assign")
        msg = "The task should not be started yet ! (for the sake of the test)"
        self.assertNotEquals(api.content.get_state(task), "to_do", msg)

        # simulate modification
        notify(ObjectModifiedEvent(task_container))

        # the task should have been started
        msg = "The task should have been started"
        self.assertEquals(api.content.get_state(task), "to_do", msg)

    def test_task_starting_on_container_workflow_modification(self):
        """
        When changing state a contentype scheduled with a ScheduleConfig
        Task should started automatically depending on start conditions
        and starting_states.
        """
        task_container = self.task_container
        task = self.task

        msg = "The task should not be closed yet ! (for the sake of the test)"
        self.assertNotEquals(api.content.get_state(task), "to_do", msg)

        # do workflow change
        api.content.transition(task_container, transition="submit")

        # the task should have been started
        msg = "The task should have been started"
        self.assertEquals(api.content.get_state(task), "to_do", msg)


class TestTaskUpdate(ExampleScheduleFunctionalTestCase):
    """
    Test task update with different changes of TaskContainer.
    """

    def test_update_due_date_on_container_modification(self):
        """
        When modifying a contentype scheduled with a ScheduleConfig
        Task due date should be updated.
        """
        task_container = self.task_container
        task = self.task
        old_due_date = task.due_date

        # set an additional delay of 42 days on the task config
        CalculationDefaultDelay.calculate_delay = Mock(return_value=42)
        msg = "The task due date should not have changed"
        self.assertEquals(task.due_date, old_due_date)

        # simulate modification
        notify(ObjectModifiedEvent(task_container))

        msg = "The task due date should have been updated"
        self.assertNotEquals(task.due_date, old_due_date, msg)

    def test_reindex_due_date_on_container_modification(self):
        """
        When modifying a contentype scheduled with a ScheduleConfig
        Task due date should be updated and reindexed.
        """
        task_container = self.task_container
        task = self.task
        old_due_date = task.due_date

        # set an additional delay of 42 days on the task config
        CalculationDefaultDelay.calculate_delay = Mock(return_value=42)
        msg = "The task due date should not have changed"
        self.assertEquals(task.due_date, old_due_date)

        # simulate modification
        notify(ObjectModifiedEvent(task_container))

        catalog = api.portal.get_tool("portal_catalog")
        msg = "catalog should not find anything with old due date"
        task_brain = catalog(due_date=old_due_date, UID=task.UID())
        self.assertFalse(task_brain, msg)
        msg = "new due date should have been reindexed"
        task_brain = catalog(due_date=task.due_date, UID=task.UID())
        self.assertTrue(task_brain, msg)


class TestMacroTaskUpdate(MacroTaskScheduleFunctionalTestCase):
    """
    Test task update with different changes of TaskContainer.
    """

    def tearDown(self):
        api.content.transition(obj=self.macro_task, to_state="created")

    def test_update_recurrence_handler(self):
        """
        When modifying a contenttype the recurrence should be evaluated
        """
        transitions = ["do_to_assign", "do_realized", "do_closed"]
        self.macrotask_config.activate_recurrency = True
        self.macrotask_config.recurrence_conditions = (
            self.macrotask_config.creation_conditions
        )
        self.macrotask_config.recurrence_states = ("private",)

        self.subtask_config.activate_recurrency = True
        self.subtask_config.recurrence_conditions = (
            self.subtask_config.creation_conditions
        )
        self.subtask_config.recurrence_states = ("private",)

        for transition in transitions:
            api.content.transition(obj=self.macro_task, transition=transition)
        notify(ObjectModifiedEvent(self.task_container))

        self.assertTrue("TASK_test_macrotaskconfig-1" in self.task_container)
        macro_task = self.task_container["TASK_test_macrotaskconfig-1"]
        self.assertTrue("TASK_test_subtaskconfig" in macro_task)
        for transition in transitions:
            api.content.transition(obj=macro_task, transition=transition)


class TestTaskEnding(ExampleScheduleFunctionalTestCase):
    """
    Test task ending with different changes of TaskContainer.
    """

    def test_task_ending_on_container_modification(self):
        """
        When modifying a contentype scheduled with a ScheduleConfig
        Task should ended automatically depending on end conditions
        and ending_states.
        """
        task_container = self.task_container
        task = self.task

        # put the task container on 'published' state to match 'ending states'
        api.content.transition(task_container, transition="publish")
        # reopen the task to be sure it was not closed before the container
        # modification
        if api.content.get_state(task) == "closed":
            api.content.transition(task, "back_in_realized")
        msg = "The task should not be closed yet ! (for the sake of the test)"
        self.assertNotEquals(api.content.get_state(task), "closed", msg)

        # simulate modification
        notify(ObjectModifiedEvent(task_container))

        # the task should have been ended
        msg = "The task should have been ended"
        self.assertEquals(api.content.get_state(task), "closed", msg)

    def test_task_ending_on_container_workflow_modification(self):
        """
        When changing state a contentype scheduled with a ScheduleConfig
        Task should ended automatically depending on end conditions
        and ending_states.
        """
        task_container = self.task_container
        task = self.task

        msg = "The task should not be closed yet ! (for the sake of the test)"
        self.assertNotEquals(api.content.get_state(task), "closed", msg)

        # do workflow change
        api.content.transition(task_container, transition="publish")

        # the task should have been ended
        msg = "The task should have been ended"
        self.assertEquals(api.content.get_state(task), "closed", msg)


class TestTaskFreezing(ExampleScheduleFunctionalTestCase):
    """
    Test task freezing with different changes of TaskContainer.
    """

    def test_task_freezing_on_container_modification(self):
        """
        When modifying a contentype scheduled with a ScheduleConfig
        Task should froze automatically depending on freeze conditions
        and freezing_states.
        """
        task_container = self.task_container
        task = self.task
        task_config = self.task_config
        task_config.ending_states = ["published"]
        task_config.freeze_states = ["private"]

        msg = "The task should not be closed or frozen yet ! (for the sake of the test)"
        self.assertNotEquals(task.get_state(), "closed", msg)
        self.assertNotEquals(task.get_state(), "frozen", msg)
        msg = "The task container should  be in private state"
        self.assertEquals(api.content.get_state(task_container), "private", msg)

        # simulate modification
        notify(ObjectModifiedEvent(task_container))

        # the task should have been frozen
        msg = "The task should have been frozen"
        self.assertEquals(api.content.get_state(task), "frozen", msg)

    def test_task_freezing_on_container_workflow_modification(self):
        """
        When changing state a contentype scheduled with a ScheduleConfig
        Task should froze automatically depending on freeze conditions
        and freezing_states.
        """
        task_container = self.task_container
        task = self.task
        task_config = self.task_config
        task_config.ending_states = ["private"]
        task_config.freeze_states = ["published"]

        msg = "The task should not be closed or frozen yet ! (for the sake of the test)"
        self.assertNotEquals(task.get_state(), "closed", msg)
        self.assertNotEquals(task.get_state(), "frozen", msg)

        # do workflow change
        api.content.transition(task_container, transition="publish")

        # the task should have been frozen
        msg = "The task should have been frozen"
        self.assertEquals(task.get_state(), "frozen", msg)


class TestTaskThawing(ExampleScheduleFunctionalTestCase):
    """
    Test task thawing with different changes of TaskContainer.
    """

    def test_task_thawing_on_container_modification(self):
        """
        When modifying a contentype scheduled with a ScheduleConfig
        Task should froze automatically depending on thaw conditions
        and thawing_states.
        """
        task_container = self.task_container
        task = self.task
        task_config = self.task_config
        task_config.ending_states = ["published"]
        task_config.thaw_states = ["private"]

        task_original_state = task.get_state()
        msg = "The task original state should not be frozen! (for the sake of the test)"
        self.assertNotEquals(task_original_state, "frozen", msg)
        msg = "The task container should  be in private state"
        self.assertEquals(api.content.get_state(task_container), "private", msg)

        # freeze task
        task_config.freeze_task(task)
        self.assertEquals(task.get_state(), "frozen", msg)
        # simulate modification
        notify(ObjectModifiedEvent(task_container))

        # the task should have been thawed
        msg = "The task should have been thawed"
        self.assertEquals(api.content.get_state(task), task_original_state, msg)

    def test_task_thawing_on_container_workflow_modification(self):
        """
        When changing state a contentype scheduled with a ScheduleConfig
        Task should froze automatically depending on thaw conditions
        and thawing_states.
        """
        task_container = self.task_container
        task = self.task
        task_config = self.task_config
        task_config.freeze_states = ["private"]
        task_config.thaw_states = ["published"]

        task_original_state = task.get_state()
        msg = "The task original state should not be frozen! (for the sake of the test)"
        self.assertNotEquals(task_original_state, "frozen", msg)

        # freeze task
        task_config.freeze_task(task)
        self.assertEquals(task.get_state(), "frozen", msg)
        # do workflow change
        api.content.transition(task_container, transition="publish")

        # the task should have been thawed
        msg = "The task should have been thawed"
        self.assertEquals(task.get_state(), task_original_state, msg)
