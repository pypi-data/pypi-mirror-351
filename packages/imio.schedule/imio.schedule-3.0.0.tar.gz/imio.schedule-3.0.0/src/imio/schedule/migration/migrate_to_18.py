# -*- coding: utf-8 -*-

from imio.schedule.workflow.freeze_task import FreezeTaskWorkflowAdaptation

import logging

logger = logging.getLogger("imio.schedule: migrations")


def migrate_to_18(context):
    """ """
    logger = logging.getLogger("imio.schedule: migrate to 1.8")
    logger.info("starting migration steps")

    logger.info("add freeze state to task workflow")
    adaptation = FreezeTaskWorkflowAdaptation()
    adaptation.patch_workflow("task_workflow")

    logger.info("reinstalling imio.schedule done!")
    logger.info("migration done!")
