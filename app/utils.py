import pytz
from datetime import datetime

async def convert_to_utc(timezone: str, date_time: datetime):
    utc_time = date_time.astimezone(pytz.utc)
    return utc_time

async def convert_from_utc_to_local(local_timezone: str, utc_time: datetime):
    local_time = utc_time.astimezone(pytz.timezone(local_timezone))
    return local_time