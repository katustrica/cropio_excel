"""for requests"""

from datetime import datetime

import requests

from info import HEADERS, URL

REGION = {}


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
        self.work_type = WorkType(self.work_type_id)
        self.implement = Implement(self.implement_id)


class Machine(Base):
    """class for get requests of machine info"""

    def __init__(self, id_for_query: str):
        """get info by request"""
        returned_info = self.request("machines", "id", id_for_query)[0]
        self.name = returned_info["name"]
        returned_machines_info = self.request(
            "machine_region_mapping_items", "machine_id", id_for_query
        )[0]
        self.region = get_region_info(returned_machines_info["machine_region_id"])


class Driver(Base):
    """class for get requests of driver info"""

    def __init__(self, id_for_query: str):
        """get info by request"""
        returned_info = self.request("users", "id", id_for_query)[0]
        self.driver_name = returned_info["username"]


class WorkType(Base):
    """class for get requests of work_type info"""

    def __init__(self, id_for_query: str):
        """get info by request"""
        returned_info = self.request("work_types", "id", id_for_query)[0]
        self.work_type_name = returned_info["name"]


class Implement(Base):
    """class for get requests of implement info"""

    def __init__(self, id_for_query: str):
        """get info by request"""
        returned_info = self.request("implements", "id", id_for_query)[0]
        self.implement_name = returned_info["name"]
