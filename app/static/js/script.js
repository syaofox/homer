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

    // Handle context menu actions
    $contextMenu.on('click', 'li', function(e) {
        e.stopPropagation();
        const action = $(this).data('action');
        if (!contextTarget) return;
        const $target = $(contextTarget);
        const category = $target.data('category');
        const title = $target.data('title');
        if (action === 'edit') {
            // Open config page to edit this item
            const url = '/config?edit_category=' + encodeURIComponent(category) + '&edit_title=' + encodeURIComponent(title);
            window.open(url, '_blank');
        } else if (action === 'delete') {
            // Open config page focusing this item so user can delete there
            const url = '/config?edit_category=' + encodeURIComponent(category) + '&edit_title=' + encodeURIComponent(title);
            window.open(url, '_blank');
        }
        $contextMenu.hide();
    });

    // Add button handler
    $(document).on('click', '.add-item', function(e) {
        e.preventDefault();
        const category = $(this).data('category');
        const url = '/config?add_category=' + encodeURIComponent(category);
        window.open(url, '_blank');
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
// No-op helpers removed; navigation to /config is used instead