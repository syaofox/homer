import json
from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from app import app

@app.route('/')
def index():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
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
            category = request.form.get('category')
            title = request.form.get('title')
            url = request.form.get('url')
            icon = request.files.get('icon')
            
            if icon and icon.filename:
                filename = secure_filename(icon.filename)
                icon.save(os.path.join(app.static_folder, 'img', filename))
                icon_path = f'img/{filename}'
            else:
                icon_path = 'fas fa-link'  # 默认图标
            
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
            old_category = request.form.get('old_category')
            new_category = request.form.get('new_category')
            old_title = request.form.get('old_title')
            new_title = request.form.get('new_title')
            new_url = request.form.get('new_url')
            new_icon = request.files.get('new_icon')
            
            with open('config.json', 'r+', encoding='utf-8') as f:
                config = json.load(f)
                item_to_move = None
                for category in config['categories']:
                    if category['name'] == old_category:
                        for item in category['items']:
                            if item['title'] == old_title:
                                item['title'] = new_title
                                item['url'] = new_url
                                if new_icon and new_icon.filename:
                                    filename = secure_filename(new_icon.filename)
                                    new_icon.save(os.path.join(app.static_folder, 'img', filename))
                                    item['icon'] = f'img/{filename}'
                                if old_category != new_category:
                                    item_to_move = item
                                    category['items'].remove(item)
                                break
                        break
                
                if item_to_move:
                    for category in config['categories']:
                        if category['name'] == new_category:
                            category['items'].append(item_to_move)
                            break
                
                f.seek(0)
                json.dump(config, f, ensure_ascii=False, indent=2)
                f.truncate()
            
            flash('项目已更新', 'success')
        
        elif action == 'delete':
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
    
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    categories = [{
        'name': category['name'],
        'nav_items': category['items']
    } for category in config['categories']]
    return render_template('config.html', categories=categories)