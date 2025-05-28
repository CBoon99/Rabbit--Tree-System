const CACHE_NAME = 'rabbit-tree-system-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/index.html',
    '/js/app.js',
    '/js/auth.js',
    '/js/config.js',
    '/js/storage.js',
    '/js/tasks.js',
    '/js/ui.js',
    '/js/notifications.js',
    '/js/plugins.js',
    '/plugins/laundry-plugin-fixed.js',
    '/favicon.ico'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(ASSETS_TO_CACHE))
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }
                return fetch(event.request)
                    .then(response => {
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        const responseToCache = response.clone();
                        caches.open(CACHE_NAME)
                            .then(cache => cache.put(event.request, responseToCache));
                        return response;
                    })
                    .catch(() => new Response('Offline'));
            })
    );
}); 