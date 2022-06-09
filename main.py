""" Создание файлов """
import itertools
from collections import defaultdict
from datetime import datetime
from typing import Optional
import aiohttp
from async_timeout import asyncio

from datas import Task, PlanTask
from excel import ExcelInfo, KamazExcel, WaybillExcel, ExcelProductionInfo, ProductionExcel
from info import DEBUG_LINUX

path_to_save_kamaz = ".\\Путевые листы\\Камазы\\" if not DEBUG_LINUX else 'Путевые листы/Камазы/'
path_to_save_simple = ".\\Путевые листы\\Обычные\\" if not DEBUG_LINUX else 'Путевые листы/Обычные/'
path_to_save_production = ".\\Выработка\\" if not DEBUG_LINUX else 'Выработка/'

def create_waybill_excels(
    task_ids: Optional[list[int]] = None, period: Optional[list[datetime]] = None
):
    """Создать файлы Путевых листов"""
    excel_infos = get_waybill_excel_infos(task_ids=task_ids, period=period)
    simple_excel_infos, kamaz_excel_infos = [], []
    for excel_info in excel_infos:
        is_kamaz = next(
            (
                True
                for name in ["камаз", "уаз", "газ"]
                if name in excel_info.machine_name.lower()
            ),
            False,
        )
        if is_kamaz:
            kamaz_excel_infos.append(excel_info)
        else:
            simple_excel_infos.append(excel_info)

    if simple_excel_infos:
        WaybillExcel(simple_excel_infos, path_to_save=path_to_save_simple)
    if kamaz_excel_infos:
        KamazExcel(kamaz_excel_infos, path_to_save=path_to_save_kamaz)


async def get_waybill_excel_infos(
    task_ids: Optional[list[int]] = None, period: Optional[list[datetime]] = None
):
    excel_infos = []
    futures = []
    async with aiohttp.ClientSession() as session:
        if task_ids and not period:
            futures = [asyncio.ensure_future(Task(task_id, session)) for task_id in task_ids]
        elif not task_ids and period:
            futures = itertools.chain(*[asyncio.ensure_future(Task.get_by_day(date, session))  for date in period])
        elif not task_ids and not period:
            raise ValueError("Должен быть заполнен только один аргумент")
        print("ensured")
        tasks = await asyncio.gather(*futures)

    for task in tasks:
        start, end = task.start, task.end
        machine = task.machine
        excel_info = ExcelInfo(
            task=str(task.task_id),
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
            fuel_consumption=task.fuel_consumption,
            covered_area=task.covered_area,
            work_distance=task.work_distance,
            road_distance=task.road_distance,
            day_shift=task.day_shift,
            night_shift=task.night_shift,
        )
        excel_infos.append(excel_info)
    return excel_infos


def create_production_excels(
    task_ids: Optional[list[int]] = None, period: Optional[list[datetime]] = None
):
    """Создать файлы Путевых листов"""
    excel_infos_by_region = get_production_excel_infos(task_ids=task_ids, period=period)
    ProductionExcel(excel_infos_by_region, path_to_save=path_to_save_production)


def get_production_excel_infos(task_ids: Optional[list[int]] = None, period: Optional[list[datetime]] = None):
    excel_infos_by_region = defaultdict(list)
    tasks = []
    if task_ids and not period:
        tasks = [PlanTask(task_id) for task_id in task_ids]
    elif not task_ids and period:
        tasks = itertools.chain(*[PlanTask.get_by_day(date) for date in period])
    elif not task_ids and not period:
        raise ValueError("Должен быть заполнен только один аргумент")

    for task in tasks:
        start, end = task.start, task.end
        machine = task.machine
        region = machine.region

        if task.work_type.is_transfer:
            excel_info = ExcelProductionInfo(
                task=task.task_id,
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
                fuel_consumption=task.fuel_consumption,
                covered_area=task.covered_area,
                work_distance=task.work_distance,
                road_distance=task.road_distance,
                day_shift=task.day_shift,
                night_shift=task.night_shift,
                field_name='',
                crop_name='',
                field_area='',
                field_work_area='',
                is_transfer=True
            )
            excel_infos_by_region[region].append(excel_info)
            continue

        for task_field_mapping in task.task_field_mapping_list:
            excel_info = ExcelProductionInfo(
                task=task.task_id,
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
                fuel_consumption=task.fuel_consumption,
                covered_area=task.covered_area,
                work_distance=task.work_distance,
                road_distance=task.road_distance,
                day_shift=task.day_shift,
                night_shift=task.night_shift,
                field_name=task_field_mapping.name,
                crop_name=task_field_mapping.crop_name,
                field_area=task_field_mapping.area,
                field_work_area=task_field_mapping.work_area,
            )
            excel_infos_by_region[region].append(excel_info)
    return excel_infos_by_region
