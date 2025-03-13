from flask import Request, json
from app.apis.api_external import ApiExternalUtil
from app.mappers.mappers_graph import MapperGraph

class GraphServices:

    @staticmethod
    def generatedGraph(request: Request) -> dict:
        params, weatherType = MapperGraph.mapperRequestToDict(request=request)
        dfGrouped = ApiExternalUtil.createDataframeWithHourly(params=params)
        return ApiExternalUtil.createPlotlyGraph(dfGrouped=dfGrouped, weatherType=weatherType)

    @staticmethod
    def getCurrentWeather(request: Request) -> dict:
        params, timeZone = MapperGraph.mapperRequestToDictCurrentWeather(request=request)
        return ApiExternalUtil.getCurrentWeather(params=params, timeZone=timeZone)