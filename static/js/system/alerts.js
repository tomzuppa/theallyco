
// 🌟 Auto-close Bootstrap alerts after 5 seconds
setTimeout(function() {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
      let alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
      alertInstance.close();
    });
  }, 5000); //seconds (s * 1000)
  