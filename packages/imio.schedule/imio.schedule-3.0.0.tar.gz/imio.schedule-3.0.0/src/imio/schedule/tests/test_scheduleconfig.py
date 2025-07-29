# -*- coding: utf-8 -*-

from Acquisition import aq_base

from imio.schedule.testing import ExampleScheduleIntegrationTestCase
from imio.schedule.testing import TEST_INSTALL_INTEGRATION

from plone import api

import unittest


class TestScheduleConfig(unittest.TestCase):
    """
    Test ScheduleConfig content type.
    """

    layer = TEST_INSTALL_INTEGRATION

    def test_ScheduleConfig_portal_type_is_registered(self):
        portal_types = api.portal.get_tool("portal_types")
        registered_types = portal_types.listContentTypes()
        self.assertTrue("ScheduleConfig" in registered_types)


class TestScheduleConfigFields(ExampleScheduleIntegrationTestCase):
    """
    Test schema fields declaration.
    """

    def test_class_registration(self):
        """
        Check if the class of the content type ScheduleConfig is the
        correct one.
        """
        from imio.schedule.content.schedule_config import ScheduleConfig

        self.assertTrue(self.schedule_config.__class__ == ScheduleConfig)

    def test_schema_registration(self):
        """
        Check if the schema Interface of the content type ScheduleConfig is the
        correct one.
        """
        portal_types = api.portal.get_tool("portal_types")
        scheduleconfig_type = portal_types.get(self.schedule_config.portal_type)
        self.assertTrue("IScheduleConfig" in scheduleconfig_type.schema)

    def test_enabled_attribute(self):
        task_config = aq_base(self.task_config)
        self.assertTrue(hasattr(task_config, "enabled"))

    def test_enabled_field_display(self):
        self.browser.open(self.task_config.absolute_url())
        contents = self.browser.contents
        msg = "field 'enabled' is not displayed"
        self.assertTrue('id="form-widgets-enabled"' in contents, msg)
        msg = "field 'enabled' is not translated"
        self.assertTrue("Activé" in contents, msg)

    def test_enabled_field_edit(self):
        self.browser.open(self.task_config.absolute_url() + "/edit")
        contents = self.browser.contents
        msg = "field 'enabled' is not editable"
        self.assertTrue("Activé" in contents, msg)

    def test_scheduled_contenttype_attribute(self):
        schedule_config = aq_base(self.schedule_config)
        self.assertTrue(hasattr(schedule_config, "scheduled_contenttype"))

    def test_scheduled_contenttype_field_display(self):
        self.browser.open(self.schedule_config.absolute_url())
        contents = self.browser.contents
        msg = "field 'scheduled_contenttype' is not displayed"
        self.assertTrue('id="form-widgets-scheduled_contenttype"' in contents, msg)
        msg = "field 'scheduled_contenttype' is not translated"
        self.assertTrue("Type de contenu associé" in contents, msg)

    def test_scheduled_contenttype_field_edit(self):
        self.browser.open(self.schedule_config.absolute_url() + "/edit")
        contents = self.browser.contents
        msg = "field 'scheduled_contenttype' is not editable"
        self.assertTrue("Type de contenu associé" in contents, msg)


class TestScheduleConfigIntegration(ExampleScheduleIntegrationTestCase):
    """
    Test ScheduleConfig methods.
    """

    def test_get_all_task_configs(self):
        """
        Should return all TaskConfig contained in the ScheduleConfig.
        """
        expected_taskconfigs = [self.task_config]
        task_configs = self.schedule_config.get_all_task_configs()
        msg = "expected {} but got {}".format(expected_taskconfigs, task_configs)
        self.assertTrue(task_configs == expected_taskconfigs, msg)

    def test_get_scheduled_portal_type(self):
        """
        Should return the portal_type of the content type selected on the field
        'scheduled_contenttype'.
        """
        portal_type = self.schedule_config.get_scheduled_portal_type()
        expected_type = "Folder"
        msg = "expected {} but got {}".format(expected_type, portal_type)
        self.assertTrue(portal_type == expected_type, msg)

    def test_get_scheduled_interfaces(self):
        """
        Should return the Interface (or a class) of the content type selected
        on the field 'scheduled_contenttype'.
        """
        from Products.ATContentTypes.interfaces import IATFolder

        type_interface = self.schedule_config.get_scheduled_interfaces()
        expected_interface = (IATFolder,)
        msg = "expected {} but got {}".format(expected_interface, type_interface)
        self.assertTrue(type_interface == expected_interface, msg)

    def test_is_empty(self):
        """
        Should return True if the schedule_config has no TaskConfig.
        """
        self.assertTrue(not self.schedule_config.is_empty())
        self.assertTrue(self.empty_schedule_config.is_empty())
