"""for requests"""

from dataclasses import dataclass
from datetime import datetime

import requests
from info import HEADERS, URL


@dataclass
class ExcelInfo:
    """dataclass for storing info about task"""

    task: str
    time: str
    machine: str
    region: str
    driver: str
    work: str
    implement: str


class Base:
    """Base class for init"""

    def __init__(self, id_for_query):
        """init"""
        self.get_task_info(id_for_query)

    def get_task_info(self, id_for_query):
        """base"""


class Task(Base):
    """class for get requests of task info"""

    def get_task_info(self, id_for_query):
        """get info by request"""
        defined_url = URL + "machine_tasks/?id=" + str(id_for_query)
        returned_info = requests.get(defined_url, headers=HEADERS).json()["data"][0]

        self.start_time = returned_info["start_time"]
        self.end_time = returned_info["end_time"]
        self.machine_id = returned_info["machine_id"]
        self.driver_id = returned_info["driver_id"]
        self.work_type_id = returned_info["work_type_id"]
        self.implement_id = returned_info["implement_id"]
        time_start = datetime.fromisoformat(self.start_time).replace(second=0, microsecond=0, tzinfo=None)
        time_end = datetime.fromisoformat(self.end_time).replace(second=0, microsecond=0, tzinfo=None)
        self.time = f"{time_start} - {time_end}"

        self.machine = Machine(self.machine_id)
        self.driver = Driver(self.driver_id)
        self.work_type = WorkType(self.work_type_id)
        self.implement = Implement(self.implement_id)


class Machine(Base):
    """class for get requests of machine info"""

    def get_task_info(self, id_for_query):
        """get info by request"""
        defined_url = URL + "machines/?id=" + str(id_for_query)
        returned_info = requests.get(defined_url, headers=HEADERS).json()["data"][0]
        self.name = returned_info["name"]

        defined_url = URL + "machine_region_mapping_items/?machine_id=" + str(id_for_query)
        returned_info = requests.get(defined_url, headers=HEADERS).json()["data"][0]
        defined_url = URL + "machine_regions/?id=" + str(returned_info["machine_region_id"])
        returned_info = requests.get(defined_url, headers=HEADERS).json()["data"][1]
        self.region = returned_info["name"]


class Driver(Base):
    """class for get requests of driver info"""

    def get_task_info(self, id_for_query):
        """get info by request"""
        defined_url = URL + "users/?id=" + str(id_for_query)
        returned_info = requests.get(defined_url, headers=HEADERS).json()["data"][0]
        self.driver_name = returned_info["username"]


class WorkType(Base):
    """class for get requests of work_type info"""

    def get_task_info(self, id_for_query):
        """get info by request"""
        defined_url = URL + "work_types/?id=" + str(id_for_query)
        returned_info = requests.get(defined_url, headers=HEADERS).json()["data"][0]
        self.work_type_name = returned_info["name"]


class Implement(Base):
    """class for get requests of implement info"""

    def get_task_info(self, id_for_query):
        """get info by request"""
        defined_url = URL + "implements/?id=" + str(id_for_query)
        returned_info = requests.get(defined_url, headers=HEADERS).json()["data"][0]
        self.implement_name = returned_info["name"]
