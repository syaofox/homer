console.log('个人导航页面已加载');

$(document).ready(function() {
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
            $.ajax({
                url: '/config',
                method: 'POST',
                data: {
                    action: 'delete',
                    category: category,
                    title: title
                },
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

    // 移动按钮：左移/右移（前端先乐观更新，再 Ajax 持久化）
    $(document).on('click', '.move-btn', function(e) {
        e.preventDefault();
        e.stopPropagation();
        const $item = $(this).closest('.nav-item');
        const category = $item.data('category');
        const title = $item.data('title');
        if (!category || !title) return;

        const isLeft = $(this).hasClass('move-left');
        const action = isLeft ? 'move_up' : 'move_down';

        // 仅在同一分组(nav-grid)内移动，跳过“新增”按钮
        const $grid = $item.closest('.nav-grid');
        if ($grid.length === 0) return;

        const $siblings = $grid.find('.nav-item').not('.add-item');
        const index = $siblings.index($item);
        let $swapWith = null;
        if (isLeft) {
            if (index <= 0) return; // 已经最左边
            $swapWith = $siblings.eq(index - 1);
        } else {
            if (index >= $siblings.length - 1) return; // 已经最右边（不包含新增）
            $swapWith = $siblings.eq(index + 1);
        }
        if ($swapWith && $swapWith.length) {
            // 乐观交换 DOM
            if (isLeft) {
                $item.insertBefore($swapWith);
            } else {
                $item.insertAfter($swapWith);
            }
        }

        // 后台持久化
        $.ajax({
            url: '/config',
            method: 'POST',
            data: {
                action: action,
                category: category,
                title: title
            },
            success: function() {
                // 无需刷新，已乐观更新
            },
            error: function() {
                // 出错时简单回退（再次交换还原）
                if ($swapWith && $swapWith.length) {
                    if (isLeft) {
                        $item.insertAfter($swapWith);
                    } else {
                        $item.insertBefore($swapWith);
                    }
                }
                console.error('更新顺序失败');
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
                .addClass('nav-item');

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
    } else {
        $('#search-results').hide();
        $('#original-content').show();
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
    $formJq.find('select[name="category_select"]').val(initial.category || '');
    $formJq.find('input[name="title_input"]').val(initial.title || '');
    $formJq.find('input[name="url_input"]').val(initial.url || '');
    $formJq.find('input[name="icon_input"]').val('');

    $modal.show();
    // 弹窗打开后将焦点置于标题输入框
    setTimeout(function(){ $formJq.find('input[name="title_input"]').trigger('focus'); }, 0);

    function close() { $modal.hide(); }
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
                        '<div class="nav-item-controls">\
                            <button class="move-btn move-left" type="button" title="左移" aria-label="左移"><i class="fas fa-arrow-left"></i></button>\
                            <button class="move-btn move-right" type="button" title="右移" aria-label="右移"><i class="fas fa-arrow-right"></i></button>\
                        </div>'
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
                    // 若分类改变，将卡片移至对应分组
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
                close();
            }
        });
    });
}