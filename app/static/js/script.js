function updateDateTime() {
    var now = new Date();
    var dateElement = document.getElementById('date');
    var timeElement = document.getElementById('time');

    var options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    dateElement.textContent = now.toLocaleDateString(undefined, options);

    var timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
    timeElement.textContent = now.toLocaleTimeString(undefined, timeOptions);
}

// Call the function to update the date and time immediately and set it to update every second.
updateDateTime();
setInterval(updateDateTime, 1000); // Update every 1 second





