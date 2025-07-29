# -*- coding: utf-8 -*-

from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing import z2
from zope.globalrequest import setRequest

from imio.schedule.events import zope_registration
from imio.schedule.events.zope_registration import (
    unsubscribe_task_configs_for_content_type,
)

import transaction

import unittest

import imio.schedule


class NakedPloneLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        self.loadZCML(package=imio.schedule, name="testing.zcml")
        # need to do this for archetypes products having 'initialize'
        # method for their content types in their __init__.py
        z2.installProduct(app, "imio.dashboard")

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, "imio.dashboard")


NAKED_PLONE_FIXTURE = NakedPloneLayer(name="NAKED_PLONE_FIXTURE")

NAKED_PLONE_INTEGRATION = IntegrationTesting(
    bases=(NAKED_PLONE_FIXTURE,), name="NAKED_PLONE_INTEGRATION"
)


class ScheduleLayer(NakedPloneLayer):
    def setUpPloneSite(self, portal):
        setRequest(portal.REQUEST)
        applyProfile(portal, "Products.CMFPlone:plone")
        applyProfile(portal, "imio.schedule:default")

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ["Manager"])
        login(portal, TEST_USER_NAME)

        # Commit so that the test browser sees these objects
        transaction.commit()
        setRequest(portal.REQUEST)


TEST_INSTALL_FIXTURE = ScheduleLayer(name="TEST_INSTALL_FIXTURE")

TEST_INSTALL_INTEGRATION = IntegrationTesting(
    bases=(TEST_INSTALL_FIXTURE,), name="TEST_INSTALL_INTEGRATION"
)


TEST_INSTALL_FUNCTIONAL = FunctionalTesting(
    bases=(TEST_INSTALL_FIXTURE,), name="TEST_INSTALL_FUNCTIONAL"
)


class ExampleScheduleLayer(ScheduleLayer):
    def setUpPloneSite(self, portal):
        setRequest(portal.REQUEST)
        super(ExampleScheduleLayer, self).setUpPloneSite(portal)

        applyProfile(portal, "imio.schedule:testing")

        # delete macro tasks
        api.content.delete(portal.config.test_scheduleconfig.test_macrotaskconfig)
        api.content.delete(portal.test_taskcontainer.TASK_test_macrotaskconfig)
        setRequest(portal.REQUEST)


EXAMPLE_SCHEDULE_FIXTURE = ExampleScheduleLayer(name="EXAMPLE_SCHEDULE_FIXTURE")

EXAMPLE_SCHEDULE_INTEGRATION = IntegrationTesting(
    bases=(EXAMPLE_SCHEDULE_FIXTURE,), name="EXAMPLE_SCHEDULE_INTEGRATION"
)


EXAMPLE_SCHEDULE_FUNCTIONAL = FunctionalTesting(
    bases=(EXAMPLE_SCHEDULE_FIXTURE,), name="EXAMPLE_SCHEDULE_FUNCTIONAL"
)


class BaseTest(unittest.TestCase):
    """
    Helper class for tests.
    """

    def setUp(self):
        self.portal = self.layer["portal"]


class BrowserTest(BaseTest):
    """
    Helper class for Browser tests.
    """

    def setUp(self):
        super(BrowserTest, self).setUp()
        self.browser = z2.Browser(self.portal)
        self.browser.handleErrors = False

    def browser_login(self, user, password):
        login(self.portal, user)
        self.browser.open(self.portal.absolute_url() + "/logout")
        self.browser.open(self.portal.absolute_url() + "/login_form")
        self.browser.getControl(name="__ac_name").value = user
        self.browser.getControl(name="__ac_password").value = password
        self.browser.getControl(name="submit").click()


class ExampleScheduleTestBase(BrowserTest):
    def setUp(self):
        super(ExampleScheduleTestBase, self).setUp()
        setRequest(self.portal.REQUEST)

        # only keep simple tasks
        self.schedule_config = self.portal.config.test_scheduleconfig
        self.empty_schedule_config = self.portal.config.empty_scheduleconfig
        self.task_config = self.schedule_config.test_taskconfig
        self.empty_task_container = self.portal.test_empty_taskcontainer
        self.task_container = self.portal.test_taskcontainer
        self.task = self.task_container.TASK_test_taskconfig

        # commit to save the setup in the tests.
        transaction.commit()

        self.browser_login(TEST_USER_NAME, TEST_USER_PASSWORD)
        setRequest(self.portal.REQUEST)


class ExampleScheduleIntegrationTestCase(ExampleScheduleTestBase):

    layer = EXAMPLE_SCHEDULE_INTEGRATION


class ExampleScheduleFunctionalTestCase(ExampleScheduleTestBase):

    layer = EXAMPLE_SCHEDULE_FUNCTIONAL

    def tearDown(self):
        """
        Unregister the adapters here since the zope instance never shut downs.
        """
        setRequest(self.portal.REQUEST)
        unsubscribe_task_configs_for_content_type(self.task_config, None)

        api.content.delete(self.task_container)
        api.content.delete(self.empty_task_container)
        api.content.delete(self.portal.config)
        zope_registration._registered_sites = set([])

        transaction.commit()

        super(ExampleScheduleTestBase, self).tearDown()
        setRequest(self.portal.REQUEST)


class MacrotaskScheduleLayer(ScheduleLayer):
    def setUpPloneSite(self, portal):
        setRequest(portal.REQUEST)
        super(MacrotaskScheduleLayer, self).setUpPloneSite(portal)

        applyProfile(portal, "Products.CMFPlone:dependencies")
        # ponr skin for robot tests
        applyProfile(portal, "plonetheme.sunburst:default")
        applyProfile(portal, "imio.schedule:testing")

        # delete simple tasks
        api.content.delete(portal.config.test_scheduleconfig.test_taskconfig)
        api.content.delete(portal.test_taskcontainer.TASK_test_taskconfig)
        setRequest(portal.REQUEST)


MACROTASK_SCHEDULE_FIXTURE = MacrotaskScheduleLayer(name="MACROTASK_SCHEDULE_FIXTURE")

MACROTASK_SCHEDULE_INTEGRATION = IntegrationTesting(
    bases=(MACROTASK_SCHEDULE_FIXTURE,), name="MACROTASK_SCHEDULE_INTEGRATION"
)


MACROTASK_SCHEDULE_FUNCTIONAL = FunctionalTesting(
    bases=(MACROTASK_SCHEDULE_FIXTURE,), name="MACROTASK_SCHEDULE_FUNCTIONAL"
)


class MacroTaskScheduleTestBase(BrowserTest):
    def setUp(self):
        super(MacroTaskScheduleTestBase, self).setUp()
        setRequest(self.portal.REQUEST)

        # recreate test objects
        self.portal.portal_workflow.setDefaultChain("simple_publication_workflow")

        # only keep macro tasks
        self.schedule_config = self.portal.config.test_scheduleconfig
        self.macrotask_config = self.schedule_config.test_macrotaskconfig
        self.subtask_config = self.macrotask_config.test_subtaskconfig
        self.empty_task_container = self.portal.test_empty_taskcontainer
        self.task_container = self.portal.test_taskcontainer
        self.macro_task = self.task_container.TASK_test_macrotaskconfig
        self.sub_task = self.macro_task.TASK_test_subtaskconfig

        # commit to save the setup in the tests.
        transaction.commit()

        self.browser_login(TEST_USER_NAME, TEST_USER_PASSWORD)
        setRequest(self.portal.REQUEST)


class MacroTaskScheduleIntegrationTestCase(MacroTaskScheduleTestBase):

    layer = MACROTASK_SCHEDULE_INTEGRATION


class MacroTaskScheduleFunctionalTestCase(MacroTaskScheduleTestBase):

    layer = MACROTASK_SCHEDULE_FUNCTIONAL

    def tearDown(self):
        """
        Unregister the adapters here since the zope instance never shut downs.
        """
        setRequest(self.portal.REQUEST)
        unsubscribe_task_configs_for_content_type(self.macrotask_config, None)
        unsubscribe_task_configs_for_content_type(self.subtask_config, None)

        api.content.delete(self.task_container)
        api.content.delete(self.empty_task_container)
        api.content.delete(self.portal.config)

        transaction.commit()

        super(MacroTaskScheduleTestBase, self).tearDown()
