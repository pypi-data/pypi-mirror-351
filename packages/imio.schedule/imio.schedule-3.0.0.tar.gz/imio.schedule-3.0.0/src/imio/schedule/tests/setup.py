# -*- coding: utf-8 -*-

from plone import api

from Products.ATContentTypes.interfaces import IATFolder
from Products.ATContentTypes.interfaces import IATFile

from imio.schedule.utils import interface_to_tuple
from imio.schedule.content.object_factories import CreationConditionObject
from imio.schedule.content.object_factories import StartConditionObject
from imio.schedule.content.object_factories import EndConditionObject
from imio.schedule.content.object_factories import FreezeConditionObject
from imio.schedule.content.object_factories import MacroCreationConditionObject
from imio.schedule.content.object_factories import MacroStartConditionObject
from imio.schedule.content.object_factories import MacroEndConditionObject
from imio.schedule.content.object_factories import ThawConditionObject


def schedule_example_install(context):
    """
    Example schedule install script.
    """
    if context.readDataFile("imioschedule_testing.txt") is None:
        return

    monkey_patch_scheduled_conttentype_vocabulary(context)
    add_empty_task_container(context)
    add_schedule_config(context)
    add_task(context)


def monkey_patch_scheduled_conttentype_vocabulary(context):
    """
    Monkey patch the default vocabulary for the field 'scheduled_contenttype'
    to be able to select 'Folder' content type so we can test methods of this
    field.
    """
    from imio.schedule.content.vocabulary import ScheduledContentTypeVocabulary

    def monkey_allowed_types(self):
        return {"Folder": IATFolder}

    ScheduledContentTypeVocabulary.content_types = monkey_allowed_types


def add_empty_task_container(context):
    """
    Add dummy empty task container (ATFolder)
    """
    site = api.portal.get()

    folder_id = "test_empty_taskcontainer"
    if folder_id not in site.objectIds():
        api.content.create(
            container=site, type="Folder", id=folder_id, title="Empty Task container"
        )


def add_schedule_config(context):
    """
    Add dummy ScheduleConfig, TaskConfig.
    """
    site = api.portal.get()

    # create config folder for schedule config
    folder_id = "config"
    if folder_id not in site.objectIds():
        api.content.create(
            container=site, type="Folder", id=folder_id, title="Task configs"
        )
    cfg_folder = getattr(site, folder_id)

    # create empty schedule config
    schedule_cfg_id = "empty_scheduleconfig"
    if schedule_cfg_id not in cfg_folder.objectIds():
        api.content.create(
            container=cfg_folder,
            type="ScheduleConfig",
            id=schedule_cfg_id,
            title="Empty ScheduleConfig",
            scheduled_contenttype=("Folder", (interface_to_tuple(IATFile),)),
        )

    # create schedule config
    schedule_cfg_id = "test_scheduleconfig"
    if schedule_cfg_id not in cfg_folder.objectIds():
        api.content.create(
            container=cfg_folder,
            type="ScheduleConfig",
            id=schedule_cfg_id,
            title="Test ScheduleConfig",
            scheduled_contenttype=("Folder", (interface_to_tuple(IATFolder),)),
        )
    schedule_config = getattr(cfg_folder, schedule_cfg_id)

    # create task config
    task_cfg_id = "test_taskconfig"
    creation_conditions = CreationConditionObject()
    creation_conditions.__dict__ = {
        "condition": u"schedule.test_creation_condition",
        "operator": "AND",
    }
    start_conditions = StartConditionObject()
    start_conditions.__dict__ = {
        "condition": u"schedule.test_start_condition",
        "operator": "AND",
    }
    end_conditions = EndConditionObject()
    end_conditions.__dict__ = {
        "condition": u"schedule.test_end_condition",
        "operator": "AND",
    }
    freeze_conditions = FreezeConditionObject()
    freeze_conditions.__dict__ = {
        "condition": u"schedule.test_freeze_condition",
        "operator": "AND",
    }
    thaw_conditions = ThawConditionObject()
    thaw_conditions.__dict__ = {
        "condition": u"schedule.test_thaw_condition",
        "operator": "AND",
    }
    macro_creation_conditions = MacroCreationConditionObject()
    macro_creation_conditions.__dict__ = creation_conditions.__dict__
    macro_start_conditions = MacroStartConditionObject()
    macro_start_conditions.__dict__ = start_conditions.__dict__
    macro_end_conditions = MacroEndConditionObject()
    macro_end_conditions.__dict__ = end_conditions.__dict__

    if task_cfg_id not in schedule_config.objectIds():
        api.content.create(
            container=schedule_config,
            type="TaskConfig",
            id=task_cfg_id,
            title="Test TaskConfig",
            default_assigned_user="schedule.assign_current_user",
            default_assigned_group="schedule.assign_authenticatedusers_group",
            creation_conditions=[creation_conditions],
            start_conditions=[start_conditions],
            end_conditions=[end_conditions],
            freeze_conditions=[freeze_conditions],
            thaw_conditions=[thaw_conditions],
            creation_state="private",
            starting_states=("pending",),
            ending_states=("published",),
            start_date="schedule.start_date.creation_date",
            additional_delay=10,
        )

    # create macro task config
    macrotask_cfg_id = "test_macrotaskconfig"
    if macrotask_cfg_id not in schedule_config.objectIds():
        api.content.create(
            container=schedule_config,
            type="MacroTaskConfig",
            id=macrotask_cfg_id,
            title="Test MacroTaskConfig",
            default_assigned_user="schedule.assign_current_user",
            default_assigned_group="schedule.assign_authenticatedusers_group",
            creation_conditions=[macro_creation_conditions],
            start_conditions=[macro_start_conditions],
            end_conditions=[macro_end_conditions],
            creation_state="private",
            starting_states=("pending",),
            ending_states=("published",),
            start_date="schedule.start_date.subtask_highest_due_date",
            additional_delay=17,
        )
    macrotask_config = getattr(schedule_config, macrotask_cfg_id)

    # create sub task config
    subtask_cfg_id = "test_subtaskconfig"
    if subtask_cfg_id not in macrotask_config.objectIds():
        api.content.create(
            container=macrotask_config,
            type="TaskConfig",
            id=subtask_cfg_id,
            title="Test SubTaskConfig",
            default_assigned_user="schedule.assign_current_user",
            default_assigned_group="schedule.assign_authenticatedusers_group",
            creation_conditions=[creation_conditions],
            start_conditions=[start_conditions],
            end_conditions=[end_conditions],
            creation_state="private",
            starting_states=("pending",),
            ending_states=("published",),
            start_date="schedule.start_date.creation_date",
            additional_delay=13,
        )


def add_task(context):
    """
    Add dummy task container (ATFolder) and create
    a AutomatedTask in it
    """
    site = api.portal.get()

    task_container_id = "test_taskcontainer"
    if task_container_id not in site.objectIds():
        api.content.create(
            container=site, type="Folder", id=task_container_id, title="Task container"
        )
    task_container = getattr(site, task_container_id)

    # If no task was created automatically, create the task manually
    # to keep AutomatedTask tests alive
    task_id = "TASK_test_taskconfig"
    if task_id not in task_container.objectIds():
        portal_types = api.portal.get_tool("portal_types")
        type_info = portal_types.getTypeInfo("AutomatedTask")
        schedule_config = site.config.test_scheduleconfig
        task_config = schedule_config.test_taskconfig

        type_info._constructInstance(
            container=task_container,
            id=task_id,
            title=task_config.Title(),
            schedule_config_UID=schedule_config.UID(),
            task_config_UID=task_config.UID(),
        )

    # If no task was created automatically, create the macrotask manually
    # to keep AutomatedMacroTask tests alive
    macrotask_id = "TASK_test_macrotaskconfig"
    if macrotask_id not in task_container.objectIds():
        portal_types = api.portal.get_tool("portal_types")
        type_info = portal_types.getTypeInfo("AutomatedMacroTask")
        schedule_config = site.config.test_scheduleconfig
        task_config = schedule_config.test_macrotaskconfig

        type_info._constructInstance(
            container=task_container,
            id=macrotask_id,
            title=task_config.Title(),
            schedule_config_UID=schedule_config.UID(),
            task_config_UID=task_config.UID(),
        )
    macro_task = getattr(task_container, macrotask_id)

    # If no task was created automatically, create the subtask manually
    # to keep AutomatedMacroTask tests alive
    subtask_id = "TASK_test_subtaskconfig"
    if subtask_id not in macro_task.objectIds():
        portal_types = api.portal.get_tool("portal_types")
        type_info = portal_types.getTypeInfo("AutomatedTask")
        schedule_config = site.config.test_scheduleconfig
        task_config = schedule_config.test_macrotaskconfig.test_subtaskconfig

        type_info._constructInstance(
            container=macro_task,
            id=subtask_id,
            title=task_config.Title(),
            schedule_config_UID=schedule_config.UID(),
            task_config_UID=task_config.UID(),
        )
