from flask import Flask
from flask_cors import CORS


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Register API blueprint
    from backend.api.routes import api_bp

    app.register_blueprint(api_bp, url_prefix="/")

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)


