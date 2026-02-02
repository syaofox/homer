console.log('个人导航页面已加载');

// 访问统计相关功能
let visitStats = {};
let badgesVisible = true; // 角标显示状态

// 初始化访问统计数据 - 从服务器获取
function initVisitStats() {
    $.ajax({
        url: '/api/visit-stats',
        method: 'GET',
        success: function(data) {
            visitStats = data;
            renderFrequentCategory();
        },
        error: function(xhr, status, error) {
            console.warn('无法读取访问统计数据:', error);
            visitStats = {};
        }
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
    
    // 保存状态到localStorage
    try {
        localStorage.setItem('badgesVisible', JSON.stringify(badgesVisible));
    } catch (e) {
        console.warn('无法保存角标显示状态:', e);
    }
}

// 更新角标显示状态
function updateBadgesVisibility() {
    if (badgesVisible) {
        $('body').removeClass('badges-hidden');
    } else {
        $('body').addClass('badges-hidden');
    }
}

// 更新切换按钮状态
function updateToggleButton() {
    const $btn = $('#toggle-badges');
    const $icon = $btn.find('i');
    const $text = $btn.find('span');
    
    if (badgesVisible) {
        $btn.addClass('active');
        $icon.removeClass('fa-eye-slash').addClass('fa-eye');
        // $text.text('隐藏次数');
    } else {
        $btn.removeClass('active');
        $icon.removeClass('fa-eye').addClass('fa-eye-slash');
        // $text.text('显示次数');
    }
}

// 记录访问 - 发送到服务器
function recordVisit(title, icon, url) {
    if (!url) return;
    
    // 发送到服务器
    $.ajax({
        url: '/api/visit-stats/record',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            url: url,
            title: title,
            icon: icon
        }),
        success: function(response) {
            if (response.success && response.data) {
                // 更新本地缓存
                visitStats[url] = response.data;
            }
        },
        error: function(xhr, status, error) {
            console.warn('无法保存访问统计数据:', error);
        }
    });
}

// 获取访问频率最高的站点
function getTopVisitedSites(limit = 20) {
    const sites = Object.values(visitStats);
    return sites
        .sort((a, b) => b.count - a.count)
        .slice(0, limit);
}

// 渲染常用分类
function renderFrequentCategory() {
    const topSites = getTopVisitedSites();
    if (topSites.length === 0) return;
    
    const $frequentCategory = $('#frequent-category');
    $frequentCategory.empty();
    
    // 创建分类标题
    const $title = $('<h2>').text('常用');
    $frequentCategory.append($title);
    
    // 创建网格容器
    const $grid = $('<div>').addClass('nav-grid');
    
    // 添加站点
    topSites.forEach(function(site) {
        const $item = $('<a>')
            .attr('href', site.url)
            .addClass('nav-item')
            .attr('data-category', '常用')
            .attr('data-title', site.title);
        
        // 添加图标
        if (site.icon.startsWith('fas ') || site.icon.startsWith('fab ')) {
            $item.append($('<i>').addClass(site.icon));
        } else {
            $item.append($('<img>')
                .attr('src', '/config/' + site.icon)
                .attr('alt', site.title)
                .addClass('icon-img'));
        }
        
        // 添加点击次数徽章
        if (site.count > 0) {
            const $badge = $('<div>')
                .addClass('click-badge')
                .text(site.count);
            $item.append($badge);
        }
        
        $item.append($('<span>').text(site.title));
        $grid.append($item);
    });
    
    $frequentCategory.append($grid);
    $frequentCategory.show();
}

// 为所有导航链接添加点击统计
function attachVisitTracking() {
    $(document).on('click', '.nav-item:not(.add-item)', function(e) {
        const $this = $(this);
        const title = $this.data('title') || $this.find('span').text();
        const url = $this.attr('href');
        
        // 获取图标信息
        let icon = 'fas fa-link'; // 默认图标
        const $icon = $this.find('i');
        const $img = $this.find('img');
        
        if ($icon.length) {
            icon = $icon.attr('class');
        } else if ($img.length) {
            icon = $img.attr('src').replace('/config/', '');
        }
        
        recordVisit(title, icon, url);
    });
}

$(document).ready(function() {
    // 初始化访问统计（会在成功后自动渲染常用分类）
    initVisitStats();
    
    // 初始化角标显示状态
    initBadgesVisibility();
    
    // 添加访问跟踪
    attachVisitTracking();
    
    // 角标显示切换按钮事件
    $('#toggle-badges').on('click', function(e) {
        e.preventDefault();
        toggleBadgesVisibility();
    });
    
    $('#search-input').on('input', function() {
        var searchTerm = $(this).val().toLowerCase();
        
        if (searchTerm.length > 0) {
            $.ajax({
                url: '/search',
                method: 'GET',
                data: { term: searchTerm },
                success: function(response) {
                    displaySearchResults(response);
                }
            });
        } else {
            $('#search-results').hide();
            $('#original-content').show();
        }
    });

    // Right-click context menu for nav items
    let $contextMenu = $('#context-menu');
    let contextTarget = null; // DOM element of clicked item

    $(document).on('contextmenu', '.nav-item:not(.add-item)', function(e) {
        e.preventDefault();
        contextTarget = this;
        $contextMenu.css({ top: e.pageY + 'px', left: e.pageX + 'px' }).show();
    });

    // Hide context menu on click elsewhere or Escape
    $(document).on('click', function() { $contextMenu.hide(); });
    $(document).on('keydown', function(e) { if (e.key === 'Escape') { $contextMenu.hide(); } });

    // 处理右键菜单：改为原地编辑/删除
    $contextMenu.on('click', 'li', function(e) {
        e.stopPropagation();
        const action = $(this).data('action');
        if (!contextTarget) return;
        const $target = $(contextTarget);
        const category = $target.data('category');
        const title = $target.data('title');
        if (action === 'edit') {
            openEditModal({
                mode: 'edit',
                category: category,
                title: title,
                url: $target.attr('href') || ''
            }, $target);
        } else if (action === 'delete') {
            if (!confirm('确定删除该项目吗？')) { $contextMenu.hide(); return; }
            const deleteData = {
                action: 'delete',
                category: category,
                title: title
            };
            if (category === '常用') {
                deleteData.url = $target.attr('href') || '';
            }
            $.ajax({
                url: '/config',
                method: 'POST',
                data: deleteData,
                success: function() {
                    // 前端移除
                    $target.remove();
                }
            });
        }
        $contextMenu.hide();
    });

    // Add button handler -> 打开新增弹窗
    $(document).on('click', '.add-item', function(e) {
        e.preventDefault();
        const category = $(this).data('category');
        openEditModal({ mode: 'add', category: category, title: '', url: '' }, null, $(this).closest('.nav-grid'));
    });

    // 使用 SortableJS 提升拖拽体验
    $('.nav-grid').each(function(){
        const grid = this;
        new Sortable(grid, {
            animation: 150,
            delay: 150, // 长按延时，避免误触
            delayOnTouchOnly: true,
            ghostClass: 'drag-ghost',
            chosenClass: 'drag-chosen',
            dragClass: 'drag-dragging',
            filter: '.add-item',
            preventOnFilter: true,
            onMove: function(evt) {
                // 禁止将普通卡片拖到“新增”后面
                return !$(evt.related).hasClass('add-item');
            },
            onEnd: function(evt) {
                const $grid = $(grid);
                const category = $grid.prev('h2').text();
                const order = $grid.find('.nav-item').not('.add-item').map(function(){
                    return $(this).data('title');
                }).get();
                if (category && order.length) {
                    $.ajax({ url: '/config', method: 'POST', data: { action: 'reorder', category: category, 'order[]': order } });
                }
            }
        });
    });
});

function displaySearchResults(results) {
    var $searchResults = $('#search-results');
    $searchResults.empty();

    if (results.length > 0) {
        results.forEach(function(item) {
            var $item = $('<a>')
                .attr('href', item.url)
                // .attr('target', '_blank')
                .addClass('nav-item')
                .attr('data-category', '搜索结果')
                .attr('data-title', item.title);

            if (item.icon.startsWith('fas ') || item.icon.startsWith('fab ')) {
                $item.append($('<i>').addClass(item.icon));
            } else {
                $item.append($('<img>')
                    .attr('src', '/config/' + item.icon)
                    .attr('alt', item.title)
                    .addClass('icon-img'));
            }

            $item.append($('<span>').text(item.title));
            $searchResults.append($item);
        });

        $('#search-results').show();
        $('#original-content').hide();
        $('#frequent-category').hide();
    } else {
        $('#search-results').hide();
        $('#original-content').show();
        $('#frequent-category').show();
    }
}

// Helpers for actions
// 编辑/新增 弹窗逻辑
function openEditModal(initial, $targetItem, $gridForAdd) {
    const $modal = $('#edit-modal');
    const $form = $('#modalForm')[0];
    const $formJq = $('#modalForm');
    $('#modal-title').text(initial.mode === 'add' ? '新增项目' : '编辑项目');

    // 预填
    $form.mode.value = initial.mode;
    $form.old_category.value = initial.category || '';
    $form.old_title.value = initial.title || '';
    $formJq.find('input[name="old_url"]').val(initial.url || '');
    $formJq.find('select[name="category_select"]').val(initial.category || '');
    $formJq.find('input[name="title_input"]').val(initial.title || '');
    $formJq.find('input[name="url_input"]').val(initial.url || '');
    $formJq.find('input[name="icon_input"]').val('');

    $modal.show();
    // 弹窗打开后将焦点置于标题输入框
    setTimeout(function(){ $formJq.find('input[name="title_input"]').trigger('focus'); }, 0);

    // 绑定 Esc 关闭
    $(document).off('keydown.editmodal').on('keydown.editmodal', function(e){
        if (e.key === 'Escape') {
            e.stopPropagation();
            close();
        }
    });

    function close() {
        $modal.hide();
        $(document).off('keydown.editmodal');
    }
    $('.modal-close, .modal-cancel').off('click').on('click', function() { close(); });

    $formJq.off('submit').on('submit', function(e) {
        e.preventDefault();
        const formData = new FormData();
        const mode = $form.mode.value;
        const newCategory = $formJq.find('select[name="category_select"]').val();
        const newTitle = $formJq.find('input[name="title_input"]').val();
        const newUrl = $formJq.find('input[name="url_input"]').val();
        const iconFile = $formJq.find('input[name="icon_input"]').prop('files')[0];

        if (mode === 'add') {
            formData.append('action', 'add');
            formData.append('category', newCategory);
            formData.append('title', newTitle);
            formData.append('url', newUrl);
            if (iconFile) formData.append('icon', iconFile);
        } else {
            formData.append('action', 'edit');
            formData.append('old_category', $form.old_category.value);
            formData.append('old_title', $form.old_title.value);
            formData.append('old_url', $formJq.find('input[name="old_url"]').val() || '');
            formData.append('new_category', newCategory);
            formData.append('new_title', newTitle);
            formData.append('new_url', newUrl);
            if (iconFile) formData.append('new_icon', iconFile);
        }

        $.ajax({
            url: '/config',
            method: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function() {
                if (mode === 'add') {
                    // 前端新增一个卡片
                    const $new = $('<a>')
                        .attr('href', newUrl)
                        .addClass('nav-item')
                        .attr('data-category', newCategory)
                        .attr('data-title', newTitle);
                    $new.append(iconFile ? $('<img>').addClass('icon-img').attr('alt', newTitle).attr('src', URL.createObjectURL(iconFile))
                                          : $('<i>').addClass('fas fa-link'));
                    $new.append($('<span>').text(newTitle));
                    $new.append($(
                        '<div class="nav-item-controls" style="display:none;"></div>'
                    ));
                    const $grid = $gridForAdd || $('.nav-grid').filter(function(){
                        return $(this).prev('h2').text() === newCategory;
                    }).first();
                    const $addBtn = $grid.find('.add-item');
                    if ($addBtn.length) {
                        $new.insertBefore($addBtn);
                    } else {
                        $grid.append($new);
                    }
                } else if ($targetItem) {
                    // 前端更新卡片文本和跳转
                    $targetItem.attr('href', newUrl);
                    $targetItem.attr('data-title', newTitle);
                    $targetItem.find('span').text(newTitle);
                    // 常用分组只原地更新，不移动；其它分类若改变则移至对应分组
                    const oldCategory = $form.old_category.value;
                    if (oldCategory !== '常用') {
                        const oldGrid = $targetItem.closest('.nav-grid');
                        const newGrid = $('.nav-grid').filter(function(){
                            return $(this).prev('h2').text() === newCategory;
                        }).first();
                        if (newGrid.length && !oldGrid.is(newGrid)) {
                            const $addBtn = newGrid.find('.add-item');
                            if ($addBtn.length) {
                                $targetItem.insertBefore($addBtn);
                            } else {
                                newGrid.append($targetItem);
                            }
                            $targetItem.attr('data-category', newCategory);
                        }
                    }
                }
                close();
            }
        });
    });
}