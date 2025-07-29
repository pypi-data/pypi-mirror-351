# -*- coding: utf-8 -*-

from imio.schedule.content.condition import CreationCondition
from imio.schedule.content.condition import EndCondition
from imio.schedule.content.condition import FreezeCondition
from imio.schedule.content.condition import StartCondition
from imio.schedule.content.condition import ThawCondition


class TestCreationCondition(CreationCondition):
    """
    Test task start condition.
    """

    def evaluate(self):
        return "Should start"


class TestNegativeCreationCondition(CreationCondition):
    """
    Test task start condition.
    """

    def evaluate(self):
        return False


class TestStartCondition(StartCondition):
    """
    Test task start condition.
    """

    def evaluate(self):
        return "Should start"


class TestNegativeStartCondition(StartCondition):
    """
    Test task start condition.
    """

    def evaluate(self):
        return False


class TestEndCondition(EndCondition):
    """
    Test task end condition.
    """

    def evaluate(self):
        return "Should end"


class TestNegativeEndCondition(EndCondition):
    """
    Test task end condition.
    """

    def evaluate(self):
        return False


class TestFreezeCondition(FreezeCondition):
    """
    Test task freeze condition.
    """

    def evaluate(self):
        return "Should freeze"


class TestNegativeFreezeCondition(FreezeCondition):
    """
    Test task freeze condition.
    """

    def evaluate(self):
        return False


class TestThawCondition(ThawCondition):
    """
    Test task thaw condition.
    """

    def evaluate(self):
        return "Should thaw"


class TestNegativeThawCondition(ThawCondition):
    """
    Test task thaw condition.
    """

    def evaluate(self):
        return False
