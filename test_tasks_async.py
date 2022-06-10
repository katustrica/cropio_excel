from datetime import datetime

from datas import Task, Base
import info
from main import get_production_excel_infos, get_waybill_excel_infos, create_production_excels
from interface_helpers import get_period
import asyncio
import aiohttp

period = get_period({"-DATE_START-" : "2022/05/24", "-DATE_END-" : "2022/05/25"})
create_production_excels(period=period)
print(Base.count)
