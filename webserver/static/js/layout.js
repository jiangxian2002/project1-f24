const hamburger = document.getElementById('hamburger');
const navContain = document.querySelector('.nav-container');
const navDropdown = document.querySelector('.nav-dropdown');
const searchButton = document.querySelector("#search-btn");
const searchEntry = document.querySelector('#search-entry');

// Function to validate search entry
const searchValidate = () => {
    if(searchEntry.value != '') {
        let searchText = searchEntry.value.toLowerCase();  
        let baseUrl = window.location.origin;
        window.location.replace(`${baseUrl}/search/${searchText}`);
    }
}

// Adding event listener on hamburger to show navbar
document.addEventListener("DOMContentLoaded", () => {
    const hamburger = document.getElementById("hamburger");
    const dropdownContent = document.querySelector(".dropdown-content");

    hamburger.addEventListener("click", () => {
        dropdownContent.classList.toggle("visible");
    });
    document.addEventListener("click", (event) => {
        if (!dropdownContent.contains(event.target) && !hamburger.contains(event.target)) {
            dropdownContent.classList.remove("visible");
        }
    });
});


// Event listener for search
searchButton.addEventListener('click', (e)  => {
    e.preventDefault();
    searchValidate();
});