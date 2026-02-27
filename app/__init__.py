from flask import Flask, send_from_directory

from app.config import config as app_config
from app.blueprints import main_bp
from app.utils import icon_to_svg, is_fa_icon

app = Flask(__name__)
app.jinja_env.globals["icon_to_svg"] = icon_to_svg
app.jinja_env.globals["is_fa_icon"] = is_fa_icon

app.config["MAX_CONTENT_LENGTH"] = app_config.max_content_length
app.config["DEBUG"] = app_config.debug

app.register_blueprint(main_bp)


@app.route("/config/img/<path:filename>")
def serve_config_images(filename):
    return send_from_directory(app_config.images_path, filename)
