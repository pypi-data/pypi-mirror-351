# -*- coding: utf-8 -*-

from imio.schedule.content.subform_context_choice import SubFormContextChoice
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from z3c.form.interfaces import IObjectFactory
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import Interface
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.interfaces import IObject
from zope.schema.interfaces import IVocabularyFactory


@implementer(IFieldDeserializer)
@adapter(IObject, IDexterityContent, IBrowserRequest)
class ObjectDeserializer(DefaultFieldDeserializer):
    def __call__(self, value):
        if not self.field.schema:
            return self._default_call(value)
        adapter_name = "{0}.{1}".format(
            self.field.schema.__module__,
            self.field.schema.__name__,
        )
        factory_adapter = queryMultiAdapter(
            (Interface, Interface, Interface, Interface),
            IObjectFactory,
            name=adapter_name,
        )
        if not factory_adapter:
            return self._default_call(value)
        for fieldname in self.field.schema:
            field = self.field.schema[fieldname]
            if isinstance(field, SubFormContextChoice):
                self._set_vocabulary(field)
        return factory_adapter.factory(**value)

    def _set_vocabulary(self, field):
        """Ensure that vocabularies have the right values
        to avoid errors during validation"""
        vocabulary_factory = getUtility(
            IVocabularyFactory,
            name=field.vocabulary_name,
        )
        field.vocabulary = vocabulary_factory(self.context)

    def _default_call(self, value):
        return super(ObjectDeserializer, self).__call__(value)
