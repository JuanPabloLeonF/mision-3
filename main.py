import os
from flask import Flask
from flask_cors import CORS
from app.exceptions.exception_globals import handlerExceptionsGlobals

app: Flask = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
handlerExceptionsGlobals(app=app)

if __name__ == '__main__':
   from app.controllers.graph_controllers import graphRoutes
   app.register_blueprint(graphRoutes)
   app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
