// 👁️ Toggle password visibility while pressing the eye icon
document.addEventListener('DOMContentLoaded', function() {
  const passwordInput = document.getElementById('id_password');
  const togglePassword = document.getElementById('togglePassword');

  if (passwordInput && togglePassword) {
    togglePassword.addEventListener('mousedown', function() {
      passwordInput.type = 'text'; // 👁️ Show password while pressing
    });

    togglePassword.addEventListener('mouseup', function() {
      passwordInput.type = 'password'; // 🔒 Hide password on release
    });

    togglePassword.addEventListener('mouseleave', function() {
      passwordInput.type = 'password'; // 🔒 Hide password if mouse leaves the icon
    });

    // 📱 Touch support (for mobile devices)
    togglePassword.addEventListener('touchstart', function(e) {
      e.preventDefault();
      passwordInput.type = 'text';
    });

    togglePassword.addEventListener('touchend', function() {
      passwordInput.type = 'password';
    });
  }
});
