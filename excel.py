""" Создание файла по полученным данным """
import os
import pathlib
import sys
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass
from posixpath import abspath

import openpyxl as xl
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.workbook.protection import WorkbookProtection

Cells = namedtuple("CELLS", ("name", "page_num", "cell"))
ProductionCells = namedtuple(
    "PRODUCTIONCELLS", ("name", "page_num", "cell_letter", "start_cell_row")
)

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

PRODUCTION_CELLS = (
    ProductionCells("date", 0, "A", 2),
    ProductionCells("crop_name", 0, "B", 2),
    ProductionCells("field_name", 0, "C", 2),
    ProductionCells("field_area", 0, "D", 2),
    ProductionCells("work", 0, "E", 2),
    ProductionCells("machine_name", 0, "G", 2),
    ProductionCells("implement", 0, "H", 2),
    ProductionCells("driver", 0, "J", 2),
    ProductionCells("field_work_area", 0, "K", 2),
    ProductionCells("road_distance", 0, "L", 2),
    # ProductionCells("day_shift", 0, 'M', 2),
    # ProductionCells("night_shift", 0, 'N', 2),
    ProductionCells("task", 0, "M", 2),
)
PRODUCTION_TASK_CELLS = (
    ProductionCells("task", 0, "A", 3),
    ProductionCells("date", 0, "B", 3),
    ProductionCells("driver", 0, "C", 3),
    ProductionCells("machine_name", 0, "E", 3),
    ProductionCells("machine_number", 0, "F", 3),
)

try:
    abs_path = sys._MEIPASS
except:
    abs_path = os.path.abspath(".")

# FILE_LOCATION_SIMPLE = f'{abs_path}/def/def_simple.xlsx'
# FILE_LOCATION_KAMAZ = f'{abs_path}/def/def_kamaz.xlsx'
# FILE_LOCATION_PRODUCTION = f"{abs_path}/def/def_production.xlsx"
FILE_LOCATION_SIMPLE = f"def_simple.xlsx"
FILE_LOCATION_KAMAZ = f"def_kamaz.xlsx"
FILE_LOCATION_PRODUCTION = f"def_production.xlsx"

thin = Side(border_style="thin", color="000000")
alignment = Alignment(horizontal="center", vertical="center")
border = Border(top=thin, left=thin, right=thin, bottom=thin)
font = Font(size=9)


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


@dataclass
class ExcelProductionInfo(ExcelInfo):
    """dataclass for storing info about task"""

    field_name: str
    crop_name: str
    field_area: float
    field_work_area: float
    is_transfer: bool = False


class ExcelFile(ABC):
    """Класс для создания файла по полученным данным"""

    name = ""

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
        path = f"{path_to_save}{self.name}.xlsx"
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
        self.name = "Отчет по заданиям"
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
        self.name = "Отчет по заданиям КАМАЗ"
        super().__init__(infos, file_location, path_to_save)

    def fill_file(self, workbook: xl.workbook.Workbook):
        """Заполнить данными новую excel"""
        def_worksheets = (workbook["Лист1"],)

        for num_info, info in enumerate(self.infos):
            # Создаем и заполняем новый WorkSheet с именем таски
            worksheets = tuple(
                workbook.copy_worksheet(sheet) for sheet in def_worksheets
            )
            for num, sheet in enumerate(worksheets):
                sheet.title = f"{info.task}"

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


class ProductionExcel(ExcelFile):
    """Класс для создания файла для списка путевых листов по полученным данным"""

    def __init__(
        self,
        excel_infos_by_region: dict[str, ExcelProductionInfo],
        file_location: str = FILE_LOCATION_PRODUCTION,
        path_to_save: str = ".\\",
    ):
        """Создаем копию дефолтного файла при создании экземпляра"""
        self.cells = PRODUCTION_CELLS
        self.task_cells = PRODUCTION_TASK_CELLS
        self.name = "Выработка"
        super().__init__(excel_infos_by_region, file_location, path_to_save)

    def fill_file(self, workbook: xl.workbook.Workbook):
        """Заполнить данными новую excel"""
        def_worksheet_production = workbook["Выработка"]
        def_worksheet_waybill_list = workbook["Журнал ПЛ"]
        for num_info, (region, infos) in enumerate(self.infos.items()):
            # Создаем и заполняем новый WorkSheet с именем таски
            worksheet = workbook.copy_worksheet(def_worksheet_production)
            region_name = region.removeprefix("ООО").replace('"', "").strip()
            title = worksheet.title.replace("Copy", "")
            worksheet.title = f"{title} - {region_name}"

            row_number = 0
            for info in infos:

                for name, page_num, cell_letter, start_cell_row in self.cells:

                    if "date" == name:
                        if info.driver:
                            value = (
                                f"{info.start_day}.{info.start_month}.{info.start_year}"
                            )
                        else:
                            value = ""
                    else:
                        value = getattr(info, name)

                    if value:
                        pos = f"{cell_letter}{start_cell_row+row_number}"
                        cell = worksheet[pos]
                        cell.value = value
                        cell.alignment = alignment
                        cell.border = border
                        cell.font = font
                row_number += 1

        task_ids_done = []
        for num_info, (region, infos) in enumerate(self.infos.items()):
            # Создаем и заполняем новый WorkSheet с именем таски
            worksheet = workbook.copy_worksheet(def_worksheet_waybill_list)
            region_name = region.removeprefix("ООО").replace('"', "").strip()
            title = worksheet.title.replace("Copy", "")
            worksheet.title = f"{title} - {region_name}"

            row_number = 0
            for info in infos:
                if info.task in task_ids_done:
                    continue
                for name, page_num, cell_letter, start_cell_row in self.task_cells:
                    if "date" == name:
                        if info.driver:
                            value = (
                                f"{info.start_day}.{info.start_month}.{info.start_year}"
                            )
                        else:
                            value = ""
                    else:
                        value = getattr(info, name)

                    if value:
                        pos = f"{cell_letter}{start_cell_row+row_number}"
                        cell = worksheet[pos]
                        cell.value = value
                        cell.alignment = alignment
                        cell.border = border
                        cell.font = font
                row_number += 1
                task_ids_done.append(info.task)

        # Удаляем дефолтные страницы
        for sheet in (def_worksheet_production, def_worksheet_waybill_list):
            workbook.remove(sheet)
