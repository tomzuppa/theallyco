/* ============================================================================
   🔒 AUTO LOGOUT SCRIPT
   ----------------------------------------------------------------------------
   This script automatically logs out the user after a fixed period of
   inactivity (default: 20 seconds) by redirecting them to the logout route.

   💡 This version is minimal — no warning banner is shown, and the user is
   simply logged out after inactivity.

   Dependencies: None
   Placement: Linked in base.html or any page where auto-logout is required
============================================================================ */

(function () {
    const inactivityLimit = 15 * 60 * 1000;  // ⏱️ 15 minutes of inactivity before logout
    let inactivityTimer;                // 🕒 Holds the timeout reference

    /**
     * 🔁 Resets the inactivity timer whenever user interacts
     */
    function resetTimer() {
        clearTimeout(inactivityTimer);  // 🚫 Clear previous timer if any
        inactivityTimer = setTimeout(() => {
            console.log("🚪 User inactive - triggering logout");
            window.location.href = "/users/logout/?auto=1";  // 🔐 Redirect to logout with flag
        }, inactivityLimit);
    }

    /**
     * 🖱️ Listens to common activity events to reset the timer
     */
    function attachListeners() {
        const events = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart', 'touchmove'];
        events.forEach(event => {
            document.addEventListener(event, resetTimer, { passive: true });
        });
        console.log("📡 Activity listeners attached:", events);
    }

    // 🚀 Start everything once the page loads
    window.addEventListener('load', () => {
        console.log("✅ auto_logout.js loaded — starting inactivity timer");
        resetTimer();
        attachListeners();
    });
})();
