""" Создание файлов """
from excel import ExcelInfo, WaybillExcel, KamazExcel
from datas import Task


def create_excels(task_ids: list[int]):
    """ Создать файлы """
    excel_infos = get_excel_infos(task_ids)
    simple_excel_infos, kamaz_excel_infos = [], []
    for excel_info in excel_infos:
        is_kamaz = next((True for name in ['камаз', 'уаз', 'газ'] if name in excel_info.machine_name.lower()), False)
        if is_kamaz:
            kamaz_excel_infos.append(excel_info)
        else:
            simple_excel_infos.append(excel_info)

    if simple_excel_infos:
        WaybillExcel(simple_excel_infos, path_to_save='.\\Путевые листы\\Обычные\\')
    if kamaz_excel_infos:
        KamazExcel(kamaz_excel_infos, path_to_save='.\\Путевые листы\\Камазы\\')


def get_excel_infos(task_ids: list[int]):
    excel_infos = []
    for task_id in task_ids:
        task = Task(task_id)
        start, end = task.start, task.end
        machine = task.machine
        excel_info = ExcelInfo(
            task=str(task_id),
            start_time=start.time,
            start_day=start.day,
            start_month=start.month,
            start_year=start.year,
            end_time=end.time,
            end_day=end.day,
            end_month=end.month,
            end_year=end.year,
            machine_name=machine.name,
            machine_number=machine.number,
            machine_region=machine.region,
            driver=task.driver.driver_name,
            driver_info=task.driver.additional_info,
            work=task.work_type.work_type_name,
            implement=task.implement.implement_name,
            implement_number=task.implement.registration_number,
        )
        excel_infos.append(excel_info)
    return excel_infos