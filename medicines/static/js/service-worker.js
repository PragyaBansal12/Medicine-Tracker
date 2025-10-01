// Service Worker Lifecycle
self.addEventListener('install', event => {
    console.log('Service Worker installed');
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    console.log('Service Worker activated');
    return self.clients.claim();
});

// Event listener to receive messages from the main page
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'schedule-notifications') {
        const medications = event.data.medications;
        console.log('Received medications to schedule:', medications);
        scheduleNotifications(medications);
    }
});

// This function schedules the notifications using a timer
function scheduleNotifications(medications) {
    // Clear any previous schedules to prevent duplicates
    // In a real app, you might use a database for more complex scheduling.
    
    medications.forEach(med => {
        med.times.forEach(timeStr => {
            const [hour, minute] = timeStr.split(":").map(Number);
            const now = new Date();
            let notifTime = new Date();
            notifTime.setHours(hour, minute, 0, 0);

            // If the time has already passed today, schedule it for tomorrow
            if (notifTime < now) {
                notifTime.setDate(notifTime.getDate() + 1);
            }

            const delay = notifTime.getTime() - now.getTime();

            // Use setTimeout to trigger the notification
            setTimeout(() => {
                self.registration.showNotification(med.pill_name, {
                    body: "It's time to take your medicine!",
                    icon: '/static/images/pill.png',
                    tag: `medication-${med.id}-${timeStr}` // Use a unique tag to prevent duplicate notifications from stacking up
                });
            }, delay);
        });
    });
}