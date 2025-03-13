from flask import Flask, Response, jsonify

def handlerExceptionsGlobals(app: Flask):

    @app.errorhandler(ValueError)
    def ValuerErrorHandler(error) -> tuple[Response, int]:
        return jsonify({
            "statusCode": 400,
            "status": "BAD REQUEST",
            "message": str(error)
        }), 400