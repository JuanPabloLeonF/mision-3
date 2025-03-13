from flask import Request, json

class MapperGraph:

    @staticmethod
    def mapperRequestToDict(request: Request) -> list:

        data = request.get_json()

        if data.get("params") is None or data.get("weatherType") is None:
            raise ValueError("Lo siento pero no enviaste los parametros")

        paramsData: dict = data.get("params")

        params: dict = {
            "latitude": paramsData.get("latitude"),
            "longitude": paramsData.get("longitude"),
            "hourly": ["temperature_2m", "precipitation_probability", "precipitation", "cloudcover"],
            "forecast_days": 7
        }

        weatherType: str = data.get("weatherType")

        return [params, weatherType]

    @staticmethod
    def mapperRequestToDictCurrentWeather(request: Request) -> list:

        data = request.get_json()

        if data.get("params") is None or data.get("timeZone") is None:
            raise ValueError("Lo siento pero no enviaste los parametros")

        paramsData: dict = data.get("params")

        params: dict = {
            "latitude": paramsData.get("latitude"),
            "longitude": paramsData.get("longitude"),
            "hourly": ["temperature_2m"],
            "daily": ["temperature_2m_max", "temperature_2m_min"],
            "timezone": "auto"
        }

        timeZone: str = data.get("timeZone")

        return [params, timeZone]