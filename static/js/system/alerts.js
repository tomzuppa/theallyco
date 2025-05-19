
// 🌟 Auto-close Bootstrap alerts after 5 seconds
setTimeout(function() {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
      let alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
      alertInstance.close();
    });
  }, 10000); //seconds (calculation is = seconds * 1000 = 10,000 (example))
  