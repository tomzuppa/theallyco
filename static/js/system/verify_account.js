/**
 * 📄 verify_account.js
 * Handles:
 * - Countdown timer for activation token.
 * - Disabling/enabling re-send button.
 * - Basic UX feedback for 2FA flow.
 * 
 * Dependencies:
 * - Assumes existence of elements with IDs 'resendButton' and 'timer'.
 * 
 * Author: Michingón style
 */

// ⏱ Timer duration in seconds (for testing: 60s; in production: use 300)
let countdown = 60;
let resendButton;

/**
 * Updates the countdown timer and handles button state.
 */
function updateTimer() {
    let minutes = Math.floor(countdown / 60);
    let seconds = countdown % 60;
    let timerDisplay = document.getElementById("timer");

    timerDisplay.innerText = `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;

    if (countdown > 0) {
        countdown--;
        setTimeout(updateTimer, 1000);
    } else {
        timerDisplay.innerText = "You can now re-send the code.";
        if (resendButton) {
            resendButton.disabled = false;  // ✅ Enable resend button when countdown ends
        }
    }
}

/**
 * Initializes the timer and disables the button initially.
 */
function initVerifyAccountFlow() {
    resendButton = document.getElementById("resendButton");
    if (resendButton) {
        resendButton.disabled = true;  // 🔒 Disable resend button at start
    }
    updateTimer();
}

// 🚀 Initialize when page fully loaded
window.onload = initVerifyAccountFlow;
