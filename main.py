""" Создание файлов """
import asyncio
import itertools
from collections import defaultdict
from datetime import datetime
from typing import Optional

import aiohttp

from datas import PlanTask, Task
from excel import (ExcelInfo, ExcelProductionInfo, KamazExcel, ProductionExcel,
                   WaybillExcel)
from info import DEBUG_LINUX

path_to_save_kamaz = (
    ".\\Путевые листы\\Камазы\\" if not DEBUG_LINUX else "Путевые листы/Камазы/"
)
path_to_save_simple = (
    ".\\Путевые листы\\Обычные\\" if not DEBUG_LINUX else "Путевые листы/Обычные/"
)
path_to_save_production = ".\\Выработка\\" if not DEBUG_LINUX else "Выработка/"


def create_waybill_excels(
    task_ids: Optional[list[int]] = None, period: Optional[list[datetime]] = None
):
    """Создать файлы Путевых листов"""
    excel_infos = asyncio.get_event_loop().run_until_complete(get_waybill_excel_infos(task_ids=task_ids, period=period))
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
    async with aiohttp.ClientSession() as session:
        futures = []
        if task_ids and not period:
            for task_id in task_ids:
                future = asyncio.ensure_future(
                    Task.construct(id_for_query=task_id, session=session)
                )
                futures.append(future)
            # futures = [asyncio.ensure_future(Task(task_id, session)) for task_id in task_ids]
        elif not task_ids and period:
            for date in period:
                future = asyncio.ensure_future(Task.get_by_day(date, session))
                futures.append(future)
            # futures = itertools.chain(*[asyncio.ensure_future(Task.get_by_day(date, session))  for date in period])
        elif not task_ids and not period:
            raise ValueError("Должен быть заполнен только один аргумент")
        tasks = await asyncio.gather(*futures)

    if not task_ids and period:
        tasks = itertools.chain(*tasks)

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
    excel_infos_by_region = asyncio.get_event_loop().run_until_complete(
        get_production_excel_infos(task_ids=task_ids, period=period)
    )
    ProductionExcel(excel_infos_by_region, path_to_save=path_to_save_production)


async def get_production_excel_infos(
    task_ids: Optional[list[int]] = None, period: Optional[list[datetime]] = None
):
    excel_infos_by_region = defaultdict(list)
    tasks = []

    async with aiohttp.ClientSession() as session:
        futures = []
        if task_ids and not period:
            for task_id in task_ids:
                future = asyncio.ensure_future(
                    PlanTask.construct(id_for_query=task_id, session=session)
                )
                futures.append(future)
            # futures = [asyncio.ensure_future(Task(task_id, session)) for task_id in task_ids]
        elif not task_ids and period:
            for date in period:
                future = asyncio.ensure_future(PlanTask.get_by_day(date, session))
                futures.append(future)
            # futures = itertools.chain(*[asyncio.ensure_future(Task.get_by_day(date, session))  for date in period])
        elif not task_ids and not period:
            raise ValueError("Должен быть заполнен только один аргумент")
        tasks = await asyncio.gather(*futures)

    if not task_ids and period:
        tasks = itertools.chain(*tasks)

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
                unit='Км',
                day_covered_hour='',
                night_covered_hour='',
                day_covered_work='',
                night_covered_work='',
                day_distance_hour=task.day_distance_hour,
                night_distance_hour=task.night_distance_hour,
                day_distance_work=task.day_distance_work,
                night_distance_work=task.night_distance_work,
                is_transfer=True,
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
                field_work_area=round(task_field_mapping.work_area),
                unit='Га',
                day_covered_hour=task_field_mapping.day_covered_hour,
                night_covered_hour=task_field_mapping.night_covered_hour,
                day_covered_work=task_field_mapping.day_covered_work,
                night_covered_work=task_field_mapping.night_covered_work,
                day_distance_hour=task_field_mapping.day_distance_hour,
                night_distance_hour=task_field_mapping.night_distance_hour,
                day_distance_work=task_field_mapping.day_distance_work,
                night_distance_work=task_field_mapping.night_distance_work,
            )
            excel_infos_by_region[region].append(excel_info)
    return excel_infos_by_region
