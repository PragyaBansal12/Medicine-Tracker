// service-worker.js
self.addEventListener('install', event => {
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    self.clients.claim();
});

self.addEventListener('push', event => {
    let notificationData;
    
    // parse JSON
    try {
        notificationData = event.data.json();
    } catch (e) {
        notificationData = {
            title: "Medicine Reminder",
            body: event.data.text()
        };
    }

    const options = {
        body: notificationData.body || notificationData,
        data: {
            url: '/' 
        }
    };

    event.waitUntil(
        self.registration.showNotification(
            notificationData.title || "Medicine Reminder", 
            options
        )
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    event.waitUntil(
        clients.openWindow(event.notification.data.url || '/')
    );
});