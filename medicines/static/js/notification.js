// Register Service Worker
if ('serviceWorker' in navigator && 'PushManager' in window) {
    navigator.serviceWorker.register('/static/js/service-worker.js')
    .then(reg => {
        console.log("Service Worker registered:", reg);

        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                console.log("Notification permission granted.");
            }
        });
    });
}