# -*- coding: utf-8 -*-

from plone import api

from imio.schedule.testing import ExampleScheduleIntegrationTestCase
from imio.schedule.testing import MacroTaskScheduleIntegrationTestCase

from zope.component import getUtility
from zope.component import queryAdapter
from zope.component import queryUtility
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory


class TestDashboardVocabularies(ExampleScheduleIntegrationTestCase):
    """
    Test dashboard vocabularies registration and values.
    """

    def test_task_workflow_vocabulary_factory_registration(self):
        """
        Content types voc factory should be registered as a named utility.
        """
        factory_name = "schedule.TaskWorkflowStates"
        self.assertTrue(queryUtility(IVocabularyFactory, factory_name))

    def test_task_workflow_vocabulary_values(self):
        """
        Test task workflow vocabulary values.
        """

        voc_name = "schedule.TaskWorkflowStates"
        voc_factory = getUtility(IVocabularyFactory, voc_name)
        vocabulary = voc_factory(self.schedule_config)
        expected_keys = ["created", "to_do", "closed"]
        for expected_key in expected_keys:
            msg = "expected key:\n{expected}\nwas not found in voc_keys:\n{voc}".format(
                expected=expected_key, voc=vocabulary.by_token.keys()
            )
            self.assertTrue(expected_key in vocabulary.by_token.keys(), msg)


class TestVocabularies(ExampleScheduleIntegrationTestCase):
    """
    Test field vocabularies registration and values.
    """

    def _get_fti(self, portal_type):
        """
        Helper method to return the fti of a content type.
        """
        portal_types = api.portal.get_tool("portal_types")
        fti = portal_types.getTypeInfo(portal_type)
        return fti

    def test_content_types_vocabulary_factory_registration(self):
        """
        Content types voc factory should be registered as a named utility.
        """
        factory_name = "schedule.scheduled_contenttype"
        self.assertTrue(queryUtility(IVocabularyFactory, factory_name))

    def test_content_types_default_vocabulary_registration(self):
        """
        Voc values should be registered as a named adapter on the task
        config fti and name should be the fti portal_type.
        """
        from imio.schedule.interfaces import IScheduledContentTypeVocabulary

        portal_type = self.schedule_config.portal_type

        voc_adapter = queryAdapter(
            self._get_fti(portal_type), IScheduledContentTypeVocabulary, portal_type
        )
        self.assertTrue(voc_adapter)

    def test_content_types_vocabulary_values(self):
        """
        Test some content_types values.
        """

        voc_name = "schedule.scheduled_contenttype"
        voc_factory = getUtility(IVocabularyFactory, voc_name)
        vocabulary = voc_factory(self.schedule_config)
        expected_key = (
            "('Folder', (('Products.ATContentTypes.interfaces.folder', 'IATFolder'),))"
        )
        msg = "expected key:\n{expected}\nwas not found in voc_keys:\n{voc}".format(
            expected=expected_key, voc=vocabulary.by_token.keys()
        )
        self.assertTrue(expected_key in vocabulary.by_token.keys(), msg)

    def test_assigned_user_vocabulary_factory_registration(self):
        """
        Content types voc factory should be registered as a named utility.
        """
        factory_name = "schedule.assigned_user"
        self.assertTrue(queryUtility(IVocabularyFactory, factory_name))

    def test_assigned_user_vocabulary_values(self):
        """
        Test some assigned_user values.
        """
        voc_name = "schedule.assigned_user"
        voc_factory = getUtility(IVocabularyFactory, voc_name)
        vocabulary = voc_factory(self.task_config)
        self.assertTrue("schedule.assign_current_user" in vocabulary)

        term = vocabulary.getTerm("schedule.assign_current_user")
        translation = translate(
            term.title, context=self.portal.REQUEST, target_language="fr"
        )
        msg = "Condition title was not translated"
        self.assertEquals(translation, u"Utilisateur connecté", msg)

    def test_creation_conditions_vocabulary_factory_registration(self):
        """
        Content types voc factory should be registered as a named utility.
        """
        factory_name = "schedule.creation_conditions"
        self.assertTrue(queryUtility(IVocabularyFactory, factory_name))

    def test_creation_conditions_vocabulary_values(self):
        """
        Test some creation_conditions values.
        """
        voc_name = "schedule.creation_conditions"
        voc_factory = getUtility(IVocabularyFactory, voc_name)
        vocabulary = voc_factory(self.task_config)
        self.assertTrue("schedule.test_creation_condition" in vocabulary)

        term = vocabulary.getTerm("schedule.test_creation_condition")
        translation = translate(
            term.title, context=self.portal.REQUEST, target_language="fr"
        )
        msg = "Condition title was not translated"
        self.assertEquals(translation, u"Condition de création TEST", msg)

    def test_start_conditions_vocabulary_factory_registration(self):
        """
        Content types voc factory should be registered as a named utility.
        """
        factory_name = "schedule.start_conditions"
        self.assertTrue(queryUtility(IVocabularyFactory, factory_name))

    def test_start_conditions_vocabulary_values(self):
        """
        Test some start_conditions values.
        """
        voc_name = "schedule.start_conditions"
        voc_factory = getUtility(IVocabularyFactory, voc_name)
        vocabulary = voc_factory(self.task_config)
        self.assertTrue("schedule.test_start_condition" in vocabulary)

        term = vocabulary.getTerm("schedule.test_start_condition")
        translation = translate(
            term.title, context=self.portal.REQUEST, target_language="fr"
        )
        msg = "Condition title was not translated"
        self.assertEquals(translation, u"Condition de démarrage TEST", msg)

    def test_end_conditions_vocabulary_factory_registration(self):
        """
        Content types voc factory should be registered as a named utility.
        """
        factory_name = "schedule.end_conditions"
        self.assertTrue(queryUtility(IVocabularyFactory, factory_name))

    def test_end_conditions_vocabulary_values(self):
        """
        Test some end_conditions values.
        """
        voc_name = "schedule.end_conditions"
        voc_factory = getUtility(IVocabularyFactory, voc_name)
        vocabulary = voc_factory(self.task_config)
        self.assertTrue("schedule.test_end_condition" in vocabulary)

        term = vocabulary.getTerm("schedule.test_end_condition")
        translation = translate(
            term.title, context=self.portal.REQUEST, target_language="fr"
        )
        msg = "Condition title was not translated"
        self.assertEquals(translation, u"Condition de fin TEST", msg)

    def test_start_date_vocabulary_factory_registration(self):
        """
        Content types voc factory should be registered as a named utility.
        """
        factory_name = "schedule.start_date"
        self.assertTrue(queryUtility(IVocabularyFactory, factory_name))

    def test_start_date_vocabulary_values(self):
        """
        Test some due_date values.
        """
        voc_name = "schedule.start_date"
        voc_factory = getUtility(IVocabularyFactory, voc_name)
        vocabulary = voc_factory(self.task_config)
        self.assertTrue("schedule.start_date.creation_date" in vocabulary)

        term = vocabulary.getTerm("schedule.start_date.creation_date")
        translation = translate(
            term.title, context=self.portal.REQUEST, target_language="fr"
        )
        msg = "Condition title was not translated"
        self.assertEquals(translation, u"Date de création du dossier", msg)

    def test_task_owner_vocabulary_factory_registration(self):
        """
        Content types voc factory should be registered as a named utility.
        """
        factory_name = "schedule.task_owner"
        self.assertTrue(queryUtility(IVocabularyFactory, factory_name))


class TestMacroTaskVocabularies(MacroTaskScheduleIntegrationTestCase):
    """
    Test AutomatedMacroTask field vocabularies registration and values.
    """

    def test_macrotask_creation_conditions_vocabulary_factory_registration(self):
        """
        Content types voc factory should be registered as a named utility.
        """
        factory_name = "schedule.macrotask_creation_conditions"
        self.assertTrue(queryUtility(IVocabularyFactory, factory_name))

    def test_macrotask_creation_conditions_vocabulary_values(self):
        """
        Test some creation_conditions values.
        """
        voc_name = "schedule.macrotask_creation_conditions"
        voc_factory = getUtility(IVocabularyFactory, voc_name)
        vocabulary = voc_factory(self.macrotask_config)
        self.assertTrue("schedule.create_if_subtask_can_be_created" in vocabulary)
        self.assertTrue("schedule.create_if_all_subtasks_can_be_created" in vocabulary)

        term = vocabulary.getTerm("schedule.create_if_subtask_can_be_created")
        translation = translate(
            term.title, context=self.portal.REQUEST, target_language="fr"
        )
        msg = "Condition title was not translated"
        self.assertEquals(translation, u"Créer dès qu'une sous-tâche est créable", msg)

        term = vocabulary.getTerm("schedule.create_if_all_subtasks_can_be_created")
        translation = translate(
            term.title, context=self.portal.REQUEST, target_language="fr"
        )
        msg = "Condition title was not translated"
        self.assertEquals(
            translation, u"Créer si toutes les sous-tâche sont créables", msg
        )

    def test_macrotask_start_conditions_vocabulary_factory_registration(self):
        """
        Content types voc factory should be registered as a named utility.
        """
        factory_name = "schedule.macrotask_start_conditions"
        self.assertTrue(queryUtility(IVocabularyFactory, factory_name))

    def test_macrotask_start_conditions_vocabulary_values(self):
        """
        Test some start_conditions values.
        """
        voc_name = "schedule.macrotask_start_conditions"
        voc_factory = getUtility(IVocabularyFactory, voc_name)
        vocabulary = voc_factory(self.macrotask_config)
        self.assertTrue("schedule.start_if_subtask_started" in vocabulary)
        self.assertTrue("schedule.start_if_all_subtasks_started" in vocabulary)

        term = vocabulary.getTerm("schedule.start_if_subtask_started")
        translation = translate(
            term.title, context=self.portal.REQUEST, target_language="fr"
        )
        msg = "Condition title was not translated"
        self.assertEquals(
            translation, u"Démarrer dès qu'une sous-tâche est démarrée", msg
        )

        term = vocabulary.getTerm("schedule.start_if_all_subtasks_started")
        translation = translate(
            term.title, context=self.portal.REQUEST, target_language="fr"
        )
        msg = "Condition title was not translated"
        self.assertEquals(
            translation, u"Démarrer si toutes les sous-tâche sont démarrées", msg
        )

    def test_macrotask_end_conditions_vocabulary_factory_registration(self):
        """
        Content types voc factory should be registered as a named utility.
        """
        factory_name = "schedule.macrotask_end_conditions"
        self.assertTrue(queryUtility(IVocabularyFactory, factory_name))

    def test_macrotask_end_conditions_vocabulary_values(self):
        """
        Test some end_conditions values.
        """
        voc_name = "schedule.macrotask_end_conditions"
        voc_factory = getUtility(IVocabularyFactory, voc_name)
        vocabulary = voc_factory(self.macrotask_config)
        self.assertTrue("schedule.test_end_condition" in vocabulary)

        term = vocabulary.getTerm("schedule.test_end_condition")
        translation = translate(
            term.title, context=self.portal.REQUEST, target_language="fr"
        )
        msg = "Condition title was not translated"
        self.assertEquals(translation, u"Condition de fin TEST", msg)

    def test_macrotask_start_date_vocabulary_factory_registration(self):
        """
        Content types voc factory should be registered as a named utility.
        """
        factory_name = "schedule.macrotask_start_date"
        self.assertTrue(queryUtility(IVocabularyFactory, factory_name))

    def test_macrotask_start_date_vocabulary_values(self):
        """
        Test some due_date values.
        """
        voc_name = "schedule.macrotask_start_date"
        voc_factory = getUtility(IVocabularyFactory, voc_name)
        vocabulary = voc_factory(self.macrotask_config)
        self.assertTrue("schedule.start_date.subtask_highest_due_date" in vocabulary)

        term = vocabulary.getTerm("schedule.start_date.subtask_highest_due_date")
        translation = translate(
            term.title, context=self.portal.REQUEST, target_language="fr"
        )
        msg = "Condition title was not translated"
        self.assertEquals(
            translation, u"La plus haute date d'échéance parmi les sous-tâches", msg
        )
