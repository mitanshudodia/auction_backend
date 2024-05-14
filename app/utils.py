import pytz
from datetime import datetime

async def convert_to_utc(timezone: str, date_time: datetime):
    timezone = pytz.timezone(timezone)
    date_time = timezone.localize(date_time)
    utc_time = date_time.astimezone(pytz.utc)
    return utc_time

async def convert_from_utc_to_local(local_timezone: str, utc_time: datetime):
    timezone = pytz.utc
    utc_time = timezone.localize(utc_time)
    print(utc_time)
    print("++++++++++++++++++++++++++=")
    local_time = utc_time.astimezone(pytz.timezone(local_timezone))
    return local_time