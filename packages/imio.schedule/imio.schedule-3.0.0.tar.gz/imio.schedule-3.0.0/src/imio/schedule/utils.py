# -*- coding: utf-8 -*-

from eea.facetednavigation.layout.interfaces import IFacetedLayout

from imio.dashboard.browser.facetedcollectionportlet import Assignment
from collective.eeafaceted.collectionwidget.utils import _updateDefaultCollectionFor

from imio.schedule.config import CREATION
from imio.schedule.config import STARTED
from imio.schedule.config import states_by_status
from imio.schedule.content.task import IAutomatedTask
from imio.schedule.interfaces import IToTaskConfig
from imio.schedule.interfaces import ICalendarExtraHolidays

from plone import api
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.constants import CONTEXT_CATEGORY

from zope.annotation import IAnnotations
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import getUtilitiesFor
from zope.schema.vocabulary import SimpleVocabulary
from workalendar.europe import Belgium

import datetime
import importlib


def get_all_schedule_configs():
    """
    Return all the ScheduleConfig of the site.
    """
    # nested import to avoid recursive imports
    from imio.schedule.content.schedule_config import IScheduleConfig

    catalog = api.portal.get_tool("portal_catalog")
    brains = catalog(object_provides=IScheduleConfig.__identifier__)
    configs = [brain.getObject() for brain in brains]

    return configs


def get_task_configs(task_container, descending=False):
    """
    Return all the task configs to check for the given context
    providing ITaskContainer.
    """
    config_adapters = getAdapters((task_container,), IToTaskConfig)
    task_configs = [adapter.task_config for name, adapter in config_adapters]
    ordering = descending and 1 or -1
    task_configs = sorted(task_configs, key=lambda cfg: ordering * cfg.level())

    return task_configs


def get_container_open_tasks(task_container):
    """
    Return all the open tasks of a container.
    """
    states = states_by_status[CREATION] + states_by_status[STARTED]
    open_tasks = get_container_tasks(task_container, states)
    return open_tasks


def end_all_open_tasks(task_container):
    """
    End all open tasks of a container without checking any condition.
    """
    tasks_to_end = get_container_open_tasks(task_container)
    for task in tasks_to_end:
        task._end()
    return tasks_to_end


def get_container_tasks(task_container, states=[]):
    """
    Return all the tasks of a container.
    """
    open_tasks = []
    to_explore = [task_container]
    while to_explore:
        current = to_explore.pop()
        if IAutomatedTask.providedBy(current):
            if not states:
                open_tasks.append(current)
            elif api.content.get_state(current) in states:
                open_tasks.append(current)
        if hasattr(current, "objectValues"):
            to_explore.extend(current.objectValues())
    return open_tasks


def tuple_to_interface(interface_tuple):
    """
    Turn a tuple of strings:
    ('interface.module.path', 'Interface')
    into an Interface class.
    """
    module_path, interface_name = interface_tuple
    interface_module = importlib.import_module(module_path)
    interface_class = getattr(interface_module, interface_name)

    return interface_class


def interface_to_tuple(interface):
    """
    Turn an Interface class into a tuple of strings:
    ('interface.module.path', 'Interface')
    """
    return (interface.__module__, interface.__name__)


def set_schedule_view(
    folder, faceted_config_path, schedule_configs, default_collection=None
):
    """
    Boilerplate code to set up the schedule view on a folderish context.
    """

    if type(schedule_configs) not in [list, tuple]:
        schedule_configs = [schedule_configs]

    _set_faceted_view(folder, faceted_config_path, schedule_configs, default_collection)
    _set_collection_portlet(folder)


def _set_faceted_view(
    folder, faceted_config_path, schedule_configs, default_collection=None
):
    """ """
    annotations = IAnnotations(folder)
    key = "imio.schedule.schedule_configs"
    annotations[key] = [cfg.UID() for cfg in schedule_configs]

    subtyper = folder.restrictedTraverse("@@faceted_subtyper")
    if not subtyper.is_faceted:
        subtyper.enable()
        folder.restrictedTraverse("@@faceted_settings").toggle_left_column()
        IFacetedLayout(folder).update_layout("faceted-table-items")
        folder.unrestrictedTraverse("@@faceted_exportimport").import_xml(
            import_file=open(faceted_config_path)
        )

    default_collection = default_collection or schedule_configs[0].dashboard_collection
    _updateDefaultCollectionFor(folder, default_collection.UID())


def _set_collection_portlet(folder):
    """ """
    # block parent portlets
    manager = getUtility(IPortletManager, name="plone.leftcolumn")
    blacklist = getMultiAdapter((folder, manager), ILocalPortletAssignmentManager)
    blacklist.setBlacklistStatus(CONTEXT_CATEGORY, True)

    # assign collection portlet
    manager = getUtility(IPortletManager, name="plone.leftcolumn", context=folder)
    mapping = getMultiAdapter((folder, manager), IPortletAssignmentMapping)
    if "schedules" not in mapping.keys():
        mapping["schedules"] = Assignment("schedules")


def dict_list_2_vocabulary(dict_list):
    """dict_list_2_vocabulary
    Converts a dictionary list to a SimpleVocabulary

    :param dict_list: dictionary list
    """
    terms = []
    for item in dict_list:
        for key in sorted([k for k in item]):
            terms.append(SimpleVocabulary.createTerm(key, str(key), item[key]))
    return SimpleVocabulary(terms)


def round_to_weekday(date, weekday):
    direction = weekday / abs(weekday)  # -1 => past, +1 => future
    weekday = abs(weekday) - 1
    days_delta = weekday - date.weekday()
    if days_delta * direction < 0:
        days_delta += 7 * direction
    return date + datetime.timedelta(days_delta)


def close_or_past_date(date, by_days=7):
    """
    Checks if a date is getting close (or already past)

    :type date: datetime.date
    :type by_days: int
    """
    today = datetime.date.today()
    limit_date = date - datetime.timedelta(days=by_days)
    return today >= limit_date


class WorkingDaysCalendar(Belgium):
    def __init__(self, *args, **kwargs):
        super(WorkingDaysCalendar, self).__init__(*args, **kwargs)
        self.working_days = self._get_working_days()

    def is_working_day(self, date, *args, **kwargs):
        result = super(WorkingDaysCalendar, self).is_working_day(date, *args, **kwargs)
        if result is True:
            result = date.isoweekday() in self.working_days
        return result

    def get_calendar_holidays(self, year):
        result = super(WorkingDaysCalendar, self).get_calendar_holidays(year)
        for name, utility in getUtilitiesFor(ICalendarExtraHolidays):
            result += utility.get_holidays(year)
        return result

    def _get_working_days(self):
        """Return the working days configured in the registry"""
        matching = {
            "monday": 1,
            "tuesday": 2,
            "wednesday": 3,
            "thursday": 4,
            "friday": 5,
            "saturday": 6,
            "sunday": 7,
        }
        days = (
            api.portal.get_registry_record(
                "imio.schedule.interfaces.ISettings.working_days"
            )
            or []
        )
        return [matching[d] for d in days]
