from datetime import datetime

from datas import Task, Base
import info
from main import get_waybill_excel_infos
from interface_helpers import get_period
import asyncio
import aiohttp

# period = get_period({"-DATE_START-" : "2022/05/24", "-DATE_END-" : "2022/05/25"})
# asyncio.run(get_waybill_excel_infos(period=period))
async def cor():
    async with aiohttp.ClientSession() as session:
        task = await Task.construct(8001, session=session)
        print(task.fuel_consumption)

asyncio.run(cor())