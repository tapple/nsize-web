from datetime import datetime, date
import unittest

from django.test import TestCase
from .models import fiscal_date, PST, UTC


class FiscalDateTestCase(unittest.TestCase):

    def test_winter_time_PST_1(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 1, 1, 3, 00), PST),
            date(2017, 1, 1))

    def test_winter_time_PST_2(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 1, 1, 2, 59), PST),
            date(2016, 12, 31))

    def test_spring_forward_PST_1(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 3, 12, 3, 00), PST),
            date(2017, 3, 12))

    def test_spring_forward_PST_2(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 3, 12, 2, 59), PST),
            date(2017, 3, 12))

    def test_spring_forward_PST_3(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 3, 12, 2, 00), PST),
            date(2017, 3, 12))

    def test_spring_forward_PST_4(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 3, 12, 1, 59), PST),
            date(2017, 3, 11))

    def test_summer_time_PST_1(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 6, 1, 3, 00), PST),
            date(2017, 6, 1))

    def test_summer_time_PST_2(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 6, 1, 2, 59), PST),
            date(2017, 5, 31))

    def test_fall_back_PST_1(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 11, 5, 3, 00), PST),
            date(2017, 11, 5))

    def test_fall_back_PST_2(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 11, 5, 2, 59), PST),
            date(2017, 11, 4))

    def test_winter_time_UTC_1(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 1, 1, 11, 00), UTC),
            date(2017, 1, 1))

    def test_winter_time_UTC_2(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 1, 1, 10, 59), UTC),
            date(2016, 12, 31))

    def test_spring_forward_UTC_1(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 3, 12, 11, 00), UTC),
            date(2017, 3, 12))

    def test_spring_forward_UTC_2(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 3, 12, 10, 59), UTC),
            date(2017, 3, 12))

    def test_summer_time_UTC_1(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 6, 1, 10, 00), UTC),
            date(2017, 6, 1))

    def test_summer_time_UTC_2(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 6, 1, 9, 59), UTC),
            date(2017, 5, 31))

    def test_fall_back_UTC_1(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 11, 5, 11, 00), UTC),
            date(2017, 11, 5))

    def test_fall_back_UTC_2(self):
        self.assertEqual(
            fiscal_date(datetime(2017, 11, 5, 10, 59), UTC),
            date(2017, 11, 4))

