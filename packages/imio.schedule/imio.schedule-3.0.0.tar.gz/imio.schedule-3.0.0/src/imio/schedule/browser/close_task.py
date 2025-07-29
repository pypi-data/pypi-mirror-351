# -*- coding: utf-8 -*-

from zope.interface import Interface
from z3c.form.form import Form
from z3c.form import button
from z3c.form import field
from Products.statusmessages.interfaces import IStatusMessage
from plone.z3cform.layout import FormWrapper
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from imio.schedule import _


class ICloseTask(Interface):
    """ """


class CloseTaskForm(Form):
    fields = field.Fields(ICloseTask)
    ignoreContext = True

    @button.buttonAndHandler(_(u"Confirm"))
    def handleApply(self, action):
        messages = IStatusMessage(self.request)
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            messages.addStatusMessage(self.status, type="error")
            return
        self.context._end()
        self.context.reindex_parent_tasks(idxs=["is_solvable_task"])
        self.status = _(u"Task Closed")


class CloseTaskView(FormWrapper):
    form = CloseTaskForm
    index = ViewPageTemplateFile("templates/close_task.pt")
