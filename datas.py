from dataclasses import dataclass
from datetime import datetime
import requests
from info import headers, url


@dataclass
class ExcelInfo:
    task: str
    time: str
    machine: str
    region: str
    driver: str
    work: str
    implement: str


class Task:
    def __init__(self, task_id):
        self.info = {}
        self.get_task_info(task_id)

    def get_task_info(self, task_id):
        url_ = url + "machine_tasks/?id=" + str(task_id)
        returned_info = requests.get(url_, headers=headers).json()["data"][0]

        self.info["start_time"] = returned_info["start_time"]
        self.info["end_time"] = returned_info["end_time"]
        self.info["machine_id"] = returned_info["machine_id"]
        self.info["driver_id"] = returned_info["driver_id"]
        self.info["work_type_id"] = returned_info["work_type_id"]
        self.info["implement_id"] = returned_info["implement_id"]


class Machine:
    def __init__(self, machine_id):
        self.info = {}
        self.get_task_info(machine_id)

    def get_task_info(self, machine_id):
        url_ = url + "machines/?id=" + str(machine_id)
        returned_info = requests.get(url_, headers=headers).json()["data"][0]
        self.info["name"] = returned_info["name"]

        url_ = url + "machine_region_mapping_items/?machine_id=" + str(machine_id)
        returned_info = requests.get(url_, headers=headers).json()["data"][0]
        url_ = url + "machine_regions/?id=" + str(returned_info["machine_region_id"])
        returned_info = requests.get(url_, headers=headers).json()["data"][1]
        self.info["region"] = returned_info["name"]


class Driver:
    def __init__(self, driver_id):
        self.info = {}
        self.get_task_info(driver_id)

    def get_task_info(self, driver_id):
        url_ = url + "users/?id=" + str(driver_id)
        returned_info = requests.get(url_, headers=headers).json()["data"][0]
        self.info["driver"] = returned_info["username"]


class Work_Type:
    def __init__(self, work_type_id):
        self.info = {}
        self.get_task_info(work_type_id)

    def get_task_info(self, work_type_id):
        url_ = url + "work_types/?id=" + str(work_type_id)
        returned_info = requests.get(url_, headers=headers).json()["data"][0]
        self.info["work_type_name"] = returned_info["name"]


class Implement:
    def __init__(self, implement_id):
        self.info = {}
        self.get_task_info(implement_id)

    def get_task_info(self, implement_id):
        url_ = url + "implements/?id=" + str(implement_id)
        returned_info = requests.get(url_, headers=headers).json()["data"][0]
        self.info["implement_name"] = returned_info["name"]


if __name__ == "__main__":
    task_ids = list(map(int, input().split()))
    tasks = []

    for task_id in task_ids:
        task_instance = Task(task_id)
        machine = Machine(task_instance.info["machine_id"])
        driver = Driver(task_instance.info["driver_id"])
        work_type = Work_Type(task_instance.info["work_type_id"])
        impl = Implement(task_instance.info["implement_id"])

        task = ExcelInfo
        task.task = task_id
        time_start = datetime.fromisoformat(task_instance.info["start_time"]).replace(
            second=0, microsecond=0, tzinfo=None
        )
        time_end = datetime.fromisoformat(task_instance.info["end_time"]).replace(
            second=0, microsecond=0, tzinfo=None
        )
        task.time = f"{time_start} - {time_end}"
        task.machine = machine.info["name"]
        task.region = machine.info["region"]
        task.driver = driver.info["driver"]
        task.work = work_type.info["work_type_name"]
        task.implement = impl.info["implement_name"]
        tasks.append(task)

        print(
            task.time,
            task.machine,
            task.region,
            task.driver,
            task.work,
            task.implement,
            sep="\n",
        )
