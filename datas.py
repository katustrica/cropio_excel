"""for requests"""

import locale
import warnings
from datetime import datetime, time, timedelta
from functools import cache
from typing import Any, Dict, Optional, Union

import requests

from info import HEADERS, URL

locale.setlocale(locale.LC_ALL, ("ru_RU", "UTF-8"))
TRANSFER_WORK_TYPE = 4
year = 2022
REGION = {}

class DateText:
    def __init__(self, date: datetime):
        self.date = date

    @property
    def time(self):
        return f"{self.date:%H:%M:%S}"

    @property
    def day(self):
        return f"{self.date:%d}"

    @property
    def month(self):
        return f"{self.date:%B}"

    @property
    def year(self):
        return f"{self.date:%Y}"


def get_region_info(id_for_query):
    global region
    if id_for_query not in REGION:
        returned_region_info = Base().request("machine_regions", {"": ""}, "")
        region = {
            responses["id"]: responses["name"] for responses in returned_region_info
        }
    return region[id_for_query]


class Base:
    """Base class for init"""

    @staticmethod
    def request(
        query_type: str,
        query_filter: dict[str, str|int],
        not_empty_query: str = "=",
    ):
        defined_url = f"{URL}{query_type}?" + "&".join(
            [f"{key}{not_empty_query}{value}" for key, value in query_filter.items()]
        )

        return requests.get(defined_url, headers=HEADERS).json()["data"]


class Task(Base):
    """class for get requests of task info"""

    def __init__(
        self,
        id_for_query: Optional[str] = None,
        task_data: Optional[Dict[Any, Any]] = None,
    ):
        """get info by request"""
        if not id_for_query and not task_data:
            raise AttributeError("There should be only one argument")
        elif id_for_query and task_data:
            warnings.warn("There should be one argument at most")

        returned_info = (
            task_data or self.request("machine_tasks", {"id": id_for_query})[0]
        )

        self.task_id = returned_info.get("id")
        self.machine_id = returned_info.get("machine_id")
        self.driver_id = returned_info.get("driver_id")
        self.work_type_id = returned_info.get("work_type_id")
        self.implement_id = returned_info.get("implement_id")
        self.fuel_consumption = returned_info.get("fuel_consumption")
        self.covered_area = returned_info.get("covered_area")

        start_time = datetime.fromisoformat(returned_info.get("start_time"))
        end_time = datetime.fromisoformat(returned_info.get("end_time"))

        day = time(6, 00)
        night = time(22, 00)
        self.day_shift, self.night_shift = 0, 0

        while (start_time + timedelta(hours=1)) <= end_time:
            if night >= (start_time + timedelta(hours=1)).time() > day:
                self.day_shift += 1
            else:
                self.night_shift += 1
            start_time += timedelta(hours=1)

        self.start = DateText(datetime.fromisoformat(returned_info.get("start_time")))
        self.end = DateText(datetime.fromisoformat(returned_info.get("end_time")))

        self.machine = Machine(self.machine_id)
        self.driver = Driver(self.driver_id)
        self.work_type = WorkType(self.work_type_id)
        self.implement = Implement(self.implement_id)
        work_distance = returned_info.get("work_distance")
        road_distance = returned_info.get("total_distance") - work_distance

        if self.work_type.is_transfer:
            distance_hourly = {int(info[0][10:13]): info[1] for info in returned_info.get('total_distance_hourly')}
            self.day_distance_hour = 0
            self.night_distance_hour = 0
            day_distance_work = 0
            night_distance_work = 0
            for hour, work in distance_hourly.items():
                if 6 <= hour < 22:
                    self.day_distance_hour += 1
                    day_distance_work += work
                else:
                    self.night_distance_hour += 1
                    night_distance_work += work
            self.day_distance_work = round(day_distance_work / 1000)
            self.night_distance_work = round(night_distance_work / 1000)
        else:
            self.day_distance_hour = 0
            self.night_distance_hour = 0
            self.day_distance_work = 0
            self.night_distance_work = 0

        self.work_distance = round(work_distance/1000)
        self.road_distance = round(road_distance / 1000 if road_distance >= 10000 or self.work_type.is_transfer else 0)

    @classmethod
    def get_by_day(cls, start_time: datetime):
        end_time = start_time + timedelta(days=1)
        returned_info = cls.request(
            "machine_tasks",
            {"start_time_gt_eq": str(start_time), "start_time_lt_eq": str(end_time)},
        )
        return tuple(Task(task_data=task_data) for task_data in returned_info)


class PlanTask(Task):
    """ Класс заданий для составления плана с информацией о полях """
    def __init__(
        self,
        id_for_query: Optional[str] = None,
        task_data: Optional[Dict[Any, Any]] = None,
    ):
        """get info by request"""
        super().__init__(id_for_query, task_data)
        self.task_field_mapping_list = TaskFieldMapping.get_from_task_id(self.task_id, self.work_type.is_transfer)


    @classmethod
    def get_by_day(cls, start_time: datetime):
        end_time = start_time + timedelta(days=1)
        returned_info = cls.request(
            "machine_tasks",
            {"start_time_gt_eq": str(start_time), "start_time_lt_eq": str(end_time)},
        )
        return tuple(PlanTask(task_data=task_data) for task_data in returned_info)


class Machine(Base):
    """class for get requests of machine info"""

    def __init__(self, id_for_query: str):
        """get info by request"""
        returned_info = self.request("machines", {"id": id_for_query})[0]
        self.name = returned_info.get("name")
        self.number = returned_info.get("registration_number")
        returned_machines_info = self.request(
            "machine_region_mapping_items", {"machine_id": id_for_query}
        )[0]
        self.region = get_region_info(returned_machines_info["machine_region_id"])


class Driver(Base):
    """class for get requests of driver info"""

    def __init__(self, id_for_query: str):
        """get info by request"""
        returned_info = self.request("users", {"id": id_for_query})
        info = (
            returned_info[0]
            if returned_info
            else {"username": "", "additional_info": ""}
        )  # может не быть водителя
        self.driver_name = info.get("username")
        self.additional_info = info.get("additional_info")


class WorkType(Base):
    """class for get requests of work_type info"""

    def __init__(self, id_for_query: str):
        """get info by request"""
        returned_info = self.request("work_types", {"id": id_for_query})[0]
        self.work_type_name = returned_info.get("name")
        self.is_transfer = returned_info.get("work_type_group_id") == TRANSFER_WORK_TYPE


class Implement(Base):
    """class for get requests of implement info"""

    def __init__(self, id_for_query: str):
        """get info by request"""

        # there is a case when task has not an implement id
        returned_info = (
            {}
            if not id_for_query
            else self.request("implements", {"id": id_for_query})[0]
        )
        self.implement_name = returned_info.get("name") or ""
        self.registration_number = returned_info.get("registration_number") or ""


class TaskFieldMapping(Base):
    """class for get requests of implement info"""

    def __init__(self, field_id_work: dict[str, str | int | float]):
        """get info by request"""
        field_id = field_id_work['field_id']
        field = Field(field_id)

        self.name = field.name
        self.crop_name = field.crop_name
        self.area = field.area
        self.work_area = round(field_id_work.get('covered_area', 0))

        distance_hourly = {int(info[0][10:13]): info[1] for info in field_id_work.get('work_distance_hourly')}
        self.day_distance_hour = 0
        self.night_distance_hour = 0
        day_distance_work = 0
        night_distance_work = 0
        for hour, work in distance_hourly.items():
            if 6 <= hour < 22:
                self.day_distance_hour += 1
                day_distance_work += work
            else:
                self.night_distance_hour += 1
                night_distance_work += work
        # self.day_distance_work = round(day_distance_work / 1000)
        # self.night_distance_work = round(night_distance_work / 1000)
        self.day_distance_work = ''
        self.night_distance_work = ''

        covered_area_hourly = {int(info[0][10:13]): info[1] for info in field_id_work.get('covered_area_hourly')}
        self.day_covered_hour = 0
        self.night_covered_hour = 0
        day_covered_work = 0
        night_covered_work = 0
        for hour, work in covered_area_hourly.items():
            if 6 <= hour < 22:
                self.day_covered_hour += 1
                day_covered_work += work
            else:
                self.night_covered_hour += 1
                night_covered_work += work
        self.day_covered_work = round(day_covered_work)
        self.night_covered_work = round(night_covered_work)


    @classmethod
    def get_from_task_id(cls, task_id: str, is_transfer: bool = False) -> tuple['TaskFieldMapping']:
        """ Получить список планов по ид таски """
        task_field_mapping = cls.request("machine_task_field_mapping_items", {"machine_task_id": task_id})
        return tuple(
            TaskFieldMapping(info) for info in task_field_mapping if info.get('covered_area') >= 1 or is_transfer
        )


class Field(Base):
    """class for get requests of implement info"""

    def __init__(self, id: str):
        """get info by request"""
        field_info = self.request("fields", {"id": id})[0]
        self.id = id
        self.name = field_info['name']
        self.area = field_info['legal_area']

        crop_id = HistoryItems.get_crop_id(id , year)
        self.crop_name = Crop.get_name(crop_id)


class HistoryItems(Base):
    """class for get requests of implement info"""

    def __init__(self, field_id: str, year: str):
        """get info by request"""
        self.crop_id = self.request("history_items", {"field_id": field_id, "year": year})[0]['crop_id']

    @classmethod
    @cache
    def get_crop_id(cls, field_id: str, year: str) -> str:
        return HistoryItems(field_id, year).crop_id


class Crop(Base):
    """class for get requests of implement info"""

    def __init__(self, id: str):
        """get info by request"""
        self.name = self.request("crops", {"id": id})[0]['name']

    @classmethod
    @cache
    def get_name(cls, id: str) -> str:
        return Crop(id).name
