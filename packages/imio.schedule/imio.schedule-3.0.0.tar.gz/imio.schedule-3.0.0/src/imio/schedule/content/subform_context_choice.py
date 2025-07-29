# -*- coding: utf-8 -*-

from z3c.form import term
from z3c.form.browser.select import SelectWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import FieldWidget
from zope import schema
from zope.component import adapter
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory


class ISubFormContextChoice(Interface):
    pass


class SubFormContextChoice(schema.Choice):
    implements(ISubFormContextChoice)

    def __init__(self, *args, **kwargs):
        kwargs["values"] = []
        vocabulary_name = kwargs.pop("vocabulary")
        super(SubFormContextChoice, self).__init__(*args, **kwargs)
        self.vocabulary_name = vocabulary_name


class SubFormContextSelectWidget(SelectWidget):
    def update(self):
        super(SubFormContextSelectWidget, self).update()
        self.field.vocabulary = self.terms.terms


@adapter(ISubFormContextChoice, IFormLayer)
@implementer(IFieldWidget)
def subform_context_select_field_widget(field, request):
    return FieldWidget(field, SubFormContextSelectWidget(request))


def subform_context_choice_terms(context, request, form, field, widget):
    if hasattr(form, "parentForm"):
        context = form.parentForm.context
    field = field.bind(context)
    voc = getUtility(IVocabularyFactory, name=field.vocabulary_name)
    return term.ChoiceTermsVocabulary(
        context,
        request,
        form,
        field,
        voc(context),
        widget,
    )
