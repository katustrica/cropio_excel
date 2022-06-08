from datetime import datetime, time, timedelta
from unittest import TestCase

from main import create_waybill_excels, get_waybill_excel_infos, create_production_excels


def shifts(start_time: datetime, end_time: datetime):
    day = time(6, 00)
    night = time(22, 00)
    day_shift, night_shift = 0, 0
    while (start_time + timedelta(hours=1)) <= end_time:
        if night >= (start_time + timedelta(hours=1)).time() > day:
            day_shift += 1
        else:
            night_shift += 1
        start_time += timedelta(hours=1)

    return day_shift, night_shift


class TestDailyShifts(TestCase):
    def test_only_day_shift(self):
        info_result = get_waybill_excel_infos([8017])[0]
        self.assertEqual(info_result.day_shift, 8)
        self.assertEqual(info_result.night_shift, 0)

    def test_only_day_shift2(self):
        info_result = get_waybill_excel_infos([9205])[0]
        self.assertEqual(info_result.day_shift, 12)
        self.assertEqual(info_result.night_shift, 0)


class TestNightShifts(TestCase):
    def test_day_and_night_shift1(self):
        info_result = get_waybill_excel_infos([9247])[0]
        self.assertEqual(info_result.day_shift, 16)
        self.assertEqual(info_result.night_shift, 1)

    def test_day_and_night_shift2(self):
        info_result = get_waybill_excel_infos([9222])[0]
        self.assertEqual(info_result.day_shift, 8)
        self.assertEqual(info_result.night_shift, 3)

    def test_day_and_night_shift3(self):
        info_result = get_waybill_excel_infos([9223])[0]
        self.assertEqual(info_result.day_shift, 8)
        self.assertEqual(info_result.night_shift, 3)

    def test_day_and_night_shift4(self):
        info_result = get_waybill_excel_infos([9200])[0]
        self.assertEqual(info_result.day_shift, 4)
        self.assertEqual(info_result.night_shift, 8)

    def test_not_whole_night_shift(self):
        day_shift, night_shift = shifts(
            datetime(2022, 5, 5, 5, 10), datetime(2022, 5, 5, 11, 10)
        )
        self.assertEqual(day_shift, 6)
        self.assertEqual(night_shift, 0)


class TestRoundedShifts(TestCase):
    def test_rounded_shift(self):
        info_result = get_waybill_excel_infos([9111])[0]
        self.assertEqual(info_result.day_shift, 4)
        self.assertEqual(info_result.night_shift, 8)

    def test_rounded_shift2(self):
        day_shift, night_shift = shifts(
            datetime(2022, 5, 5, 5, 0), datetime(2022, 5, 5, 11, 0)
        )
        self.assertEqual(day_shift, 5)
        self.assertEqual(night_shift, 1)


class TestProduction(TestCase):
    def test_production(self):
        info_result = create_production_excels([9358, 11009])

