# -*- coding: utf-8 -*-

from collective.compoundcriterion.interfaces import ICompoundCriterionFilter

from plone import api

from imio.schedule.content.schedule_config import IScheduleConfig
from imio.schedule.content.task_config import ITaskConfig
from imio.schedule.interfaces import IToTaskConfig
from imio.schedule.interfaces import TaskConfigNotFound
from imio.schedule.utils import interface_to_tuple
from imio.schedule.utils import tuple_to_interface

from zope.component import getGlobalSiteManager
from zope.interface import Interface
from zope.interface import implements


import logging

logger = logging.getLogger("schedule")


def subscribe_task_configs_for_content_type(task_config, event):
    """
    Register adapter returning 'task_config' to the interface
    of the content_type selected in the field 'task_container'.
    """

    gsm = getGlobalSiteManager()
    task_config_UID = task_config.UID()

    class TaskConfigSubscriber(object):
        """ """

        implements(IToTaskConfig)

        def __init__(self, context):
            """ """
            self.context = context
            self.task_config_UID = task_config_UID

        @property
        def task_config(self):
            catalog = api.portal.get_tool("portal_catalog")
            brains = catalog.unrestrictedSearchResults(UID=self.task_config_UID)
            if brains:
                task_config = brains[0].getObject()
                return task_config
            else:
                raise TaskConfigNotFound("UID {}".format(self.task_config_UID))

    registration_interfaces = task_config.get_scheduled_interfaces()

    for registration_interface in registration_interfaces:
        gsm.registerAdapter(
            factory=TaskConfigSubscriber,
            required=(registration_interface,),
            provided=IToTaskConfig,
            name=task_config.UID(),
        )
        msg = "Registered IToTaskConfig adapter '{}' for {}".format(
            task_config.Title(), registration_interface
        )
        logger.info(msg)


def unsubscribe_task_configs_for_content_type(task_config, event):
    """
    Unregister adapter returning 'task_config' to the interface
    of the content_type selected in the field 'task_container'.
    """

    gsm = getGlobalSiteManager()
    schedule_config = task_config.get_schedule_config()

    previous_interfaces = getattr(schedule_config, "_scheduled_interface_", None)
    if previous_interfaces and type(previous_interfaces[0]) not in [list, tuple]:
        previous_interfaces = (previous_interfaces,)
    previous_interfaces = [tuple_to_interface(i) for i in previous_interfaces]

    for previous_interface in previous_interfaces:
        removed = gsm.unregisterAdapter(
            required=(previous_interface,),
            provided=IToTaskConfig,
            name=task_config.UID(),
        )
        if removed:
            msg = "Unregistered IToTaskConfig adapter '{}' for {}".format(
                task_config.Title(), previous_interface
            )
            logger.info(msg)


def update_task_configs_subscriptions(schedule_config, event):
    """
    When the scheduled_contenttype value of a ScheduleConfig is changed,
    we have to unregister all the adapters providing IToTaskConfig
    and register them again for the new selected content type.
    """

    previous_interfaces = getattr(schedule_config, "_scheduled_interface_", None)
    new_interfaces = schedule_config.get_scheduled_interfaces()
    new_interfaces = tuple([interface_to_tuple(i) for i in new_interfaces])

    # if there were no previous values, just save it and return
    if not previous_interfaces:
        setattr(schedule_config, "_scheduled_interface_", new_interfaces)
        return

    # if the value did not change, do nothing
    if previous_interfaces == new_interfaces:
        return

    for task_config in schedule_config.get_all_task_configs():
        # unregister the IToTaskConfig adapter for the previous interface
        unsubscribe_task_configs_for_content_type(task_config, event)
        # register the new IToTaskConfig adapter for the new interface
        subscribe_task_configs_for_content_type(task_config, event)

    # replace the _schedule_interface_ attribute with the new value
    setattr(schedule_config, "_scheduled_interface_", new_interfaces)


def register_schedule_collection_criterion(schedule_config, event):
    """
    Register adapter turning a schedule config into a collection
    criterion filtering all tasks from this schedule config.
    """

    gsm = getGlobalSiteManager()
    schedule_config_UID = schedule_config.UID()

    class FilterTasksCriterion(object):
        def __init__(self, context):
            self.context = context

        @property
        def query(self):
            return {"schedule_config_UID": {"query": schedule_config_UID}}

    gsm.registerAdapter(
        factory=FilterTasksCriterion,
        required=(Interface,),
        provided=ICompoundCriterionFilter,
        name=schedule_config.UID(),
    )
    msg = "Registered schedule CollectionCriterion adapter '{}'".format(
        schedule_config.Title()
    )
    logger.info(msg)


def unregister_schedule_collection_criterion(schedule_config, event):
    """
    Unregister adapter turning a schedule config into a collection
    criterion.
    """

    gsm = getGlobalSiteManager()

    removed = gsm.unregisterAdapter(
        required=(Interface,),
        provided=ICompoundCriterionFilter,
        name=schedule_config.UID(),
    )
    if removed:
        msg = "Unregistered schedule CollectionCriterion adapter '{}'".format(
            schedule_config.Title()
        )
        logger.info(msg)


def register_task_collection_criterion(task_config, event):
    """
    Register adapter turning a task config into a collection
    criterion filtering all tasks from this task config.
    """

    gsm = getGlobalSiteManager()
    task_config_UID = task_config.UID()

    class FilterTasksCriterion(object):
        def __init__(self, context):
            self.context = context

        @property
        def query(self):
            return {"task_config_UID": {"query": task_config_UID}}

    gsm.registerAdapter(
        factory=FilterTasksCriterion,
        required=(Interface,),
        provided=ICompoundCriterionFilter,
        name=task_config.UID(),
    )
    msg = "Registered task CollectionCriterion adapter '{}'".format(task_config.Title())
    logger.info(msg)


def unregister_task_collection_criterion(task_config, event):
    """
    Unregister adapter turning a task config into a collection
    criterion.
    """

    gsm = getGlobalSiteManager()

    removed = gsm.unregisterAdapter(
        required=(Interface,), provided=ICompoundCriterionFilter, name=task_config.UID()
    )
    if removed:
        msg = "Unregistered task CollectionCriterion adapter '{}'".format(
            task_config.Title()
        )
        logger.info(msg)


_registered_sites = set()


def register_at_instance_startup(site, event):
    """
    Re-register:
        - all the TaskConfig adapters
        - collections criterions
        - tasks vocabulary of each ScheduleConfig
    when zope instance is started.
    """
    if site.id not in _registered_sites:

        # register task configs subscribers and task configs criterion
        catalog = api.portal.get_tool("portal_catalog")
        task_brains = catalog.unrestrictedSearchResults(
            object_provides=ITaskConfig.__identifier__
        )
        all_task_configs = [
            site.unrestrictedTraverse(brain.getPath()) for brain in task_brains
        ]

        for task_config in all_task_configs:
            subscribe_task_configs_for_content_type(task_config, event)
            register_task_collection_criterion(task_config, event)

        # register schedule configs criterion and tasks vocabulary
        schedule_brains = catalog.unrestrictedSearchResults(
            object_provides=IScheduleConfig.__identifier__
        )
        all_schedule_configs = [
            site.unrestrictedTraverse(brain.getPath()) for brain in schedule_brains
        ]

        for schedule_config in all_schedule_configs:
            register_schedule_collection_criterion(schedule_config, event)

        _registered_sites.add(site.id)
