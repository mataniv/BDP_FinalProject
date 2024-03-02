$(document).ready(function() {
    $('#loadData').click(function() {
        var authorFilter = $('#author_filter').val();
        var contentFilter = $('#content_filter').val();

        var dataToSend = {};
        if(authorFilter) dataToSend.author_filter = authorFilter;
        if(contentFilter) dataToSend.content_filter = contentFilter;

        $.ajax({
            url: '/ingestion',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(dataToSend),
            success: function(response) {
                $('#loadResults').html('<div class="alert alert-success">' + response.message + '</div>');
            },
            error: function(xhr, status, error) {
                $('#loadResults').html('<div class="alert alert-danger">Failed loading. Please try again.</div>');
                // Allows users to try loading again without navigating away
            }
        });
    });
});
