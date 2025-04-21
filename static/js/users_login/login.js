// login.js — Placehol// login.js — Toggle Password Visibility
// Affects: <span class="toggle-password"> in login.html, line ~44

function togglePasswordVisibility() {
    const passwordInput = document.getElementById('id_password');
    const toggleIcon = document.querySelector('.toggle-password');
  
    if (!passwordInput || !toggleIcon) return;
  
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
  
    // Optional: Toggle eye icon or style (if you want dynamic icon)
    toggleIcon.textContent = type === 'password' ? '👁️' : '🙈';
  }
  der for future login interactions
// Affects: login.html
