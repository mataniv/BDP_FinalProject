document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('ingestForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const text = document.getElementById('textInput').value;
        const fieldType = document.getElementById('fieldTypeSelect').value;

        fetch('/ingest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text, field_type: fieldType }),
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('ingestResponse').innerText = data.message;
        })
        .catch(error => console.error('Error:', error));
    });
});
