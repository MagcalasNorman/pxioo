from flask import Flask
from routes.main_routes import main_bp
from config import Config
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__, static_folder="views", static_url_path="")
    app.register_blueprint(main_bp)
    app.config.from_object(Config)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(
        debug=app.config.get('PIXOO_REST_DEBUG', True),
        host=app.config.get('PIXOO_REST_HOST', '127.0.0.1'),
        port=app.config.get('PIXOO_REST_PORT', 8000)
    )