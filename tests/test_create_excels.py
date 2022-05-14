from unittest import TestCase

from main import create_excels, get_excel_infos


class TestCreateExcels(TestCase):
    def test_get_excel_info(self):
        info_result = get_excel_infos([8083])[0]
        self.assertEqual(info_result.task, "8083")
        self.assertEqual(info_result.start_time, "06:00:00")
        self.assertEqual(info_result.start_day, "01")
        self.assertEqual(info_result.start_month, "Март")
        self.assertEqual(info_result.start_year, "2022")
        self.assertEqual(info_result.end_time, "18:00:00")
        self.assertEqual(info_result.end_day, "01")
        self.assertEqual(info_result.end_month, "Март")
        self.assertEqual(info_result.end_year, "2022")
        self.assertEqual(info_result.machine_name, "John Deere -1081 AB")
        self.assertEqual(info_result.machine_number, "1081 АВ")
        self.assertEqual(info_result.machine_region, 'ООО "БИО-АГРО"')
        self.assertEqual(info_result.driver, "Абдулгалимов Ренат Хакимович")
        self.assertEqual(
            info_result.work,
            "Боронование глуб.рыхление",
        )
        self.assertEqual(info_result.implement, 'пружиная "VELES" БТ-!')

    def test_create_excels(self):
        create_excels([7771])
