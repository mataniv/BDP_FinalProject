document.addEventListener('DOMContentLoaded', function() {
    fetchDataForCharts();
});

function fetchDataForCharts() {
    fetch('/chart-data')
    .then(response => {
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        renderTweetsPerYearChart(data.tweets_by_year);
        renderTopAuthorsTable(data.top_authors);
    })
    .catch(error => {
        console.error('Error fetching data:', error);
    });
}
// ... rest of your existing `renderTweetsPerYearChart` and `renderTopAuthorsTable` functions

function renderTweetsPerYearChart(tweetsByYear) {
    const ctxYear = document.getElementById('tweetsByYearChart').getContext('2d');
    new Chart(ctxYear, {
        type: 'bar',
        data: {
            labels: Object.keys(tweetsByYear),
            datasets: [{
                label: 'Number of Tweets per Year',
                data: Object.values(tweetsByYear),
                backgroundColor: 'rgba(0, 123, 255, 0.5)',
                borderColor: 'rgba(0, 123, 255, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function renderTopAuthorsTable(topAuthors) {
    const tableBody = document.getElementById('topAuthorsBody');
    topAuthors.forEach(author => {
        let row = tableBody.insertRow();
        let cell1 = row.insertCell(0);
        let cell2 = row.insertCell(1);
        cell1.innerHTML = author.tweetCount; // This should represent the author's name
        cell2.innerHTML = author.count; // This should represent the tweet count
    });
}
