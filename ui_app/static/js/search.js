$(document).ready(function() {
    $('#search').click(function() {
        // Clear any existing results or messages
        $('#results').empty();
        clearCharts();

        var author = $('#author').val();
        var content = $('#content').val();
        var language = $('#language').val();

        $.ajax({
            url: '/search',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                filters: {
                    author: author,
                    content: content,
                    language: language
                }
            }),
            success: function(response) {
                var results = response.result;
                if (results.length > 0) {
                    // Render charts
                    renderDateChart(results);
                    renderLikesHistogram(results);
                    renderWordCountChart(results);
                } else {
                    $('#results').html('<div class="alert alert-info">No results found.</div>');
                }
            },
            error: function(xhr, status, error) {
                $('#results').html('<div class="alert alert-danger">An error occurred: ' + error + '</div>');
            }
        });
    });
});

//  clear all charts
function clearCharts() {
    ['dateChart', 'likesHistogram', 'wordCountChart'].forEach(clearCanvas);
}

function clearCanvas(canvasId) {
    var canvas = document.getElementById(canvasId);
    if (canvas) {
        var ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Remove the old canvas and replace it with a new one
        var newCanvas = document.createElement('canvas');
        newCanvas.id = canvasId;
        newCanvas.width = canvas.width;
        newCanvas.height = canvas.height;
        canvas.parentNode.replaceChild(newCanvas, canvas);
    }
}

function renderDateChart(data) {
    const countsByDate = {};
    data.forEach(tweet => {
        const date = new Date(tweet.date_time).toISOString().split('T')[0];
        countsByDate[date] = (countsByDate[date] || 0) + 1;
    });

    const ctx = document.getElementById('dateChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(countsByDate),
            datasets: [{
                label: 'Tweets by Date',
                data: Object.values(countsByDate),
                backgroundColor: 'rgba(0, 123, 255, 0.5)',
                borderColor: 'rgba(0, 123, 255, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{ ticks: { beginAtZero: true } }]
            }
        }
    });
}

function renderLikesHistogram(data) {
    const likesRanges = { '0-100': 0, '101-500': 0, '501-1000': 0, '1001-5000': 0, '5001+': 0 };
    data.forEach(tweet => {
        const likes = tweet.number_of_likes;
        if (likes <= 100) likesRanges['0-100']++;
        else if (likes <= 500) likesRanges['101-500']++;
        else if (likes <= 1000) likesRanges['501-1000']++;
        else if (likes <= 5000) likesRanges['1001-5000']++;
        else likesRanges['5001+']++;
    });

    const ctx = document.getElementById('likesHistogram').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(likesRanges),
            datasets: [{
                label: 'Number of Likes',
                data: Object.values(likesRanges),
                backgroundColor: 'rgba(40, 167, 69, 0.5)',
                borderColor: 'rgba(40, 167, 69, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{ ticks: { beginAtZero: true } }]
            }
        }
    });
}


function renderWordCountChart(data) {
    const wordCounts = data.map(tweet => tweet.content.split(' ').length);
    const maxWordCount = Math.max(...wordCounts);
    const wordCountRanges = Array.from({ length: maxWordCount + 1 }, () => 0);
    wordCounts.forEach(count => wordCountRanges[count]++);

    const ctx = document.getElementById('wordCountChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: wordCountRanges.map((_, i) => i),
            datasets: [{
                label: 'Word Count per Tweet',
                data: wordCountRanges,
                backgroundColor: 'rgba(255, 193, 7, 0.5)',
                borderColor: 'rgba(255, 193, 7, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{ ticks: { beginAtZero: true } }],
                xAxes: [{ ticks: { autoSkip: true, maxTicksLimit: 20 } }]
            }
        }
    });
}

