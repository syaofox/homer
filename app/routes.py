import json
from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
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

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            # 处理添加项目
            category = request.form.get('category')
            title = request.form.get('title')
            url = request.form.get('url')
            icon = request.files.get('icon')
            
            if icon:
                filename = secure_filename(icon.filename)
                icon.save(os.path.join(app.static_folder, 'img', filename))
                icon_path = f'img/{filename}'
            else:
                icon_path = 'fas fa-link'  # 默认图标
            
            # 更新 config.json
            with open('config.json', 'r+', encoding='utf-8') as f:
                config = json.load(f)
                for cat in config['categories']:
                    if cat['name'] == category:
                        cat['items'].append({
                            'title': title,
                            'icon': icon_path,
                            'url': url
                        })
                        break
                f.seek(0)
                json.dump(config, f, ensure_ascii=False, indent=2)
                f.truncate()
            
            flash('项目已添加', 'success')
        
        elif action == 'edit':
            # 处理编辑项目
            # ... 类似的逻辑来更新现有项目 ...
            pass
        
        elif action == 'delete':
            # 处理删除项目
            category_name = request.form.get('category')
            title = request.form.get('title')
            
            with open('config.json', 'r+', encoding='utf-8') as f:
                config = json.load(f)
                for category in config['categories']:
                    if category['name'] == category_name:
                        category['items'] = [item for item in category['items'] if item['title'] != title]
                        break
                
                f.seek(0)
                json.dump(config, f, ensure_ascii=False, indent=2)
                f.truncate()
            
            flash('项目已删除', 'success')
        
        return redirect(url_for('config'))
    
    # GET 请求：显示配置页面
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    # 将 'items' 重命名为 'nav_items' 以避免与 Python 的内置方法冲突
    categories = [{
        'name': category['name'],
        'nav_items': category['items']
    } for category in config['categories']]
    return render_template('config.html', categories=categories)