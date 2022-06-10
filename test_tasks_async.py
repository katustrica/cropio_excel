from datetime import datetime

from datas import Task, Base
import info
from main import get_waybill_excel_infos
from interface_helpers import get_period
import asyncio
import aiohttp

# period = get_period({"-DATE_START-" : "2022/05/24", "-DATE_END-" : "2022/05/31"})
res = asyncio.run(get_waybill_excel_infos(task_ids=[11075, 11076, 11077, 11078]))
print(len(res))
