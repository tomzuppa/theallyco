// user-dropdown.js

function toggleUserMenu() {
    const menu = document.getElementById('user-dropdown');
    menu.classList.toggle('hidden');
}

// Close the dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('user-dropdown');
    const avatar = document.querySelector('.user-avatar');
    if (!dropdown.contains(event.target) && !avatar.contains(event.target)) {
        dropdown.classList.add('hidden');
    }
});
