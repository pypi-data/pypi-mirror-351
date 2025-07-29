# -*- coding: utf-8 -*-

from collective.wfadaptations.interfaces import IWorkflowAdaptation

from Persistence import PersistentMapping

from plone import api

from zope.interface import implements


class FreezeTaskWorkflowAdaptation(object):
    """
    Suspension workflow adaptation adding a suspension state.
    """

    implements(IWorkflowAdaptation)

    schema = None

    def patch_workflow(self, workflow_name, **parameters):

        wtool = api.portal.get_tool("portal_workflow")
        workflow = wtool[workflow_name]

        self.create_frozen_state(workflow, **parameters)

        message = "patched '{}' workflow with frozen state".format(workflow_name)
        return True, message

    def create_frozen_state(self, workflow, **parameters):
        """
        create a 'frozen' state
        """
        if "frozen" not in workflow.states:
            workflow.states.addState("frozen")

        frozen_state = workflow.states["frozen"]
        default_mapping = workflow.states.objectValues()[0].permission_roles.copy()
        frozen_state.title = "frozen"
        frozen_state.permission_roles = default_mapping
        frozen_state.group_roles = PersistentMapping()
        frozen_state.var_values = PersistentMapping()
        frozen_state.transitions = ()
