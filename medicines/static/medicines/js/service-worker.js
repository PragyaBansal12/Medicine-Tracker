// service-worker.js - SIMPLIFIED VERSION
self.addEventListener('push', event => {
    let data = {};
    try {
        data = event.data.json();
    } catch (e) {
        data = {
            title: "💊 Medicine Reminder",
            body: event.data.text()
        };
    }

    const options = {
        body: data.body,
        // icon: "/static/images/pill.png",
        // badge: "/static/images/badge.png",
        data: data.data || {},
        // No actions - simple notification
        requireInteraction: false // Don't force user to interact
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', function (event) {
    event.notification.close();

    // ALWAYS open dashboard, regardless of how user interacts with notification
    event.waitUntil(
        clients.openWindow('/dashboard/')
    );
});