# -*- coding: utf-8 -*-

from datetime import datetime
from mock import Mock
from DateTime import DateTime

from imio.schedule.content.delay import CalculationDefaultDelay
from imio.schedule.testing import ExampleScheduleFunctionalTestCase
from imio.schedule.tests.due_date import ContainerCreationDate


class TestCalculationDelay(ExampleScheduleFunctionalTestCase):
    def setUp(self):
        super(TestCalculationDelay, self).setUp()
        self._start_date = ContainerCreationDate.start_date

    def tearDown(self):
        ContainerCreationDate.start_date = self._start_date
        super(TestCalculationDelay, self).tearDown()

    @property
    def delay_adapter(self):
        return CalculationDefaultDelay(self.task_container, self.task)

    def test_start_date(self):
        """Test different cases for 'start_date' property"""
        current_date = datetime.now().date()
        self.assertEqual(current_date, self.delay_adapter.start_date)

        ContainerCreationDate.start_date = Mock(return_value=DateTime())
        self.assertEqual(current_date, self.delay_adapter.start_date)

        ContainerCreationDate.start_date = Mock(return_value=None)
        self.assertEqual(
            datetime(9999, 1, 1).date(),
            self.delay_adapter.start_date,
        )

    def test_delta(self):
        """Test 'delta' property"""
        adapter = self.delay_adapter

        adapter.calculate_delay = Mock(return_value=0)
        self.assertEqual(0, adapter.delta)

        adapter.calculate_delay = Mock(return_value=10)
        self.assertEqual(10, adapter.delta)

    def test_due_date(self):
        """Test 'due_date' property"""
        adapter = self.delay_adapter
        ContainerCreationDate.start_date = Mock(
            return_value=datetime(2016, 1, 1).date()
        )
        due_date = datetime(2016, 1, 11).date()
        adapter.calculate_delay = Mock(return_value=10)

        self.assertEqual(due_date, adapter.due_date)

    def test_compute_due_date(self):
        """Test 'compute_due_date' method"""
        adapter = self.delay_adapter
        base_date = datetime(2016, 1, 1).date()
        due_date = datetime(2016, 1, 11).date()
        adapter.calculate_delay = Mock(return_value=10)

        self.assertEqual(due_date, adapter.compute_due_date(base_date))