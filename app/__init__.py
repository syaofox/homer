from flask import Flask, send_from_directory
import os

app = Flask(__name__)
# 移除无用的SECRET_KEY，因为flash消息在前端AJAX场景下不起作用
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为 16MB

# 添加从config/img提供静态文件的路由
@app.route('/config/img/<path:filename>')
def serve_config_images(filename):
    return send_from_directory(os.path.abspath('config/img'), filename)

from app import routes