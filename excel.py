""" Создание файла по полученным данным """
from datas import ExcelInfo

import openpyxl as xl

CELLS = {
    'task': 'F1',
    'time': 'C2',
    'machine': 'B4',
    'region': 'B1',
    'driver': 'B3',
    'work': 'B6',
    'implement': 'B5',
}

DEFAULT_FILE_LOCATION = 'def.xlsx'

class WaybillExcel():
    """ Класс для создания файла по полученным данным """
    def __init__(self, infos: list[ExcelInfo], path_to_save: str | None = None):
        """ Создаем копию дефолтного файла при создании экземпляра """

        self.infos = infos
        # Читаем дефолтную эксельку
        workbook = xl.load_workbook(DEFAULT_FILE_LOCATION)
        # Заполняем её
        self.fill_waybill(workbook)
        # Сохраняем
        file_name = f'{", ".join(map(str, self.task_ids))}.xlsx'
        path = f'{path_to_save}\\{file_name}' if path_to_save else file_name
        workbook.save(path)

    def fill_waybill(self, workbook: xl.workbook.Workbook):
        """ Заполнить данными новую excel """
        def_worksheet = workbook['Лист1']

        for info in self.infos:
            # Создаем и заполняем новый WorkSheet с именем таски
            worksheet = workbook.copy_worksheet(def_worksheet)
            worksheet.title = info.task
            for name, pos in CELLS.items():
                value = getattr(info, name)
                worksheet[pos] = value

        # Удаляем дефолтную страницу
        workbook.remove(def_worksheet)

    @property
    def task_ids(self):
        """ Получить ид таск """
        return tuple(info.task for info in self.infos)
