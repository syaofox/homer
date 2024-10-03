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
});

function displaySearchResults(results) {
    var $searchResults = $('#search-results');
    $searchResults.empty();

    if (results.length > 0) {
        results.forEach(function(item) {
            var $item = $('<a>')
                .attr('href', item.url)
                .attr('target', '_blank')
                .addClass('nav-item');

            if (item.icon.startsWith('fas ') || item.icon.startsWith('fab ')) {
                $item.append($('<i>').addClass(item.icon));
            } else {
                $item.append($('<img>')
                    .attr('src', '/static/' + item.icon)
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