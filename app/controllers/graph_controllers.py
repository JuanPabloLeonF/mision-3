from flask import jsonify, Response, request, Blueprint
from app.services.graph_services import GraphServices

graphRoutes: Blueprint = Blueprint(name="graph", import_name=__name__, url_prefix="/graph")

class GraphController:

    @staticmethod
    @graphRoutes.route("/generatedGraph", methods=["POST"])
    def generatedGraph() -> tuple[Response, int]:
        graphGeneratedJSON: dict = GraphServices.generatedGraph(request=request)
        return jsonify(graphGeneratedJSON), 201

    @staticmethod
    @graphRoutes.route("/currentWeather", methods=["POST"])
    def currentWeather() -> tuple[Response, int]:
        currentWeatherJSON: dict = GraphServices.getCurrentWeather(request=request)
        return jsonify(currentWeatherJSON), 201