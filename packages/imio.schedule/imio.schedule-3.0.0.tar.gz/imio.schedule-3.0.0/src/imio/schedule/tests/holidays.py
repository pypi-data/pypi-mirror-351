# -*- coding: utf-8 -*-

from datetime import date
from zope.interface import implements

from imio.schedule.interfaces import ICalendarExtraHolidays


class CalendarExtraHolidays(object):
    implements(ICalendarExtraHolidays)

    def get_holidays(self, year):
        return ((date(2017, 2, 1), "Test holidays"),)
