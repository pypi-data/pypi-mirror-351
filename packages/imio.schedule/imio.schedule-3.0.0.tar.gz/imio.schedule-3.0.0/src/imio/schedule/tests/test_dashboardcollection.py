# -*- coding: utf-8 -*-

from imio.schedule.testing import ExampleScheduleFunctionalTestCase

from plone import api

from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestDashboardCollectionFunctional(ExampleScheduleFunctionalTestCase):
    """ """

    def test_update_title(self):
        """
        DashboardCollection title should always be the same as the parent task.
        """
        task_config = self.task_config
        collection = self.task_config.dashboard_collection
        self.assertEquals(task_config.title, collection.title)

        task_config.title = "my new title"
        notify(ObjectModifiedEvent(task_config))
        self.assertEquals(task_config.title, collection.title)

        msg = "collection title should be reindexed when updated"
        catalog = api.portal.get_tool("portal_catalog")
        brains = catalog(portal_type="DashboardCollection", Title=task_config.title)
        self.assertEquals(len(brains), 1, msg)
