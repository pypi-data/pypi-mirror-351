# -*- coding: utf-8 -*-

from Acquisition import aq_base

from imio.schedule.interfaces import TaskAlreadyExists
from imio.schedule.utils import get_task_configs

from plone import api


def create_new_tasks(task_container, event):
    """
    For each task config associated to this task container content type
    check the task config creations conditions and create the task if
    we can.
    """

    # This handler can be triggered for archetypes containers by the
    # workflow modification event but we want to create tasks only if
    # the container really exists (more than just created in portal_factory...)
    if hasattr(aq_base(task_container), "checkCreationFlag"):
        if task_container.checkCreationFlag():
            return

    # descending=True <= it's important to create to macro tasks first
    task_configs = get_task_configs(task_container, descending=True)

    if not task_configs:
        return

    with api.env.adopt_roles(["Manager"]):
        for config in task_configs:
            if config.is_main_taskconfig():
                if config.should_create_task(task_container):
                    try:
                        config.create_task(task_container)
                    except TaskAlreadyExists:
                        continue
            # case of a sub-task creation, the parent should have been created first
            else:
                macro_config = config.getParentNode()
                parent_task = macro_config.get_open_task(task_container)
                if parent_task and config.should_create_task(
                    task_container, parent_container=parent_task
                ):
                    try:
                        config.create_task(task_container, creation_place=parent_task)
                    except TaskAlreadyExists:
                        continue
