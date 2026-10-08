"""Flask application for the calculator challenge."""

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge

from calculator import CalculationError, calculate


MAX_REQUEST_BYTES = 8 * 1024


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_BYTES

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/api/calculate")
    def calculate_route():
        if not request.is_json:
            return jsonify(error="request must use application/json"), 415

        try:
            payload = request.get_json()
        except BadRequest:
            return jsonify(error="request body contains invalid JSON"), 400

        if not isinstance(payload, dict):
            return jsonify(error="request body must be a JSON object"), 400

        required_fields = {"left", "operator", "right"}
        if set(payload) != required_fields:
            return jsonify(error="request must contain exactly left, operator, and right"), 400

        try:
            result = calculate(payload["left"], payload["operator"], payload["right"])
        except CalculationError as exc:
            return jsonify(error=str(exc)), 400

        return jsonify(result=result)

    @app.errorhandler(RequestEntityTooLarge)
    def request_too_large(_error):
        return jsonify(error="request body is too large"), 413

    return app


app = create_app()


if __name__ == "__main__":
    app.run()

