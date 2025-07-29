# -*- coding: utf-8 -*-

from imio.schedule.content.task import IAutomatedTask
from imio.schedule.content.task_config import ITaskConfig

from plone import api

from zope.component import getUtility
from zope.component.interface import getInterface
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from zope.schema.interfaces import IVocabularyFactory


def update_marker_interfaces(task_config, event):
    """
    When the 'marker_interfaces' field is updated, update the interface
    provided on all the tasks of this task config as well.
    """
    catalog = api.portal.get_tool("portal_catalog")

    vocname = ITaskConfig.get("marker_interfaces").value_type.vocabularyName
    interfaces_voc = getUtility(IVocabularyFactory, vocname)(task_config)
    marker_interfaces = dict(
        [(i, getInterface("", i)) for i in interfaces_voc.by_value]
    )

    task_brains = catalog(
        object_provides=IAutomatedTask.__identifier__, task_config_UID=task_config.UID()
    )
    sample_task = task_brains and task_brains[0].getObject() or None

    # verify if the update is needed
    do_update = False
    for interface_name, marker_interface in marker_interfaces.iteritems():
        is_provided = marker_interface.providedBy(sample_task)
        # new interface on the config but not present yet on the tasks => update
        if interface_name in (task_config.marker_interfaces or []) and not is_provided:
            do_update = True
            break
        # old interface on the tasks no longer present on the config => update
        elif (
            interface_name not in (task_config.marker_interfaces or []) and is_provided
        ):
            do_update = True
            break

    if do_update:
        for task_brain in task_brains:
            task = task_brain.getObject()

            for (
                marker_interface_name,
                marker_interface,
            ) in marker_interfaces.iteritems():
                if marker_interface_name in task_config.marker_interfaces:
                    alsoProvides(task, marker_interface)
                else:
                    noLongerProvides(task, marker_interface)

            task.reindexObject(idxs=["object_provides"])
