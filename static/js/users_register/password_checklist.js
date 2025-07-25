// ✅ Password Checklist Logic with Reappearance
// Hides checklist when all rules are valid, but brings it back if the password becomes invalid again

document.addEventListener('DOMContentLoaded', function () {
  const passwordInput = document.getElementById('id_password1');
  if (!passwordInput) return;

  const checklistContainer = document.getElementById('password-checklist'); // 🔎 Checklist container

  // 🎯 References to checklist items
  const checklist = {
    length: document.getElementById('check-length'),
    uppercase: document.getElementById('check-uppercase'),
    lowercase: document.getElementById('check-lowercase'),
    number: document.getElementById('check-number'),
    symbol: document.getElementById('check-symbol')
  };

  passwordInput.addEventListener('input', function () {
    const val = passwordInput.value;

    // 🟢 Evaluate rules
    const rules = {
      length: val.length >= 8,
      uppercase: /[A-Z]/.test(val),
      lowercase: /[a-z]/.test(val),
      number: /\d/.test(val),
      symbol: /[^A-Za-z0-9]/.test(val)
    };

    // 🔄 Update checklist items visually
    for (const [key, valid] of Object.entries(rules)) {
      checklist[key].classList.toggle('valid', valid);
    }

    const allValid = Object.values(rules).every(v => v);

    // 🧠 Smart visibility toggle
    if (allValid) {
      checklistContainer.style.display = 'none';
    } else {
      checklistContainer.style.display = 'block';
    }
  });
});
