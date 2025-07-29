# encoding: utf-8

from collective.eeafaceted.z3ctable.columns import BaseColumn

from plone import api

from imio.schedule import _
from imio.schedule.config import CREATION
from imio.schedule.config import DONE
from imio.schedule.config import STARTED
from imio.schedule.content.task import IAutomatedMacroTask
from imio.schedule.dashboard.interfaces import IDisplayTaskStatus
from imio.schedule.dashboard.interfaces import ISimpleDisplayTaskStatus
from imio.schedule.dashboard.interfaces import IStatusColumn
from imio.schedule.interfaces import IToIcon
from imio.schedule.utils import close_or_past_date

from zope.component import queryAdapter
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.i18n import translate


def due_date_extra_classes(due_date, review_state):
    extra_classes = ""

    if review_state != "closed" and due_date and due_date.year != 9999:
        orange_limit = api.portal.get_registry_record(
            "imio.schedule.interfaces.IDueDateSettings.color_orange_x_days_before_due_date",
            default=None,
        )
        red_limit = api.portal.get_registry_record(
            "imio.schedule.interfaces.IDueDateSettings.color_red_x_days_before_due_date",
            default=None,
        )
        if red_limit is not None and close_or_past_date(due_date, by_days=red_limit):
            extra_classes += " red_close_due_date"
        elif orange_limit is not None and close_or_past_date(
            due_date, by_days=orange_limit
        ):
            extra_classes += " orange_close_due_date"

    return extra_classes


class DueDateColumn(BaseColumn):
    """Due date column for schedule listings."""

    def renderCell(self, item):
        due_date = item.due_date
        if not due_date or due_date.year == 9999:
            return u"\u221E"

        return due_date.strftime("%d/%m/%Y")

    def getCSSClasses(self, item):
        """Returns a CSS class specific to current content."""
        cssClasses = super(DueDateColumn, self).getCSSClasses(item)

        cssClasses["td"] += due_date_extra_classes(item.due_date, item.review_state)

        return cssClasses


class AssignedUserColumn(BaseColumn):
    """display licence address in SearchResultTable"""

    def renderCell(self, item):
        username = item.assigned_user
        groupname = item.assigned_group

        user = username and api.user.get(username)
        username = user and user.getProperty("fullname").decode("utf-8") or username
        assigned = username
        if groupname:
            to_icon = queryAdapter(item, IToIcon)
            group = api.group.get(groupname)
            if to_icon:
                icon_url = to_icon.get_icon_url()
                groupname = '<img src="{}">'.format(icon_url)
            else:
                groupname = (
                    group and group.getProperty("title").decode("utf-8") or groupname
                )
                groupname = "({})".format(groupname)

            assigned = u"{user} {group}".format(user=username, group=groupname)

        return assigned


class StatusColum(BaseColumn):
    """
    Column displaying the status of the tasks and its subtasks if it has any.
    """

    implements(IStatusColumn)

    sort_index = -1
    display_status_interface = IDisplayTaskStatus
    escape = False

    def renderHeadCell(self):
        """Override rendering of head of the cell to include jQuery
        call to initialize annexes menu and to show the 'more/less details' if we are listing items."""
        # activate necessary javascripts
        if not self.header_js:
            # avoid problems while concataining None and unicode
            self.header_js = u""
        self.header_js += (
            u'<script type="text/javascript">'
            + u'$("#task_status a").prepOverlay({subtype: "ajax"});'
            + "</script>"
        )
        return super(StatusColum, self).renderHeadCell()

    def renderCell(self, item):
        """ """
        status = ""
        task = item.getObject()

        adapter = queryMultiAdapter(
            (self, task, api.portal.getRequest()), self.display_status_interface
        )
        if adapter:
            status = adapter.render()
        return status


class SimpleStatusColumn(StatusColum):
    """
    Used for task listing on a single task container.
    """

    display_status_interface = ISimpleDisplayTaskStatus


class SimpleTaskStatusDisplay(object):
    """
    Adpater, adapting a task and returning some html
    table cell displaying its status.
    """

    implements(IDisplayTaskStatus)

    def __init__(self, column, task, request):
        self.task = task
        self.request = request

    def render(self):
        task = self.task
        status = u'<span class="simple_task">&nbsp&nbsp&nbsp</span>'
        link = (
            '<a class="link-overlay" href="{task_url}/@@item_view">{status}</a>'.format(
                task_url=task.absolute_url(), status=status
            )
        )
        status_display = '<span id="task_status">{}</span>'.format(link)
        return status_display


class TaskStatusDisplay(object):
    """
    Adpater, adapting a task and returning some html
    table cell displaying its status.
    """

    implements(IDisplayTaskStatus)

    def __init__(self, column, task, request):
        self.task = task
        self.request = request

    def render(self):
        task = self.task
        return self.display_task_status(
            task, with_subtasks=IAutomatedMacroTask.providedBy(task)
        )

    def display_task_status(self, task, with_subtasks=False):
        """
        By default just put a code colour of the state of the task.
        """
        css_class = "schedule_{}".format(api.content.get_state(task))
        css_level = "term-level-{}".format(self.task.level())
        status = u'<span class="{css_level}"><span class="{css_class}">&nbsp&nbsp&nbsp</span></span>'.format(
            css_level=css_level,
            css_class=css_class,
        )
        if task.get_status() in [CREATION, STARTED]:
            viewname = "{}{}_status".format(
                (not with_subtasks) and "simple_" or "",
                task.get_status() is CREATION and "start" or "end",
            )
            status = '<a class="link-overlay" href="{task_url}/@@{view}">{status}</a>'.format(
                task_url=task.absolute_url(), view=viewname, status=status
            )
        status = '<span id="task_status">{}</span>'.format(status)
        return status


class MacroTaskStatusDisplay(TaskStatusDisplay):
    """
    Adapts a macro task and return some html table cell
    displaying the status of all subtasks that need to be done.
    """

    def render(self):
        """ """
        all_subtasks = self.task.get_last_subtasks()
        subtasks_to_do = [task for task in all_subtasks if task.get_status() != DONE]
        if not subtasks_to_do:
            return self.display_task_status(self.task)

        rows = [
            u'<tr><th class="subtask_status_icon">{icon}</th>\
            <th i18n:translate="">{subtask}</th>\
            <th i18n:translate="">{due_date}</th></tr>'.format(
                icon=self.display_task_status(
                    self.task, with_subtasks=bool(subtasks_to_do)
                ),
                subtask=translate(_("Subtask"), context=self.request),
                due_date=translate(_("Due date"), context=self.request),
            ),
        ]
        for task in subtasks_to_do:
            title = task.Title()
            display_subtasks = IAutomatedMacroTask.providedBy(task)
            status_icon = u'<td class="subtask_status_icon">{status}</td>'.format(
                status=self.display_task_status(task, with_subtasks=display_subtasks),
            )
            status_title = u'<td class="subtask_status_title">{title}</td>'.format(
                title=title.decode("utf-8"),
            )
            date = task.due_date
            due_date = date.year == 9999 and u"\u221E" or date.strftime("%d/%m/%Y")
            extra_css_classes = due_date_extra_classes(
                task.due_date,
                api.content.get_state(task),
            )
            due_date = u'<td class="subtask_status_date{}">{}</td>'.format(
                extra_css_classes, due_date
            )
            row = u"<tr>{icon}{title}{due_date}</tr>".format(
                icon=status_icon, title=status_title, due_date=due_date
            )
            rows.append(row)

        status_display = u"<table class=subtask_status_table>{}</table>".format(
            "".join(rows)
        )
        return status_display
