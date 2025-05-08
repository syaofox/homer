from flask import Flask, send_from_directory
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # 用于 flash 消息
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为 16MB

# 添加从config/img提供静态文件的路由
@app.route('/config/img/<path:filename>')
def serve_config_images(filename):
    return send_from_directory(os.path.abspath('config/img'), filename)

from app import routes