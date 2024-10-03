import json
from flask import render_template
from app import app

@app.route('/')
def index():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    # 将 'items' 重命名为 'nav_items' 以避免与 Python 的内置方法冲突
    categories = [{
        'name': category['name'],
        'nav_items': category['items']
    } for category in config['categories']]
    return render_template('index.html', categories=categories)