import os
from flask import Flask
from flask_cors import CORS
from app.exceptions.exception_globals import handlerExceptionsGlobals
import gunicorn
from app.controllers.graph_controllers import graphRoutes

app: Flask = Flask(__name__)
app.register_blueprint(graphRoutes)
CORS(app, resources={r"/*": {"origins": "*"}})
handlerExceptionsGlobals(app=app)


if __name__ == '__main__':
   port = os.environ.get("PORT", "10000")
   os.system(f"gunicorn -b 0.0.0.0:{port} main:app")
