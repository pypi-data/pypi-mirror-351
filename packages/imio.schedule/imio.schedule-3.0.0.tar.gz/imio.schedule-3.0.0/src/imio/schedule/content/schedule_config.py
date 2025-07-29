# -*-coding: utf-8 -*-

from plone import api
from plone.dexterity.content import Container
from plone.supermodel import model

from imio.schedule import _
from imio.schedule.content.task_config import ITaskConfig
from imio.schedule.utils import tuple_to_interface

from plone.memoize.request import cache

from zope import schema
from zope.interface import implements


class IScheduleConfig(model.Schema):
    """
    ScheduleConfig dexterity schema.
    """

    enabled = schema.Bool(
        title=_(u"Enabled"),
        default=True,
        required=False,
    )

    scheduled_contenttype = schema.Choice(
        title=_(u"Scheduled content type"),
        description=_(u"Select the content type to apply schedule."),
        vocabulary="schedule.scheduled_contenttype",
        required=True,
    )


class ScheduleConfig(Container):
    """
    ScheduleConfig dexterity class.
    """

    implements(IScheduleConfig)

    def level(self):
        """
        Return depth contenance level.
        """
        return 0

    def query_task_configs(self, query={}):
        """
        Query the TaskConfig of this ScheduleConfig.
        """
        catalog = api.portal.get_tool("portal_catalog")
        config_path = "/".join(self.getPhysicalPath())

        base_query = {
            "object_provides": ITaskConfig.__identifier__,
            "path": {"query": config_path},
            "sort_on": "getObjPositionInParent",
        }

        base_query.update(query)

        config_brains = catalog(**base_query)

        return config_brains

    @cache(get_key=lambda m, schedule_cfg: schedule_cfg.id, get_request="self.REQUEST")
    def get_all_task_configs(self):
        """
        Return all the TaskConfig of this ScheduleConfig.
        """
        config_brains = self.query_task_configs()
        with api.env.adopt_roles(["Manager"]):
            task_configs = [brain.getObject() for brain in config_brains]

        return task_configs

    def get_scheduled_portal_type(self):
        """
        Return the portal_type of the selected scheduled_contenttype.
        """
        return self.scheduled_contenttype and self.scheduled_contenttype[0] or ""

    def get_scheduled_interfaces(self):
        """
        Return the registration interface of the selected scheduled_contenttype.
        """
        portal_type, interface_tuples = self.scheduled_contenttype
        if type(interface_tuples[0]) not in [list, tuple]:
            interface_tuples = (interface_tuples,)
        interfaces = tuple([tuple_to_interface(i) for i in interface_tuples])

        return interfaces

    def is_empty(self):
        """
        Tells if the schedule config has no task configs.
        """
        return len(self.objectIds()) <= 1
