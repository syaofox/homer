from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # 用于 flash 消息
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为 16MB

from app import routes