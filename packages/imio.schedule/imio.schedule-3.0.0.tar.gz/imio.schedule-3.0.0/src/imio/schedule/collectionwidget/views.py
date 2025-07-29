# -*- coding: utf-8 -*-

from collective.eeafaceted.collectionwidget.browser.views import RenderTermView

from imio.schedule.interfaces import IToIcon

from zope.component import queryAdapter


class RenderScheduleTermView(RenderTermView):
    """ """

    selected_term = ""

    def get_icon(self):
        to_icon = queryAdapter(self.context, IToIcon)
        if to_icon:
            return to_icon.get_icon_url()
        return ""
