""" Создание файла по полученным данным """
import pathlib
import sys
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass

import openpyxl as xl
from openpyxl.workbook.protection import WorkbookProtection

Cells = namedtuple("CELLS", ("name", "page_num", "cell"))
SIMPLE_CELLS = (
    Cells("task", 0, "F1"),
    Cells("time", 0, "C2"),
    Cells("machine_name", 0, "B4"),
    Cells("machine_region", 0, "B1"),
    Cells("driver", 0, "B3"),
    Cells("work", 0, "B6"),
    Cells("implement", 0, "B5"),
)
KAMAZ_CELLS = (
    Cells("task", 0, "DN1"),
    Cells("start_day", 0, "BG5"),
    Cells("start_month", 0, "BP5"),
    Cells("start_year", 0, "CL5"),
    Cells("machine_name", 0, "Q13"),
    Cells("machine_number", 0, "AB14"),
    Cells("machine_region", 0, "Q6"),
    Cells("driver", 0, "I15"),
    Cells("driver_info", 0, "P17"),
    Cells("driver_short_1", 0, "CO46"),
    Cells("driver_short_2", 0, "CF52"),
    Cells("driver_short_3", 0, "DA74"),
    Cells("work", 0, "W30"),
    Cells("implement_number", 0, "AR21"),
)

# FILE_LOCATION_SIMPLE = f'{sys._MEIPASS}/def/def_simple.xlsx'
# FILE_LOCATION_KAMAZ = f'{sys._MEIPASS}/def/def_kamaz.xlsx'
FILE_LOCATION_SIMPLE = f"def_simple.xlsx"
FILE_LOCATION_KAMAZ = f"def_kamaz.xlsx"


@dataclass
class ExcelInfo:
    """dataclass for storing info about task"""

    task: str
    start_time: str
    start_day: str
    start_month: str
    start_year: str
    end_time: str
    end_day: str
    end_month: str
    end_year: str
    machine_name: str
    machine_number: str
    machine_region: str
    driver: str
    driver_info: str
    work: str
    implement: str
    implement_number: str
    fuel_consumption: float
    covered_area: float
    work_distance: float
    road_distance: float
    day_shift: int
    night_shift: int


class ExcelFile(ABC):
    """Класс для создания файла по полученным данным"""

    def __init__(
        self, infos: list[ExcelInfo], file_location: str, path_to_save: str = ".\\"
    ):
        """Создаем копию дефолтного файла при создании экземпляра"""
        self.infos = infos
        # Читаем дефолтную эксельку
        workbook = xl.load_workbook(file_location)
        # Заполняем её
        self.fill_file(workbook)
        # Сохраняем
        self.save_file(workbook, path_to_save)

    @abstractmethod
    def fill_file(self, workbook: xl.workbook.Workbook):
        """Заполнить данными новую excel"""
        raise NotImplemented

    def save_file(self, workbook: xl.workbook.Workbook, path_to_save: str):
        file_name = f'{", ".join(map(str, self.task_ids))}.xlsx'
        path = f"{path_to_save}{file_name}"
        pathlib.Path(path_to_save).mkdir(parents=True, exist_ok=True)
        # workbook.security = WorkbookProtection(workbookPassword='imax', lockStructure=True)
        try:
            workbook.save(path)
        except PermissionError:
            raise PermissionError("Закройте файл и попробуйте заново")

    @property
    def task_ids(self):
        """Получить ид таск"""
        return tuple(info.task for info in self.infos)


class WaybillExcel(ExcelFile):
    """Класс для создания обычного файла по полученным данным"""

    def __init__(
        self,
        infos: list[ExcelInfo],
        file_location: str = FILE_LOCATION_SIMPLE,
        path_to_save: str = ".\\",
    ):
        """Создаем копию дефолтного файла при создании экземпляра"""
        self.cells = SIMPLE_CELLS
        super().__init__(infos, file_location, path_to_save)

    def fill_file(self, workbook: xl.workbook.Workbook):
        """Заполнить данными новую excel"""
        def_worksheet = workbook["Лист1"]

        for info in self.infos:
            # Создаем и заполняем новый WorkSheet с именем таски
            worksheet = workbook.copy_worksheet(def_worksheet)
            worksheet.title = info.task
            for name, _, pos in self.cells:
                if name == "time":
                    value = (
                        f"{info.start_day} {info.start_month} {info.start_year}г. {info.start_time} - "
                        f"{info.end_day} {info.end_month} {info.end_year}г. {info.end_time}"
                    )
                else:
                    value = getattr(info, name)

                worksheet[pos] = value

        # Удаляем дефолтную страницу
        workbook.remove(def_worksheet)


class KamazExcel(ExcelFile):
    """Класс для создания файла для камазов по полученным данным"""

    def __init__(
        self,
        infos: list[ExcelInfo],
        file_location: str = FILE_LOCATION_KAMAZ,
        path_to_save: str = ".\\",
    ):
        """Создаем копию дефолтного файла при создании экземпляра"""
        self.cells = KAMAZ_CELLS
        super().__init__(infos, file_location, path_to_save)

    def fill_file(self, workbook: xl.workbook.Workbook):
        """Заполнить данными новую excel"""
        def_worksheets = (workbook["Лист1"], workbook["Лист2"])

        for num_info, info in enumerate(self.infos):
            # Создаем и заполняем новый WorkSheet с именем таски
            worksheets = tuple(
                workbook.copy_worksheet(sheet) for sheet in def_worksheets
            )
            for num, sheet in enumerate(worksheets):
                sheet.title = f"{info.task} стр. {num+1}"

            for name, sheet_num, pos in self.cells:
                if "driver_short" in name:
                    if info.driver:
                        surname, name, middlename = info.driver.split(" ")
                        value = f"{surname} {name[0]}. {middlename[0]}."
                    else:
                        value = ""
                else:
                    value = getattr(info, name)
                if value:
                    worksheets[sheet_num][pos] = value

        # Удаляем дефолтные страницы
        for sheet in def_worksheets:
            workbook.remove(sheet)
