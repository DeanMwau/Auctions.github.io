// Prevents closing a bid by mistake
document.getElementById("close-bidding-button").addEventListener("click", function (event) {
    // Show confirmation popup
    let confirmClose = confirm("Are you sure you want to close this listing?");

    if (!confirmClose) {
        event.preventDefault(); // Prevent form submission if user cancels
    }
});

