"""for requests"""

import locale
from datetime import datetime

import requests

from info import HEADERS, URL

locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))
REGION = {}


class DateText():
    def __init__(self, date: datetime):
        self.date = date

    @property
    def time(self):
        return f'{self.date:%H:%M:%S}'
    @property
    def day(self):
        return f'{self.date:%d}'
    @property
    def month(self):
        return f'{self.date:%B}'
    @property
    def year(self):
        return f'{self.date:%Y}'


def get_region_info(id_for_query):
    global region
    if id_for_query not in REGION:
        returned_region_info = Base().request("machine_regions", "", "", "")
        region = {
            responses["id"]: responses["name"] for responses in returned_region_info
        }
    return region[id_for_query]


class Base:
    """Base class for init"""

    def request(
        self,
        query_type: str,
        query_value: str,
        query_key: str,
        not_empty_query: str = "=",
    ):
        defined_url = f"{URL}//{query_type}//?{query_value}{not_empty_query}{query_key}"
        return requests.get(defined_url, headers=HEADERS).json()["data"]


class Task(Base):
    """class for get requests of task info"""

    def __init__(self, id_for_query: str):
        """get info by request"""
        returned_info = self.request("machine_tasks", "id", id_for_query)[0]

        self.machine_id = returned_info.get("machine_id")
        self.driver_id = returned_info.get("driver_id")
        self.work_type_id = returned_info.get("work_type_id")
        self.implement_id = returned_info.get("implement_id")

        self.start = DateText(datetime.fromisoformat(returned_info.get("start_time")))
        self.end = DateText(datetime.fromisoformat(returned_info.get("end_time")))

        self.machine = Machine(self.machine_id)
        self.driver = Driver(self.driver_id)
        self.work_type = WorkType(self.work_type_id)
        self.implement = Implement(self.implement_id)


class Machine(Base):
    """class for get requests of machine info"""

    def __init__(self, id_for_query: str):
        """get info by request"""
        returned_info = self.request("machines", "id", id_for_query)[0]
        self.name = returned_info.get("name")
        self.number = returned_info.get("registration_number")
        returned_machines_info = self.request(
            "machine_region_mapping_items", "machine_id", id_for_query
        )[0]
        self.region = get_region_info(returned_machines_info["machine_region_id"])


class Driver(Base):
    """class for get requests of driver info"""

    def __init__(self, id_for_query: str):
        """get info by request"""
        returned_info = self.request("users", "id", id_for_query)
        info = returned_info[0] if returned_info else {"username": '', "additional_info": ''}  # может не быть водителя
        self.driver_name = info.get("username")
        self.additional_info = info.get("additional_info")


class WorkType(Base):
    """class for get requests of work_type info"""

    def __init__(self, id_for_query: str):
        """get info by request"""
        returned_info = self.request("work_types", "id", id_for_query)[0]
        self.work_type_name = returned_info.get("name")


class Implement(Base):
    """class for get requests of implement info"""

    def __init__(self, id_for_query: str):
        """get info by request"""
        returned_info = self.request("implements", "id", id_for_query)[0]
        self.implement_name = returned_info.get("name")
        self.registration_number = returned_info.get("registration_number")
