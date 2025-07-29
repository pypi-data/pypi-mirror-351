# -*- coding: utf-8 -*-

from plone import api
from plone.registry import Record
from plone.registry import field
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import alsoProvides


def upgrade_2_fix_schedule_collection(context):
    from collective.eeafaceted.collectionwidget.interfaces import IDashboardCollection
    from imio.schedule.interfaces import IScheduleCollection

    brains = api.content.find(
        object_provides=IDashboardCollection.__identifier__,
        id="dashboard_collection",
    )
    for brain in brains:
        if "schedule" not in brain.getPath():
            continue
        collection = brain.getObject()
        alsoProvides(collection, IScheduleCollection)


def upgrade_3_set_showNumberOfItems(context):
    from collective.eeafaceted.collectionwidget.interfaces import IDashboardCollection

    brains = api.content.find(
        object_provides=IDashboardCollection.__identifier__,
        id="dashboard_collection",
    )
    for brain in brains:
        if "schedule" not in brain.getPath():
            continue
        collection = brain.getObject()
        collection.showNumberOfItems = True


def upgrade_4_add_due_date_reminders(context):
    from imio.schedule.interfaces import IDueDateSettings

    setup_tool = api.portal.get_tool("portal_setup")
    registry = getUtility(IRegistry)

    default_values = {
        "color_orange_x_days_before_due_date": 10,
        "color_red_x_days_before_due_date": 5,
    }

    base = "imio.schedule.interfaces.IDueDateSettings"
    for key, default_value in default_values.items():
        full_key = "{0}.{1}".format(base, key)
        if full_key not in registry.records:
            registry_field = field.Int(
                title=IDueDateSettings[key].title, required=False, min=0
            )
            registry_record = Record(registry_field)
            registry_record.value = default_value
            registry.records[full_key] = registry_record
