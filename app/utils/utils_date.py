import pytz
from datetime import datetime

class UtilDate:

    @staticmethod
    def getHourCurrentLocal(timeZone: str) -> list:
        timezone: pytz.BaseTzInfo = pytz.timezone(timeZone)
        nowUtc: datetime = datetime.now(pytz.UTC)
        nowLocal: datetime = nowUtc.astimezone(timezone)
        return [nowLocal, timezone]