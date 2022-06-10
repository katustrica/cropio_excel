import asyncio
from datetime import datetime

import aiohttp

import info
from datas import Base, Task
from interface_helpers import get_period
from main import (create_production_excels, get_production_excel_infos,
                  get_waybill_excel_infos)

period = get_period({"-DATE_START-": "2022/05/24", "-DATE_END-": "2022/05/25"})
create_production_excels(period=period)
print(Base.count)
