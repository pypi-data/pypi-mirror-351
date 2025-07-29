# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from z3c.table.interfaces import IColumn

from zope.interface import Interface


class IDisplayTaskStatus(Interface):
    """
    Adapts a task instance into a z3c table cell
    displaying the task status.
    """

    def render(self):
        """ """


class ISimpleDisplayTaskStatus(Interface):
    """
    Adapts a task instance into a z3c table cell
    displaying the task status.
    """

    def render(self):
        """ """


class IStatusColumn(IColumn):
    """Marker interface for Task Status columns."""
