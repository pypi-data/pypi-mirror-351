# -*- coding: utf-8 -*-

from collective.eeafaceted.collectionwidget.vocabulary import CollectionVocabulary

from plone import api

from zope.annotation import IAnnotations


class ScheduleCollectionVocabulary(CollectionVocabulary):
    """
    Return vocabulary of base searchs for schedule faceted view.
    """

    def _brains(self, context):
        """
        Return all the DashboardCollections in the 'schedule' folder.
        """
        configs_UID = IAnnotations(context).get("imio.schedule.schedule_configs", [])
        catalog = api.portal.get_tool("portal_catalog")
        config_brains = catalog(UID=configs_UID)
        collections_brains = []
        for brain in config_brains:
            config = brain.getObject()
            brains = catalog(
                path={
                    "query": "/".join(config.getPhysicalPath()),
                },
                object_provides="plone.app.contenttypes.interfaces.ICollection",
                sort_on="getObjPositionInParent",
            )
            collections_brains.extend(brains)
        collections_brains = [
            b for b in collections_brains if b.getObject().aq_parent.enabled
        ]
        return collections_brains


ScheduleCollectionVocabularyFactory = ScheduleCollectionVocabulary()
