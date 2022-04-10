from dataclasses import dataclass
from datetime import datetime
import requests
from info import HEADERS, URL


@dataclass
class ExcelInfo:
    task: str
    time: str
    machine: str
    region: str
    driver: str
    work: str
    implement: str


class Base:
    def __init__(self, id):
        self.get_task_info(id)

class Task(Base):
    def get_task_info(self, task_id):
        URL_ = URL + "machine_tasks/?id=" + str(task_id)
        returned_info = requests.get(URL_, headers=HEADERS).json()["data"][0]

        self.start_time = returned_info["start_time"]
        self.end_time = returned_info["end_time"]
        self.machine_id = returned_info["machine_id"]
        self.driver_id = returned_info["driver_id"]
        self.work_type_id = returned_info["work_type_id"]
        self.implement_id = returned_info["implement_id"]
        time_start = datetime.fromisoformat(self.start_time).replace(
            second=0, microsecond=0, tzinfo=None
        )
        time_end = datetime.fromisoformat(self.end_time).replace(
            second=0, microsecond=0, tzinfo=None
        )
        self.time = f"{time_start} - {time_end}"

        self.machine = Machine(self.machine_id)
        self.driver = Driver(self.driver_id)
        self.work_type = Work_Type(self.work_type_id)
        self.implement = Implement(self.implement_id)


class Machine(Base):
    def get_task_info(self, machine_id):
        URL_ = URL + "machines/?id=" + str(machine_id)
        returned_info = requests.get(URL_, headers=HEADERS).json()["data"][0]
        self.name = returned_info["name"]

        URL_ = URL + "machine_region_mapping_items/?machine_id=" + str(machine_id)
        returned_info = requests.get(URL_, headers=HEADERS).json()["data"][0]
        URL_ = URL + "machine_regions/?id=" + str(returned_info["machine_region_id"])
        returned_info = requests.get(URL_, headers=HEADERS).json()["data"][1]
        self.region = returned_info["name"]


class Driver(Base):
    def get_task_info(self, driver_id):
        URL_ = URL + "users/?id=" + str(driver_id)
        returned_info = requests.get(URL_, headers=HEADERS).json()["data"][0]
        self.driver_name = returned_info["username"]


class Work_Type(Base):
    def __init__(self, work_type_id):
        info = self.get_task_info(work_type_id)

    def get_task_info(self, work_type_id):
        URL_ = URL + "work_types/?id=" + str(work_type_id)
        returned_info = requests.get(URL_, headers=HEADERS).json()["data"][0]
        self.work_type_name = returned_info["name"]


class Implement(Base):
    def __init__(self, implement_id):
        self.info = self.get_task_info(implement_id)

    def get_task_info(self, implement_id):
        URL_ = URL + "implements/?id=" + str(implement_id)
        returned_info = requests.get(URL_, headers=HEADERS).json()["data"][0]
        self.implement_name = returned_info["name"]

