console.log('个人导航页面已加载');

// 图标 SVG 映射（与 app/utils.py icon_to_svg 保持一致，用于动态创建内容）
var ICON_SVG_MAP = {
    eye: ['0 0 576 512', 'M572.52 241.4C518.29 135.59 410.93 64 288 64S57.68 135.64 3.48 241.41a32.35 32.35 0 0 0 0 29.19C57.71 376.41 165.07 448 288 448s230.32-71.64 284.52-177.41a32.35 32.35 0 0 0 0-29.19zM288 400a144 144 0 1 1 144-144 143.93 143.93 0 0 1-144 144zm0-240a95.31 95.31 0 0 0-25.31 3.79 47.85 47.85 0 0 1-66.9 66.9A95.78 95.78 0 1 0 288 160z'],
    'eye-slash': ['0 0 640 512', 'M320 400c-75.85 0-137.25-58.71-142.9-133.11L72.2 185.82c-13.79 17.3-26.48 35.59-36.72 55.59a32.35 32.35 0 0 0 0 29.19C89.71 376.41 197.07 448 320 448c26.91 0 52.87-4 77.89-10.46L346 397.39a144.13 144.13 0 0 1-26 2.61zm313.82 58.1l-110.55-85.44a331.25 331.25 0 0 0 81.25-102.07 32.35 32.35 0 0 0 0-29.19C550.29 135.59 442.93 64 320 64a308.15 308.15 0 0 0-147.32 37.7L45.46 3.37A16 16 0 0 0 23 6.18L3.37 31.45A16 16 0 0 0 6.18 53.9l588.36 454.73a16 16 0 0 0 22.46-2.81l19.64-25.27a16 16 0 0 0-2.82-22.45zm-183.72-142l-39.3-30.38A94.75 94.75 0 0 0 416 256a94.76 94.76 0 0 0-121.31-92.21A47.65 47.65 0 0 1 304 192a46.64 46.64 0 0 1-1.54 10l-73.61-56.89A142.31 142.31 0 0 1 320 112a143.92 143.92 0 0 1 144 144c0 21.63-5.29 41.79-13.9 60.11z'],
    plus: ['0 0 448 512', 'M416 208H272V64c0-17.67-14.33-32-32-32h-32c-17.67 0-32 14.33-32 32v144H32c-17.67 0-32 14.33-32 32v32c0 17.67 14.33 32 32 32h144v144c0 17.67 14.33 32 32 32h32c17.67 0 32-14.33 32-32V304h144c17.67 0 32-14.33 32-32v-32c0-17.67-14.33-32-32-32z'],
    link: ['0 0 512 512', 'M326.612 185.391c59.747 59.809 58.927 155.698.36 214.59-.11.12-.24.25-.36.37l-67.2 67.2c-59.27 59.27-155.699 59.262-214.96 0-59.27-59.26-59.27-155.7 0-214.96l37.106-37.106c9.84-9.84 26.786-3.3 27.294 10.606.648 17.722 3.826 35.527 9.69 52.721 1.986 5.822.567 12.262-3.783 16.612l-13.087 13.087c-28.026 28.026-28.905 73.66-1.155 101.96 28.024 28.579 74.086 28.749 102.325.51l67.2-67.19c28.191-28.191 28.073-73.757 0-101.83-3.701-3.694-7.429-6.564-10.341-8.569a16.037 16.037 0 0 1-6.947-12.606c-.396-10.567 3.348-21.456 11.698-29.806l21.054-21.055c5.521-5.521 14.182-6.199 20.584-1.731a152.482 152.482 0 0 1 20.522 17.197zM467.547 44.449c-59.261-59.262-155.69-59.27-214.96 0l-67.2 67.2c-.12.12-.25.25-.36.37-58.566 58.892-59.387 154.781.36 214.59a152.454 152.454 0 0 0 20.521 17.196c6.402 4.468 15.064 3.789 20.584-1.731l21.054-21.055c8.35-8.35 12.094-19.239 11.698-29.806a16.037 16.037 0 0 0-6.947-12.606c-2.912-2.005-6.64-4.875-10.341-8.569-28.073-28.073-28.191-73.639 0-101.83l67.2-67.19c28.239-28.239 74.3-28.069 102.325.51 27.75 28.3 26.872 73.934-1.155 101.96l-13.087 13.087c-4.35 4.35-5.769 10.79-3.783 16.612 5.864 17.194 9.042 34.999 9.69 52.721.509 13.906 17.454 20.446 27.294 10.606l37.106-37.106c59.271-59.259 59.271-155.699.001-214.959z'],
    robot: ['0 0 640 512', 'M32,224H64V416H32A31.96166,31.96166,0,0,1,0,384V256A31.96166,31.96166,0,0,1,32,224Zm512-48V448a64.06328,64.06328,0,0,1-64,64H160a64.06328,64.06328,0,0,1-64-64V176a79.974,79.974,0,0,1,80-80H288V32a32,32,0,0,1,64,0V96H464A79.974,79.974,0,0,1,544,176ZM264,256a40,40,0,1,0-40,40A39.997,39.997,0,0,0,264,256Zm-8,128H192v32h64Zm96,0H288v32h64ZM456,256a40,40,0,1,0-40,40A39.997,39.997,0,0,0,456,256Zm-8,128H384v32h64ZM640,256V384a31.96166,31.96166,0,0,1-32,32H576V224h32A31.96166,31.96166,0,0,1,640,256Z'],
    server: ['0 0 512 512', 'M480 160H32c-17.673 0-32-14.327-32-32V64c0-17.673 14.327-32 32-32h448c17.673 0 32 14.327 32 32v64c0 17.673-14.327 32-32 32zm-48-88c-13.255 0-24 10.745-24 24s10.745 24 24 24 24-10.745 24-24-10.745-24-24-24zm-64 0c-13.255 0-24 10.745-24 24s10.745 24 24 24 24-10.745 24-24-10.745-24-24-24zm112 248H32c-17.673 0-32-14.327-32-32v-64c0-17.673 14.327-32 32-32h448c17.673 0 32 14.327 32 32v64c0 17.673-14.327 32-32 32zm-48-88c-13.255 0-24 10.745-24 24s10.745 24 24 24 24-10.745 24-24-10.745-24-24-24zm-64 0c-13.255 0-24 10.745-24 24s10.745 24 24 24 24-10.745 24-24-10.745-24-24-24zm112 248H32c-17.673 0-32-14.327-32-32v-64c0-17.673 14.327-32 32-32h448c17.673 0 32 14.327 32 32v64c0 17.673-14.327 32-32 32zm-48-88c-13.255 0-24 10.745-24 24s10.745 24 24 24 24-10.745 24-24-10.745-24-24-24zm-64 0c-13.255 0-24 10.745-24 24s10.745 24 24 24 24-10.745 24-24-10.745-24-24-24z']
};
// 判断是否为 Font Awesome 图标类名（与 app/utils.py is_fa_icon 保持一致）
function isFaIcon(icon) {
    if (!icon || typeof icon !== 'string') return false;
    var s = icon.trim();
    return s.indexOf('fas ') === 0 || s.indexOf('fab ') === 0 || s.indexOf('far ') === 0 || s.indexOf('fal ') === 0 || s.indexOf('fa ') === 0;
}
function iconToSvgHtml(iconClass) {
    if (!iconClass || typeof iconClass !== 'string') iconClass = 'fa-link';
    var parts = iconClass.trim().split(/\s+/);
    var iconName = 'link';
    for (var i = 0; i < parts.length; i++) {
        if (parts[i].indexOf('fa-') === 0 && parts[i].length > 3) {
            iconName = parts[i].substring(3);
            break;
        }
    }
    var data = ICON_SVG_MAP[iconName] || ICON_SVG_MAP.link;
    return '<svg class="icon-svg" aria-hidden="true" viewBox="' + data[0] + '" xmlns="http://www.w3.org/2000/svg"><path d="' + data[1] + '"/></svg>';
}

// 访问统计相关功能
let visitStats = {};
let badgesVisible = true; // 角标显示状态

// 初始化访问统计数据 - 从服务器获取
function initVisitStats() {
    if (window.frequentItemsFromServer && window.frequentItemsFromServer.length > 0) {
        visitStats = {};
        window.frequentItemsFromServer.forEach(function(item) {
            visitStats[item.url] = item;
        });
        renderFrequentCategory();
        return;
    }
    fetch('/api/visit-stats', { method: 'GET' })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            visitStats = data;
            renderFrequentCategory();
        })
        .catch(function(err) {
            console.warn('无法读取访问统计数据:', err);
            visitStats = {};
        });
}

// 初始化角标显示状态
function initBadgesVisibility() {
    try {
        const stored = localStorage.getItem('badgesVisible');
        if (stored !== null) {
            badgesVisible = JSON.parse(stored);
        }
    } catch (e) {
        console.warn('无法读取角标显示状态:', e);
        badgesVisible = true;
    }
    updateBadgesVisibility();
    updateToggleButton();
}

// 切换角标显示状态
function toggleBadgesVisibility() {
    badgesVisible = !badgesVisible;
    updateBadgesVisibility();
    updateToggleButton();

    try {
        localStorage.setItem('badgesVisible', JSON.stringify(badgesVisible));
    } catch (e) {
        console.warn('无法保存角标显示状态:', e);
    }
}

// 更新角标显示状态
function updateBadgesVisibility() {
    var body = document.body;
    if (badgesVisible) {
        body.classList.remove('badges-hidden');
    } else {
        body.classList.add('badges-hidden');
    }
}

// 更新切换按钮状态（通过 .active 控制 eye/eye-slash 图标显示）
function updateToggleButton() {
    var btn = document.getElementById('toggle-badges');
    if (!btn) return;
    if (badgesVisible) {
        btn.classList.add('active');
    } else {
        btn.classList.remove('active');
    }
}

// 记录访问 - 发送到服务器
function recordVisit(title, icon, url) {
    if (!url) return;

    fetch('/api/visit-stats/record', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url, title: title, icon: icon })
    })
        .then(function(res) { return res.json(); })
        .then(function(response) {
            if (response.success && response.data) {
                visitStats[url] = response.data;
            }
        })
        .catch(function(err) {
            console.warn('无法保存访问统计数据:', err);
        });
}

// 获取访问频率最高的站点
function getTopVisitedSites(limit) {
    limit = limit || 20;
    const sites = Object.values(visitStats);
    return sites
        .sort(function(a, b) { return b.visit_count - a.visit_count; })
        .slice(0, limit);
}

// 渲染常用分类
function renderFrequentCategory() {
    const topSites = getTopVisitedSites();
    if (topSites.length === 0) return;

    var frequentCategory = document.getElementById('frequent-category');
    if (!frequentCategory) return;
    frequentCategory.innerHTML = '';

    var title = document.createElement('h2');
    title.textContent = '常用';
    frequentCategory.appendChild(title);

    var grid = document.createElement('div');
    grid.className = 'nav-grid';

    topSites.forEach(function(site) {
        var item = document.createElement('a');
        item.href = site.url;
        item.className = 'nav-item';
        item.setAttribute('data-category', '常用');
        item.setAttribute('data-title', site.title);
        item.setAttribute('data-icon', site.icon);

        if (isFaIcon(site.icon)) {
            var iconSpan = document.createElement('span');
            iconSpan.className = 'nav-item-icon';
            iconSpan.innerHTML = iconToSvgHtml(site.icon);
            item.appendChild(iconSpan);
        } else {
            var img = document.createElement('img');
            img.src = '/config/' + site.icon;
            img.alt = site.title;
            img.className = 'icon-img';
            item.appendChild(img);
        }

        if (site.visit_count > 0) {
            var badge = document.createElement('div');
            badge.className = 'click-badge';
            badge.textContent = site.visit_count;
            item.appendChild(badge);
        }

        var textSpan = document.createElement('span');
        textSpan.textContent = site.title;
        item.appendChild(textSpan);

        grid.appendChild(item);
    });

    frequentCategory.appendChild(grid);
    frequentCategory.style.display = '';
}

// 为所有导航链接添加点击统计
function attachVisitTracking() {
    document.addEventListener('click', function(e) {
        var target = e.target.closest('.nav-item:not(.add-item)');
        if (!target) return;

        var textSpan = target.querySelector('span:not(.nav-item-icon)');
        var title = target.dataset.title || (textSpan ? textSpan.textContent : '') || '';
        var url = target.getAttribute('href');

        var icon = 'fas fa-link';
        if (target.dataset.icon) {
            icon = target.dataset.icon;
        } else {
            var imgEl = target.querySelector('img.icon-img');
            if (imgEl) icon = (imgEl.getAttribute('src') || '').replace('/config/', '') || 'fas fa-link';
        }

        recordVisit(title, icon, url);
    });
}

// 动态加载 SortableJS（本地文件，延迟加载不阻塞首屏）
function loadSortable() {
    if (typeof Sortable !== 'undefined') return Promise.resolve(Sortable);
    return new Promise(function(resolve, reject) {
        var script = document.createElement('script');
        script.src = (function() {
            var mainScript = document.querySelector('script[data-sortable-src]');
            if (mainScript && mainScript.getAttribute('data-sortable-src')) {
                return mainScript.getAttribute('data-sortable-src');
            }
            var scripts = document.getElementsByTagName('script');
            for (var i = 0; i < scripts.length; i++) {
                var src = scripts[i].src;
                if (src && src.indexOf('script.js') !== -1) {
                    return src.replace(/script\.js.*$/, 'sortable.min.js');
                }
            }
            return '/static/js/sortable.min.js';
        })();
        script.onload = function() { resolve(window.Sortable); };
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

function displaySearchResults(results) {
    var searchResults = document.getElementById('search-results');
    var originalContent = document.getElementById('original-content');
    var frequentCategory = document.getElementById('frequent-category');
    if (!searchResults || !originalContent) return;

    searchResults.innerHTML = '';

    if (results.length > 0) {
        results.forEach(function(item) {
            var a = document.createElement('a');
            a.href = item.url;
            a.className = 'nav-item';
            a.setAttribute('data-category', '搜索结果');
            a.setAttribute('data-title', item.title);
            a.setAttribute('data-icon', item.icon);

            if (isFaIcon(item.icon)) {
                var iconSpan = document.createElement('span');
                iconSpan.className = 'nav-item-icon';
                iconSpan.innerHTML = iconToSvgHtml(item.icon);
                a.appendChild(iconSpan);
            } else {
                var img = document.createElement('img');
                img.src = '/config/' + item.icon;
                img.alt = item.title;
                img.className = 'icon-img';
                a.appendChild(img);
            }

            var textSpan = document.createElement('span');
            textSpan.textContent = item.title;
            a.appendChild(textSpan);

            searchResults.appendChild(a);
        });

        searchResults.style.display = '';
        originalContent.style.display = 'none';
        if (frequentCategory) frequentCategory.style.display = 'none';
    } else {
        searchResults.style.display = 'none';
        originalContent.style.display = '';
        if (frequentCategory) frequentCategory.style.display = '';
    }
}

// 编辑/新增 弹窗逻辑
function openEditModal(initial, targetItem, gridForAdd) {
    var modal = document.getElementById('edit-modal');
    var form = document.getElementById('modalForm');
    if (!modal || !form) return;

    document.getElementById('modal-title').textContent = initial.mode === 'add' ? '新增项目' : '编辑项目';

    form.mode.value = initial.mode;
    form.old_category.value = initial.category || '';
    form.old_title.value = initial.title || '';
    var oldUrlInput = form.querySelector('input[name="old_url"]');
    if (oldUrlInput) oldUrlInput.value = initial.url || '';
    var categorySelect = form.querySelector('select[name="category_select"]');
    if (categorySelect) categorySelect.value = initial.category || '';
    var titleInput = form.querySelector('input[name="title_input"]');
    if (titleInput) titleInput.value = initial.title || '';
    var urlInput = form.querySelector('input[name="url_input"]');
    if (urlInput) urlInput.value = initial.url || '';
    var iconInput = form.querySelector('input[name="icon_input"]');
    if (iconInput) iconInput.value = '';
    var iconSelect = form.querySelector('input[name="icon_select"]');
    if (iconSelect) iconSelect.value = initial.icon || '';
    var iconPreviewImg = form.querySelector('.icon-preview img');

    function updateIconPreview(src) {
        if (iconPreviewImg) {
            if (src) {
                iconPreviewImg.src = src;
                iconPreviewImg.style.display = '';
            } else {
                iconPreviewImg.src = '';
                iconPreviewImg.style.display = 'none';
            }
        }
    }

    if (initial.icon && initial.icon.startsWith('img/')) {
        updateIconPreview('/config/' + initial.icon);
    } else {
        updateIconPreview('');
    }

    var clearBtn = form.querySelector('.icon-clear-btn');
    if (clearBtn) {
        clearBtn.onclick = function() {
            if (iconSelect) iconSelect.value = '';
            if (iconInput) iconInput.value = '';
            updateIconPreview('');
        };
    }

    if (iconSelect) {
        iconSelect.addEventListener('input', function() {
            var val = this.value.trim();
            if (val) {
                updateIconPreview('/config/' + val);
            } else {
                updateIconPreview('');
            }
        });
    }

    if (iconInput) {
        iconInput.addEventListener('change', function() {
            if (currentBlobUrl) {
                URL.revokeObjectURL(currentBlobUrl);
                currentBlobUrl = '';
            }
            if (this.files && this.files[0]) {
                currentBlobUrl = URL.createObjectURL(this.files[0]);
                updateIconPreview(currentBlobUrl);
            }
        });
    }

    modal.style.display = '';

    setTimeout(function() {
        var ti = form.querySelector('input[name="title_input"]');
        if (ti) ti.focus();
    }, 0);

    var currentBlobUrl = '';
    function closeModal() {
        if (currentBlobUrl) {
            URL.revokeObjectURL(currentBlobUrl);
            currentBlobUrl = '';
        }
        modal.style.display = 'none';
        document.removeEventListener('keydown', escHandler);
        document.querySelectorAll('.modal-close, .modal-cancel').forEach(function(btn) {
            btn.removeEventListener('click', closeClickHandler);
        });
        form.removeEventListener('submit', submitHandler);
    }

    function escHandler(e) {
        if (e.key === 'Escape') {
            e.stopPropagation();
            closeModal();
        }
    }

    var closeClickHandler = function() { closeModal(); };

    document.addEventListener('keydown', escHandler);
    document.querySelectorAll('.modal-close, .modal-cancel').forEach(function(btn) {
        btn.addEventListener('click', closeClickHandler);
    });

    function submitHandler(e) {
        e.preventDefault();

        var formData = new FormData();
        var mode = form.mode.value;
        var newCategory = (form.querySelector('select[name="category_select"]') || {}).value || '';
        var newTitle = (form.querySelector('input[name="title_input"]') || {}).value || '';
        var newUrl = (form.querySelector('input[name="url_input"]') || {}).value || '';
        var iconFileInput = form.querySelector('input[name="icon_input"]');
        var iconFile = iconFileInput && iconFileInput.files ? iconFileInput.files[0] : null;
        var iconSelect = form.querySelector('input[name="icon_select"]');
        var iconSelectValue = iconSelect ? iconSelect.value.trim() : '';

        if (mode === 'add') {
            formData.append('action', 'add');
            formData.append('category', newCategory);
            formData.append('title', newTitle);
            formData.append('url', newUrl);
            if (iconFile) {
                formData.append('icon', iconFile);
            } else if (iconSelectValue) {
                formData.append('icon_path', iconSelectValue);
            }
        } else {
            formData.append('action', 'edit');
            formData.append('old_category', form.old_category.value);
            formData.append('old_title', form.old_title.value);
            formData.append('old_url', (form.querySelector('input[name="old_url"]') || {}).value || '');
            formData.append('new_category', newCategory);
            formData.append('new_title', newTitle);
            formData.append('new_url', newUrl);
            if (iconFile) {
                formData.append('new_icon', iconFile);
            } else if (iconSelectValue) {
                formData.append('new_icon_path', iconSelectValue);
            }
        }

        fetch('/config', {
            method: 'POST',
            body: formData
        })
            .then(function() {
                if (mode === 'add') {
                    var newItem = document.createElement('a');
                    newItem.href = newUrl;
                    newItem.className = 'nav-item';
                    newItem.setAttribute('data-category', newCategory);
                    newItem.setAttribute('data-title', newTitle);

                    if (iconSelectValue) {
                        var img = document.createElement('img');
                        img.className = 'icon-img';
                        img.alt = newTitle;
                        img.src = '/config/' + iconSelectValue;
                        newItem.appendChild(img);
                        newItem.setAttribute('data-icon', iconSelectValue);
                    } else if (iconFile) {
                        var img = document.createElement('img');
                        img.className = 'icon-img';
                        img.alt = newTitle;
                        img.src = URL.createObjectURL(iconFile);
                        newItem.appendChild(img);
                    } else {
                        var span = document.createElement('span');
                        span.className = 'nav-item-icon';
                        span.innerHTML = iconToSvgHtml('fas fa-link');
                        newItem.appendChild(span);
                        newItem.setAttribute('data-icon', 'fas fa-link');
                    }

                    var textSpan = document.createElement('span');
                    textSpan.textContent = newTitle;
                    newItem.appendChild(textSpan);

                    var controls = document.createElement('div');
                    controls.className = 'nav-item-controls';
                    controls.style.display = 'none';
                    newItem.appendChild(controls);

                    var targetGrid = gridForAdd;
                    if (!targetGrid) {
                        var grids = document.querySelectorAll('.nav-grid');
                        for (var i = 0; i < grids.length; i++) {
                            var h2 = grids[i].previousElementSibling;
                            if (h2 && h2.textContent === newCategory) {
                                targetGrid = grids[i];
                                break;
                            }
                        }
                    }

                    if (targetGrid) {
                        var addBtn = targetGrid.querySelector('.add-item');
                        if (addBtn) {
                            targetGrid.insertBefore(newItem, addBtn);
                        } else {
                            targetGrid.appendChild(newItem);
                        }
                    }
                } else if (targetItem) {
                    targetItem.setAttribute('href', newUrl);
                    targetItem.setAttribute('data-title', newTitle);
                    var textSpanEl = targetItem.querySelector('span:not(.nav-item-icon)');
                    if (textSpanEl) textSpanEl.textContent = newTitle;

                    if (iconFile) {
                        var iconImg = targetItem.querySelector('img.icon-img');
                        var existingIcon = targetItem.querySelector('.nav-item-icon');
                        var newIconSrc = URL.createObjectURL(iconFile);
                        if (iconImg) {
                            iconImg.src = newIconSrc;
                        } else if (existingIcon) {
                            var newImg = document.createElement('img');
                            newImg.className = 'icon-img';
                            newImg.alt = newTitle;
                            newImg.src = newIconSrc;
                            existingIcon.replaceWith(newImg);
                        }
                        targetItem.setAttribute('data-icon', '');
                    } else if (iconSelectValue) {
                        var existingImg2 = targetItem.querySelector('img.icon-img');
                        var existingIcon2 = targetItem.querySelector('.nav-item-icon');
                        if (existingImg2) {
                            existingImg2.src = '/config/' + iconSelectValue;
                        } else if (existingIcon2) {
                            var newImg2 = document.createElement('img');
                            newImg2.className = 'icon-img';
                            newImg2.alt = newTitle;
                            newImg2.src = '/config/' + iconSelectValue;
                            existingIcon2.replaceWith(newImg2);
                        }
                        targetItem.setAttribute('data-icon', iconSelectValue);
                    }

                    var oldCategory = form.old_category.value;
                    if (oldCategory !== '常用') {
                        var oldGrid = targetItem.closest('.nav-grid');
                        var newGrid = null;
                        var allGrids = document.querySelectorAll('.nav-grid');
                        for (var j = 0; j < allGrids.length; j++) {
                            var prev = allGrids[j].previousElementSibling;
                            if (prev && prev.textContent === newCategory) {
                                newGrid = allGrids[j];
                                break;
                            }
                        }
                        if (newGrid && oldGrid && oldGrid !== newGrid) {
                            var addBtnNew = newGrid.querySelector('.add-item');
                            if (addBtnNew) {
                                newGrid.insertBefore(targetItem, addBtnNew);
                            } else {
                                newGrid.appendChild(targetItem);
                            }
                            targetItem.setAttribute('data-category', newCategory);
                        }
                    }
                }
                closeModal();
                initVisitStats();
            })
            .catch(function(err) { console.warn('保存失败:', err); });
    }

    form.addEventListener('submit', submitHandler);
}

// DOMContentLoaded 初始化
document.addEventListener('DOMContentLoaded', function() {
    initVisitStats();
    initBadgesVisibility();
    attachVisitTracking();

    var toggleBtn = document.getElementById('toggle-badges');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            toggleBadgesVisibility();
        });
    }

    var searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            var searchTerm = this.value.toLowerCase();

            if (searchTerm.length > 0) {
                fetch('/search?term=' + encodeURIComponent(searchTerm), { method: 'GET' })
                    .then(function(res) { return res.json(); })
                    .then(function(response) {
                        displaySearchResults(response);
                    })
                    .catch(function(err) { console.warn('搜索失败:', err); });
            } else {
                var searchResults = document.getElementById('search-results');
                var originalContent = document.getElementById('original-content');
                var frequentCategory = document.getElementById('frequent-category');
                if (searchResults) searchResults.style.display = 'none';
                if (originalContent) originalContent.style.display = '';
                if (frequentCategory) frequentCategory.style.display = '';
            }
        });
    }

    // 添加分类弹窗的关闭和提交逻辑
    var addCategoryModal = document.getElementById('add-category-modal');
    var addCategoryForm = addCategoryForm || null;
    var addCatCloseBtns, addCatEscHandler;
    
    function openAddCategoryModal(mode, oldCategoryName) {
        var modal = addCategoryModal;
        if (!modal) return;
        
        var form = modal.querySelector('form');
        var titleEl = document.getElementById('category-modal-title');
        var modeInput = form ? form.querySelector('input[name="mode"]') : null;
        var oldCatInput = form ? form.querySelector('input[name="old_category"]') : null;
        var nameInput = form ? form.querySelector('input[name="category_name"]') : null;
        
        if (titleEl) {
            titleEl.textContent = mode === 'edit' ? '编辑分类' : '添加分类';
        }
        if (modeInput) modeInput.value = mode || 'add';
        if (oldCatInput) oldCatInput.value = oldCategoryName || '';
        if (nameInput) nameInput.value = mode === 'edit' ? (oldCategoryName || '') : '';
        
        modal.style.display = '';
        setTimeout(function() { if (nameInput) nameInput.focus(); }, 0);
    }

    if (addCategoryModal) {
        addCategoryForm = addCategoryModal.querySelector('form');
        addCatCloseBtns = addCategoryModal.querySelectorAll('.modal-close, .modal-cancel');
        addCatEscHandler = function(e) { if (e.key === 'Escape') addCategoryModal.style.display = 'none'; };
        
        addCatCloseBtns.forEach(function(btn) {
            btn.addEventListener('click', function() { addCategoryModal.style.display = 'none'; });
        });
        document.addEventListener('keydown', addCatEscHandler);

        if (addCategoryForm) {
            addCategoryForm.addEventListener('submit', function(e) {
                e.preventDefault();
                var input = addCategoryForm.querySelector('input[name="category_name"]');
                var categoryName = input ? input.value.trim() : '';
                if (!categoryName) return;

                var mode = (addCategoryForm.querySelector('input[name="mode"]') || {}).value || 'add';
                var oldCategory = (addCategoryForm.querySelector('input[name="old_category"]') || {}).value || '';
                
                var formData = new FormData();
                if (mode === 'edit' && oldCategory) {
                    formData.append('action', 'edit_category');
                    formData.append('old_category', oldCategory);
                    formData.append('new_category', categoryName);
                } else {
                    formData.append('action', 'add_category');
                    formData.append('category', categoryName);
                }

                fetch('/config', { method: 'POST', body: formData })
                    .then(function() { return fetch('/'); })
                    .then(function() { window.location.reload(); })
                    .catch(function(err) { console.warn('保存分类失败:', err); });
            });
        }
    }

    // 空状态的添加分类按钮
    var addFirstCategoryBtn = document.getElementById('add-first-category');
    if (addFirstCategoryBtn) {
        addFirstCategoryBtn.addEventListener('click', function() {
            openAddCategoryModal('add', '');
        });
    }

    // 每个分类标题后的添加分类按钮
    document.addEventListener('click', function(e) {
        var addCatBtn = e.target.closest('.add-category-btn');
        if (!addCatBtn) return;
        var header = addCatBtn.closest('.category-header');
        var categoryName = header ? header.dataset.category : '';
        openAddCategoryModal('add', categoryName);
    });

    // 右键菜单 for items
    var contextMenu = document.getElementById('context-menu');
    var categoryContextMenu = document.getElementById('category-context-menu');
    var contextTarget = null;
    var categoryContextTarget = null;

    document.addEventListener('contextmenu', function(e) {
        var target = e.target.closest('.nav-item:not(.add-item)');
        if (!target) return;
        e.preventDefault();

        contextTarget = target;
        var category = target.dataset.category || '';

        var editLi = contextMenu ? contextMenu.querySelector('li[data-action="edit"]') : null;
        if (editLi) {
            editLi.style.display = category === '常用' ? 'none' : '';
        }

        if (contextMenu) {
            contextMenu.style.top = e.pageY + 'px';
            contextMenu.style.left = e.pageX + 'px';
            contextMenu.style.display = '';
        }
    });

    document.addEventListener('click', function() {
        if (contextMenu) contextMenu.style.display = 'none';
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && contextMenu) contextMenu.style.display = 'none';
    });

    if (contextMenu) {
        contextMenu.addEventListener('click', function(e) {
            var li = e.target.closest('li');
            if (!li || !contextTarget) return;
            e.stopPropagation();

            var action = li.dataset.action;
            var category = contextTarget.dataset.category || '';
            var title = contextTarget.dataset.title || '';

            if (action === 'edit') {
                if (category === '常用') return;
                openEditModal({
                    mode: 'edit',
                    category: category,
                    title: title,
                    url: contextTarget.getAttribute('href') || '',
                    icon: contextTarget.getAttribute('data-icon') || ''
                }, contextTarget, null);
            } else if (action === 'delete') {
                if (!confirm('确定删除该项目吗？')) {
                    contextMenu.style.display = 'none';
                    return;
                }
                var deleteData = new FormData();
                deleteData.append('action', 'delete');
                deleteData.append('category', category);
                deleteData.append('title', title);
                if (category === '常用') {
                    deleteData.append('url', contextTarget.getAttribute('href') || '');
                }

                fetch('/config', {
                    method: 'POST',
                    body: deleteData
                })
                    .then(function() {
                        contextTarget.remove();
                        initVisitStats();
                    })
                    .catch(function(err) { console.warn('删除失败:', err); });
            }

            contextMenu.style.display = 'none';
        });
    }

    // 分类标题右键菜单
    document.addEventListener('contextmenu', function(e) {
        var target = e.target.closest('.category-header');
        if (!target) return;
        e.preventDefault();
        
        var categoryName = target.dataset.category || '';
        if (categoryName === '常用') return;
        
        categoryContextTarget = target;
        if (categoryContextMenu) {
            categoryContextMenu.style.top = e.pageY + 'px';
            categoryContextMenu.style.left = e.pageX + 'px';
            categoryContextMenu.style.display = '';
        }
    });

    document.addEventListener('click', function() {
        if (categoryContextMenu) categoryContextMenu.style.display = 'none';
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && categoryContextMenu) categoryContextMenu.style.display = 'none';
    });

    if (categoryContextMenu) {
        categoryContextMenu.addEventListener('click', function(e) {
            var li = e.target.closest('li');
            if (!li || !categoryContextTarget) return;
            e.stopPropagation();
            
            var action = li.dataset.action;
            var categoryName = categoryContextTarget.dataset.category || '';
            
            if (action === 'edit-category') {
                openAddCategoryModal('edit', categoryName);
            } else if (action === 'delete-category') {
                if (!confirm('确定删除分类"' + categoryName + '"吗？该分类下的所有项目也会被删除。')) {
                    categoryContextMenu.style.display = 'none';
                    return;
                }
                var deleteData = new FormData();
                deleteData.append('action', 'delete_category');
                deleteData.append('category', categoryName);
                
                fetch('/config', {
                    method: 'POST',
                    body: deleteData
                })
                    .then(function() { window.location.reload(); })
                    .catch(function(err) { console.warn('删除分类失败:', err); });
            }
            
            categoryContextMenu.style.display = 'none';
        });
    }

    // Add button handler
    document.addEventListener('click', function(e) {
        var addBtn = e.target.closest('.add-item');
        if (!addBtn) return;
        e.preventDefault();

        var category = addBtn.dataset.category || '';
        var grid = addBtn.closest('.nav-grid');
        openEditModal({ mode: 'add', category: category, title: '', url: '' }, null, grid);
    });

    // 动态加载 SortableJS
    var initSortable = function() {
        loadSortable().then(function(Sortable) {
            document.querySelectorAll('.nav-grid').forEach(function(grid) {
                new Sortable(grid, {
                    animation: 150,
                    delay: 150,
                    delayOnTouchOnly: true,
                    ghostClass: 'drag-ghost',
                    chosenClass: 'drag-chosen',
                    dragClass: 'drag-dragging',
                    filter: '.add-item',
                    preventOnFilter: true,
                    onMove: function(evt) {
                        return !evt.related.classList.contains('add-item');
                    },
                    onEnd: function(evt) {
                        var h2 = grid.previousElementSibling;
                        var category = h2 ? h2.textContent : '';
                        var items = grid.querySelectorAll('.nav-item:not(.add-item)');
                        var order = [];
                        for (var k = 0; k < items.length; k++) {
                            var t = items[k].dataset.title;
                            if (t) order.push(t);
                        }
                        if (category && order.length) {
                            var fd = new FormData();
                            fd.append('action', 'reorder');
                            fd.append('category', category);
                            order.forEach(function(o) { fd.append('order[]', o); });
                            fetch('/config', { method: 'POST', body: fd }).catch(function(err) { console.warn('排序保存失败:', err); });
                        }
                    }
                });
            });
        }).catch(function(err) { console.warn('SortableJS 加载失败:', err); });
    };

    if (typeof requestIdleCallback !== 'undefined') {
        requestIdleCallback(function() { initSortable(); }, { timeout: 2000 });
    } else {
        setTimeout(initSortable, 0);
    }
});
