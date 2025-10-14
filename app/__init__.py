from flask import Flask, send_from_directory
from pathlib import Path

from .config import config as app_config

app = Flask(__name__)

# 使用配置系统设置应用参数
app.config['MAX_CONTENT_LENGTH'] = app_config.max_content_length
app.config['DEBUG'] = app_config.debug

# 添加从config/img提供静态文件的路由
@app.route('/config/img/<path:filename>')
def serve_config_images(filename):
    """提供配置文件中的图片"""
    return send_from_directory(app_config.images_path, filename)

from app import routes