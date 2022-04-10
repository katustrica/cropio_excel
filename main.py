""" Создание файлов """
from excel import ExcelInfo, WaybillExcel
from datas import Task

def create_excels(task_ids: list[int]):
    """ Создать файлы """
    excel_infos = []
    for task_id in task_ids:
        task = Task(task_id)
        excel_info = ExcelInfo(str(task_id),
                               task.time,
                               task.machine.name,
                               task.machine.region,
                               task.driver.driver_name,
                               task.work_type.work_type_name,
                               task.implement.implement_name)
        excel_infos.append(excel_info)

    WaybillExcel(excel_infos, '.\\Путевые листы\\')