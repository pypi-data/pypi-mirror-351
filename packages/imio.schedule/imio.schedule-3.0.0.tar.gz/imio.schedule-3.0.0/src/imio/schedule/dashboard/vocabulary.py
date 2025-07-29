# -*- coding: utf-8 -*-

from imio.schedule.config import task_types

from plone import api

from zope.i18n import translate as _
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class TaskWorkflowStates(object):
    """
    List all states of urban licence workflow.
    """

    def __call__(self, context):

        states = ["created", "to_do", "closed"]

        vocabulary_terms = []
        for state in states:
            vocabulary_terms.append(
                SimpleTerm(state, state, _(state, "collective.task", context.REQUEST))
            )

        vocabulary = SimpleVocabulary(vocabulary_terms)
        return vocabulary


class TaskPortalTypes(object):
    """
    List all states of urban licence workflow.
    """

    def __call__(self, context):

        portal_types = api.portal.get_tool("portal_types")
        vocabulary_terms = []

        for task_type in task_types:
            p_type = portal_types[task_type]
            vocabulary_terms.append(
                SimpleTerm(
                    task_type,
                    task_type,
                    _(p_type.Title(), "imio.schedule", context.REQUEST),
                )
            )

        vocabulary = SimpleVocabulary(vocabulary_terms)
        return vocabulary
