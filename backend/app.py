from flask import Flask, send_from_directory
from pathlib import Path

from backend.routes.birthdays import bp as birthdays_bp
from backend.routes.weather    import bp as weather_bp
from backend.routes.kanji      import bp as kanji_bp
from backend.routes.news       import bp as news_bp
from backend.routes.fx         import bp as fx_bp

BASE_DIR = Path(__file__).resolve().parents[1]
FRONT_DIR = BASE_DIR / "frontend" / "public"

def create_app():
    app = Flask(__name__)
    app.register_blueprint(birthdays_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(kanji_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(fx_bp)

    @app.get("/")
    def index():
        return send_from_directory(FRONT_DIR, "index.html")

    @app.get("/<path:path>")
    def static_files(path):
        return send_from_directory(FRONT_DIR, path)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=8000, debug=True)
