# -*- coding: utf-8 -*-
"""
imio.schedule
-------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from imio.schedule import utils
from imio.schedule import _


class WorkingDaysVocabularyFactory(object):
    def __call__(self, context):
        return utils.dict_list_2_vocabulary(
            [
                {"monday": _(u"Monday")},
                {"tuesday": _(u"Tuesday")},
                {"wednesday": _(u"Wednesday")},
                {"thursday": _(u"Thursday")},
                {"friday": _(u"Friday")},
                {"saturday": _(u"Saturday")},
                {"sunday": _(u"Sunday")},
            ]
        )


class AdditionalDelayTypeVocabularyFactory(object):
    def __call__(self, context):
        return utils.dict_list_2_vocabulary(
            [
                {"absolute": _(u"Absolute")},
                {"working_days": _(u"Working days")},
            ]
        )
