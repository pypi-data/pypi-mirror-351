# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema
from z3c.form.form import Form
from z3c.form import button
from z3c.form import field
from Products.statusmessages.interfaces import IStatusMessage
from plone.z3cform.layout import FormWrapper
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from imio.schedule import _


class ITaskChangeOwner(Interface):

    new_owner = schema.Choice(
        title=_(u"New owner"),
        vocabulary="schedule.task_owner",
        required=True,
    )


class TaskChangeOwnerForm(Form):
    fields = field.Fields(ITaskChangeOwner)
    ignoreContext = True

    @button.buttonAndHandler(_(u"Confirm"))
    def handleApply(self, action):
        messages = IStatusMessage(self.request)
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            messages.addStatusMessage(self.status, type="error")
            return
        self.context.assigned_user = data.get("new_owner")
        self.context.reindexObject()
        self.context.reindex_parent_tasks(idxs=["is_solvable_task"])
        self.status = _(u"Owner changed")


class TaskChangeOwnerView(FormWrapper):
    form = TaskChangeOwnerForm
    index = ViewPageTemplateFile("templates/task_change_owner.pt")
