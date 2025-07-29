# -*- coding: utf-8 -*-

from imio.schedule.content.object_factories import CreationConditionObject
from imio.schedule.content.object_factories import EndConditionObject
from imio.schedule.content.object_factories import FreezeConditionObject
from imio.schedule.content.object_factories import MacroCreationConditionObject
from imio.schedule.content.object_factories import MacroEndConditionObject
from imio.schedule.content.object_factories import MacroFreezeConditionObject
from imio.schedule.content.object_factories import MacroRecurrenceConditionObject
from imio.schedule.content.object_factories import MacroStartConditionObject
from imio.schedule.content.object_factories import MacroThawConditionObject
from imio.schedule.content.object_factories import RecurrenceConditionObject
from imio.schedule.content.object_factories import StartConditionObject
from imio.schedule.content.object_factories import ThawConditionObject
from plone.restapi.interfaces import IJsonCompatible
from zope.component import adapter
from zope.interface import implementer


def base_converter(value):
    return value.__dict__


@adapter(CreationConditionObject)
@implementer(IJsonCompatible)
def creation_condition_converter(value):
    return base_converter(value)


@adapter(StartConditionObject)
@implementer(IJsonCompatible)
def start_condition_converter(value):
    return base_converter(value)


@adapter(EndConditionObject)
@implementer(IJsonCompatible)
def end_condition_converter(value):
    return base_converter(value)


@adapter(FreezeConditionObject)
@implementer(IJsonCompatible)
def freeze_condition_converter(value):
    return base_converter(value)


@adapter(ThawConditionObject)
@implementer(IJsonCompatible)
def thaw_condition_converter(value):
    return base_converter(value)


@adapter(RecurrenceConditionObject)
@implementer(IJsonCompatible)
def recurrence_condition_converter(value):
    return base_converter(value)


@adapter(MacroCreationConditionObject)
@implementer(IJsonCompatible)
def macro_creation_condition_converter(value):
    return base_converter(value)


@adapter(MacroStartConditionObject)
@implementer(IJsonCompatible)
def macro_start_condition_converter(value):
    return base_converter(value)


@adapter(MacroEndConditionObject)
@implementer(IJsonCompatible)
def macro_end_condition_converter(value):
    return base_converter(value)


@adapter(MacroFreezeConditionObject)
@implementer(IJsonCompatible)
def macro_freeze_condition_converter(value):
    return base_converter(value)


@adapter(MacroThawConditionObject)
@implementer(IJsonCompatible)
def macro_thaw_condition_converter(value):
    return base_converter(value)


@adapter(MacroRecurrenceConditionObject)
@implementer(IJsonCompatible)
def macro_recurrence_condition_converter(value):
    return base_converter(value)
