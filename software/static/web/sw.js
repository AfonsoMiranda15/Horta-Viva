self.addEventListener('push', function(event) {
    let payload = event.data ? event.data.json() : { head: 'No Content', body: 'No Content', icon: '' };
    
    event.waitUntil(
        self.registration.showNotification(payload.head, {
            body: payload.body,
            icon: payload.icon || '/assets/logo_hortaviva.png'
        })
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(windowClients => {
            for (let i = 0; i < windowClients.length; i++) {
                let client = windowClients[i];
                if (client.url === '/' && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow('/minha-conta');
            }
        })
    );
});
