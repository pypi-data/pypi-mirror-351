# -*- coding: utf-8 -*-

from imio.schedule import _
from imio.schedule.content.schedule_config import IScheduleConfig
from imio.schedule.interfaces import IScheduleCollection

from plone import api

from zope.interface import alsoProvides


def create(schedule_container, event):
    """ """
    # do not automatically re-create the collection during upgrade steps
    if "portal_setup/manage_importSteps" in schedule_container.REQUEST.URL:
        return

    collection_id = "dashboard_collection"
    title = (
        IScheduleConfig.providedBy(schedule_container)
        and _("All")
        or schedule_container.Title()
    )

    if collection_id not in schedule_container.objectIds():
        factory_args = {
            "id": "dashboard_collection",
            "title": title,
            "query": [
                {
                    "i": "CompoundCriterion",
                    "o": "plone.app.querystring.operation.compound.is",
                    "v": schedule_container.UID(),
                },
                {
                    "i": "review_state",
                    "o": "plone.app.querystring.operation.selection.is",
                    "v": ["to_do"],
                },
            ],
            "customViewFields": (u"assigned_user", u"status", u"due_date"),
            "sort_on": u"due_date",
            "sort_reversed": True,
            "b_size": 30,
        }

        if IScheduleConfig.providedBy(schedule_container):
            factory_args["customViewFields"] = (
                u"pretty_link",
                u"sortable_title",
                u"assigned_user",
                u"status",
                u"due_date",
            )

        kwargs = {}
        additional_queries = kwargs.pop("query", [])
        for query in additional_queries:
            factory_args["query"].append(query)
        factory_args.update(kwargs)

        portal_types = api.portal.get_tool("portal_types")
        type_info = portal_types.getTypeInfo("DashboardCollection")
        collection = type_info._constructInstance(schedule_container, **factory_args)
        # mark the collection with an interface to to customize the render
        # term view of collection widget
        alsoProvides(collection, IScheduleCollection)


def update_title(schedule_container, event):
    """
    Dashboard Collection title should always be the title of the parent task.
    """
    # do not automatically re-create the collection during upgrade steps
    if "portal_setup" in schedule_container.REQUEST.URL:
        return

    collection = getattr(schedule_container, "dashboard_collection", None)
    if collection:
        title = (
            IScheduleConfig.providedBy(schedule_container)
            and _("All")
            or schedule_container.Title()
        )
        collection.title = title
        collection.reindexObject(idxs=("Title", "sortable_title"))
