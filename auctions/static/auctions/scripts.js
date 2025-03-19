// Prevents closing a bid by mistake
document.getElementById("close-bidding-button").addEventListener("click", function (event) {
    // Show confirmation popup
    let confirmClose = confirm("Are you sure you want to close this listing?");

    if (!confirmClose) {
        event.preventDefault(); // Prevent form submission if user cancels
    }
});

// Associated with create listing page

function updateLabelAlignment() {
    const labels = document.querySelectorAll('#listing-container [data-label-alignment]');
    const isSmallScreen = window.innerWidth <= 768; // Adjust breakpoint as needed

    labels.forEach(label => {
        if (isSmallScreen) {
            label.classList.remove('text-end');
            label.classList.add('text-start');
            label.setAttribute('data-label-alignment', 'left');
        } else {
            label.classList.remove('text-start');
            label.classList.add('text-end');
            label.setAttribute('data-label-alignment', 'right');
        }
    });
}

// Initial alignment and on resize
updateLabelAlignment();
window.addEventListener('resize', updateLabelAlignment);