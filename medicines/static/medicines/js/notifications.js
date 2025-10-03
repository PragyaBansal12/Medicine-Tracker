async function initializeNotifications() {
    try {
        // Fetch VAPID public key from backend
        const response = await fetch('/get-vapid-public-key/');
        const data = await response.json();
        const VAPID_PUBLIC_KEY = data.vapid_public_key;
        
        console.log("VAPID Public Key loaded:", VAPID_PUBLIC_KEY);

        function urlBase64ToUint8Array(base64String) {
            const base64 = base64String
                .replace(/-/g, "+")
                .replace(/_/g, "/");
            const padding = "=".repeat((4 - base64.length % 4) % 4);
            const base64Padded = base64 + padding;
            const rawData = window.atob(base64Padded);
            return Uint8Array.from(rawData, c => c.charCodeAt(0));
        }

        if ("serviceWorker" in navigator && "PushManager" in window) {
            const reg = await navigator.serviceWorker.register("/static/medicines/js/service-worker.js");
            console.log("Service Worker registered", reg);

            const permission = await Notification.requestPermission();
            if (permission === "granted") {
                console.log("Notification permission granted.");

                const subscription = await reg.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
                });

                console.log("Subscription:", subscription);

                if (!subscription.getKey('p256dh') || !subscription.getKey('auth')) {
                    console.error("Subscription failed: Encryption keys are missing");
                    return;
                }

                console.log("Subscription keys look good, sending to server.");

                // Helper function to convert array buffer to base64
                function arrayBufferToBase64(buffer) {
                    const bytes = new Uint8Array(buffer);
                    let binary = '';
                    for (let i = 0; i < bytes.byteLength; i++) {
                        binary += String.fromCharCode(bytes[i]);
                    }
                    return btoa(binary);
                }

                // Send subscription to backend
                await fetch("/save-subscription/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                    body: JSON.stringify({
                        endpoint: subscription.endpoint,
                        p256dh: arrayBufferToBase64(subscription.getKey('p256dh')),
                        auth: arrayBufferToBase64(subscription.getKey('auth'))
                    }),
                });
                
                console.log("Subscription saved successfully");
            }
        }
    } catch (error) {
        console.error("Error initializing notifications:", error);
    }
}

// Helper to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        document.cookie.split(";").forEach(cookie => {
            const [key, value] = cookie.trim().split("=");
            if (key === name) cookieValue = decodeURIComponent(value);
        });
    }
    return cookieValue;
}

// Initialize notifications when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeNotifications();
});