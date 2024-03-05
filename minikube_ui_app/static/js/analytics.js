document.addEventListener("DOMContentLoaded", function() {
  document.getElementById('analyticsForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // Serialize the form data
    var formData = new FormData(this);
    var object = {};
    formData.forEach((value, key) => { object[key] = value });
    var json = JSON.stringify(object);

    // Perform the AJAX request to the Flask backend
    fetch('/analytics', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: json
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
      }
      return response.json();
    })
    .then(data => {
      console.log("Data received:", data);
      updateGraphs(data);
    })
    .catch(error => console.error('Error during fetch:', error));
  });
});

function updateGraphs(data) {

}
