# -*- coding: utf-8 -*-

from plone.dexterity.browser.edit import DefaultEditForm
from z3c.form.interfaces import DISPLAY_MODE
from plone.z3cform import layout


class CustomViewForm(DefaultEditForm):
    mode = DISPLAY_MODE

    _actions_keys = ["save", "cancel"]

    def update(self):
        super(CustomViewForm, self).update()
        for action in self._actions_keys:
            del self.actions[action]


CustomView = layout.wrap_form(CustomViewForm)
