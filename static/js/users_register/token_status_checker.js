/**
 * @file Manages the UI state for the token verification step.
 * @path static/js/users_register/token_status_checker.js
 */
function initTokenStatusChecker(config) {
    // DOM Element Selection
    const codeTextarea = document.getElementById('verification_code');
    const verifyButton = document.getElementById('verify-code-button');
    const resendButton = document.getElementById('resend-code-button');
    const countdownTimerEl = document.getElementById('countdown-timer');

    // Application State
    let state = {
        canVerify: config.canVerify,
        canResend: config.canResend,
        isExpired: config.isExpired,
        timeLeft: config.initialCountdown,
    };

    let countdownInterval;

    // Central UI update function
    function updateUI() {
        if (codeTextarea) {
            codeTextarea.disabled = !state.canVerify;
        }
        if (verifyButton) {
            verifyButton.disabled = !state.canVerify;
        }
        if (resendButton) {
            resendButton.disabled = !state.canResend;
        }
    }

    // Countdown timer manager
    function startCountdown() {
        clearInterval(countdownInterval);

        if (state.timeLeft <= 0) {
            if (countdownTimerEl) countdownTimerEl.textContent = '0';
            // When expired on load, we still need to set the final button state
            updateUI();
            return;
        }
        
        countdownInterval = setInterval(() => {
            state.timeLeft--;
            if (countdownTimerEl) {
                countdownTimerEl.textContent = state.timeLeft;
            }

            if (state.timeLeft <= 0) {
                clearInterval(countdownInterval);
                state.isExpired = true;
                state.canVerify = false;
                
                // After timer expires, user should be able to resend
                state.canResend = true;

                updateUI();
            }
        }, 1000);
    }

    // Initial Script Execution
    updateUI();
    startCountdown();
}