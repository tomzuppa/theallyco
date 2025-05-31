/**
 * 🧠 token_timer.js
 * Handles countdown for token expiration.
 * 🔁 Enables "Re-send Code" when token expires.
 * 🔐 Disables "Verify Code" once time runs out.
 */

// ⏳ Token expiry in seconds – passed from Django via data-seconds attribute
let countdownRaw = document.getElementById("token-timer")?.dataset.seconds;
let countdown = parseInt(countdownRaw, 10);

// Si `countdown` no es un número válido (ej. NaN), aplica valor por defecto (180)
if (isNaN(countdown)) {
  countdown = 180;
}

// ⬇️ DOM Elements
let timerDisplay;
let resendButton;
let verifyButton;
let timerInterval;

/**
 * ⏱️ Update the countdown display every second
 */
function updateTimer() {
  if (!timerDisplay) return;

  if (countdown <= 0) {
    clearInterval(timerInterval);

    // 🛑 Token expired message
    timerDisplay.innerText = "⛔ Token invalid or expired — please request a new code.";

    // ⚠️ Warning about attempt limits
    const warning = document.createElement("div");
    warning.className = "text-warning small mt-2 text-center";
    warning.innerText = "⚠️ After 3 failed attempts, your session will be blocked.";
    timerDisplay.parentNode.appendChild(warning);

    // 🔁 Enable Re-send
    if (resendButton) {
      resendButton.disabled = false;
      resendButton.classList.remove("btn-resend-disabled");
      resendButton.classList.add("btn-resend-active");
      resendButton.textContent = "Re-send Code";
    }

    // ❌ Disable Verify
    if (verifyButton) {
      verifyButton.disabled = true;
      verifyButton.classList.add("btn-verify-disabled");
    }

    return;
  }

  // ⏳ Show time remaining
  const minutes = Math.floor(countdown / 60);
  const seconds = countdown % 60;
  timerDisplay.innerText = `Token expires in ${minutes}:${seconds
    .toString()
    .padStart(2, "0")} seconds`;

  countdown--;
}

/**
 * 🚀 Initializes the token timer logic
 */
function initTokenTimer() {
  timerDisplay = document.getElementById("token-timer");
  resendButton = document.getElementById("resend-btn");
  verifyButton = document.getElementById("verify-btn");

  if (!timerDisplay) return;

  // 🔒 Disable "Re-send Code" at the start
  if (resendButton) {
    resendButton.disabled = true;
    resendButton.classList.add("btn-resend-disabled");
  }

  // ✅ Enable "Verify Code" at the start
  if (verifyButton) {
    verifyButton.disabled = false;
    verifyButton.classList.remove("btn-verify-disabled");
  }

  // ⏱️ Start countdown
  updateTimer();
  timerInterval = setInterval(updateTimer, 1000);
}

// 🚦 Launch on page load
window.addEventListener("DOMContentLoaded", initTokenTimer);
