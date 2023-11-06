function updateDateTime() {
    const dateTimeElement = document.getElementById("date-time");
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', timeZoneName: 'short' };
    const formattedDateTime = now.toLocaleDateString(undefined, options);
    dateTimeElement.textContent = formattedDateTime;
}

setInterval(updateDateTime, 1000); // Update every 1 second

// Call the function to update the date and time immediately and set it to update every second.
updateDateTime();






