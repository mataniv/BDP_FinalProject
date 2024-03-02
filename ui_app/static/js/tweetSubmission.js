document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('tweetForm');
    form.onsubmit = function(event) {
        event.preventDefault();
        var tweetText = document.getElementById('tweetText').value;
        var messageElement = document.getElementById('message');

        fetch('/post_tweet', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'tweet_text=' + encodeURIComponent(tweetText)
        })
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (data.message === 'Processed successfully.') {
                messageElement.textContent = 'Post successful!';
                messageElement.classList.add('text-success');
            } else {
                throw new Error('Upload failed.');
            }
        })
        .catch(function(error) {
            messageElement.textContent = 'Upload failed, Please verify that you updated your credentials';
            messageElement.classList.add('text-danger');
        });
    };
});
