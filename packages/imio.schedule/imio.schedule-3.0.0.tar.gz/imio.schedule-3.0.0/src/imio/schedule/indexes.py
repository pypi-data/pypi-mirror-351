# -*- coding: utf-8 -*-

from imio.schedule.content.task import IAutomatedTask

from plone.indexer import indexer


@indexer(IAutomatedTask)
def schedule_config_UID(task):
    """
    Return the ScheduleConfig UID of this task.
    """
    return task.schedule_config_UID


@indexer(IAutomatedTask)
def task_config_UID(task):
    """
    Return the TaskConfig UID of this task.
    """
    return task.task_config_UID


@indexer(IAutomatedTask)
def is_solvable_task(task):
    """
    Return 'True' if the task and its open (sub-)subtasks are doable by the same person.
    """
    return str(task.is_solvable)
