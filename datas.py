"""for requests"""

import locale
import warnings
from datetime import datetime, time, timedelta
from typing import Any, Dict, Optional, Union

import aiohttp
from async_timeout import asyncio
import requests
from aiocache import cached

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


async def get_region_info(id_for_query, session: aiohttp.ClientSession):
    global REGION
    if id_for_query not in REGION:
        returned_region_info = await Base.arequest(
            "machine_regions", {"": ""}, session, ""
        )
        REGION = {
            responses["id"]: responses["name"] for responses in returned_region_info
        }
    return REGION[id_for_query]


# count = 0
class Base:
    """Base class for init"""

    none_base = "none"
    count = 0
    lock = asyncio.Lock()
    @staticmethod
    def request(
        query_type: str,
        query_filter: dict[str, Union[str, int]],
        not_empty_query: str = "=",
    ):
        defined_url = f"{URL}{query_type}?" + "&".join(
            [f"{key}{not_empty_query}{value}" for key, value in query_filter.items()]
        )

        return requests.get(defined_url, headers=HEADERS).json()["data"]

    @classmethod
    async def arequest(
        cls,
        query_type: str,
        query_filter: dict[str, Union[str, int]],
        session: aiohttp.ClientSession,
        not_empty_query: str = "=",
    ):

        async with session.get(
            URL + query_type, params=query_filter, headers=HEADERS
        ) as response:

            res = (await response.json())["data"]
            async with cls.lock:
                cls.count += 1
            return res


class Task(Base):
    """class for get requests of task info"""

    @classmethod
    async def construct(
        cls,
        session: aiohttp.ClientSession,
        id_for_query: Optional[str] = None,
        task_data: Optional[Dict[Any, Any]] = None,
    ):
        """get info by request"""
        self = cls()
        if not id_for_query and not task_data:
            raise AttributeError("There should be only one argument")
        elif id_for_query and task_data:
            warnings.warn("There should be one argument at most")

        returned_info = (
            task_data
            or (
                await cls.arequest(
                    "machine_tasks", {"id": str(id_for_query)}, session=session
                )
            )[0]
        )
        # print(returned_info)
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

        self.machine = await Machine.construct(self.machine_id, session=session)
        self.work_type = await WorkType.construct(self.work_type_id, session=session)
        try:
            self.driver = await Driver.construct(self.driver_id, session=session)
        except:
            self.driver = Driver()
        try:
            self.implement = await Implement.construct(
                self.implement_id, session=session
            )
        except:
            self.implement = Implement()
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

        return self

    @classmethod
    async def get_by_day(cls, start_time: datetime, session: aiohttp.ClientSession):
        end_time = start_time + timedelta(days=1)
        returned_info = await cls.arequest(
            "machine_tasks",
            {"start_time_gt_eq": str(start_time), "start_time_lt_eq": str(end_time)},
            session=session,
        )
        return [
            await cls.construct(task_data=task_data, session=session)
            for task_data in returned_info
        ]


class PlanTask(Task):
    """Класс заданий для составления плана с информацией о полях"""

    @classmethod
    async def construct(
        cls,
        session: aiohttp.ClientSession,
        id_for_query: Optional[str] = None,
        task_data: Optional[Dict[Any, Any]] = None,
    ):
        """get info by request"""
        self = cls()
        task_instance = await super().construct(
            session=session, id_for_query=id_for_query, task_data=task_data
        )
        self.__dict__ = {
            key: value for key, value in task_instance.__dict__.items()
        }  # TODO , надо исправить, выглядит не очень
        self.task_field_mapping_list = await TaskFieldMapping.get_from_task_id(
            self.task_id, session
        )
        return self

    @classmethod
    async def get_by_day(cls, start_time: datetime, session: aiohttp.ClientSession):
        end_time = start_time + timedelta(days=1)
        returned_info = await cls.arequest(
            "machine_tasks",
            {"start_time_gt_eq": str(start_time), "start_time_lt_eq": str(end_time)},
            session,
        )
        return [
            (await PlanTask.construct(session, task_data=task_data))
            for task_data in returned_info
        ]


class Machine(Base):
    """class for get requests of machine info"""

    def __init__(self):
        self.name = self.none_base
        self.number = self.none_base
        self.region = self.none_base

    @classmethod
    async def construct(cls, id_for_query: str, session: aiohttp.ClientSession):
        """get info by request"""
        self = cls()
        returned_info = (
            await self.arequest("machines", {"id": id_for_query}, session=session)
        )[0]
        self.name = returned_info.get("name")
        self.number = returned_info.get("registration_number")
        returned_machines_info = (
            await self.arequest(
                "machine_region_mapping_items",
                {"machine_id": id_for_query},
                session=session,
            )
        )[0]
        self.region = await get_region_info(
            returned_machines_info["machine_region_id"], session=session
        )
        return self


class Driver(Base):
    def __init__(self):
        self.driver_name = None
        self.additional_info = self.none_base

    """class for get requests of driver info"""

    @classmethod
    async def construct(cls, id_for_query: str, session: aiohttp.ClientSession):
        """get info by request"""
        self = cls()
        returned_info = await self.arequest(
            "users", {"id": id_for_query}, session=session
        )
        info = (
            returned_info[0]
            if returned_info
            else {"username": "", "additional_info": ""}
        )  # может не быть водителя
        self.driver_name = info.get("username")
        self.additional_info = info.get("additional_info")
        return self


class WorkType(Base):
    """class for get requests of work_type info"""

    def __init__(self):
        self.work_type_name = self.none_base
        self.is_transfer = self.none_base

    @classmethod
    async def construct(cls, id_for_query: str, session: aiohttp.ClientSession):
        """get info by request"""
        self = cls()
        returned_info = (
            await self.arequest("work_types", {"id": id_for_query}, session=session)
        )[0]
        self.work_type_name = returned_info.get("name")
        self.is_transfer = returned_info.get("work_type_group_id") == TRANSFER_WORK_TYPE
        return self


class Implement(Base):
    """class for get requests of implement info"""

    def __init__(self):
        self.implement_name = self.none_base
        self.registration_number = self.none_base

    @classmethod
    async def construct(cls, id_for_query: str, session: aiohttp.ClientSession):
        """get info by request"""

        # there is a case when task has not an implement id
        self = cls()
        returned_info = (
            {}
            if not id_for_query
            else (
                await self.arequest("implements", {"id": id_for_query}, session=session)
            )[0]
        )
        self.implement_name = returned_info.get("name") or ""
        self.registration_number = returned_info.get("registration_number") or ""
        return self


class TaskFieldMapping(Base):
    """class for get requests of implement info"""

    @classmethod
    async def construct(
        cls,
        field_id_work: dict[str, Union[str, int, float]],
        session: aiohttp.ClientSession,
    ):
        """get info by request"""
        self = cls()
        field_id = field_id_work["field_id"]
        field = await Field.construct(field_id, session)

        self.name = field.name
        self.crop_name = field.crop_name
        self.area = field.area
        self.work_area = round(field_id_work.get("covered_area", 0))

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
        return self


    @classmethod
    async def get_from_task_id(
        cls, task_id: str, session: aiohttp.ClientSession, is_transfer: bool = False
    ) -> tuple["TaskFieldMapping"]:
        """Получить список планов по ид таски"""
        task_field_mapping = await cls.arequest(
            "machine_task_field_mapping_items", {"machine_task_id": task_id}, session
        )
        return [
            (await TaskFieldMapping.construct(info, session))
            for info in task_field_mapping
            if info.get("covered_area") > 0 or is_transfer
        ]


class Field(Base):
    """class for get requests of implement info"""

    @classmethod
    async def construct(
        cls,
        id: str,
        session: aiohttp.ClientSession,
    ):
        """get info by request"""
        self = cls()
        field_info = (await self.arequest("fields", {"id": id}, session))[0]
        self.id = id
        self.name = field_info["name"]
        self.area = field_info["legal_area"]

        crop_id = await HistoryItems.get_crop_id(id, year, session)
        self.crop_name = await Crop.get_name(crop_id, session) if crop_id else ''
        return self


class HistoryItems(Base):
    """class for get requests of implement info"""

    @classmethod
    async def construct(cls, field_id: str, year: str, session: aiohttp.ClientSession):
        """get info by request"""
        self = cls()
        self.crop_id = (
            await self.arequest(
                "history_items", {"field_id": field_id, "year": year}, session
            )
        )[0]["crop_id"]
        return self

    @classmethod
    @cached()
    async def get_crop_id(
        cls, field_id: str, year: str, session: aiohttp.ClientSession
    ) -> str:
        return (await HistoryItems.construct(field_id, year, session)).crop_id


class Crop(Base):
    """class for get requests of implement info"""

    @classmethod
    async def construct(self, id: str, session: aiohttp.ClientSession):
        """get info by request"""
        self.name = (await self.arequest("crops", {"id": id}, session))[0]["name"]
        return self

    @classmethod
    @cached()
    async def get_name(cls, id: str, session: aiohttp.ClientSession) -> str:
        return (await Crop.construct(id, session)).name
