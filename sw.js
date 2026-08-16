const CACHE_NAME = "hawo-weather-v1";

const APP_FILES = [
  "./",
  "./index.html",
  "./manifest.json"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(APP_FILES))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {

  const request = event.request;

  /*
   * API погоды всегда получаем свежим.
   */
  if (
    request.url.includes("api.open-meteo.com") ||
    request.url.includes("air-quality-api.open-meteo.com") ||
    request.url.includes("geocoding-api.open-meteo.com") ||
    request.url.includes("bigdatacloud.net")
  ) {
    event.respondWith(
      fetch(request)
        .catch(() => caches.match(request))
    );

    return;
  }

  /*
   * Для файлов приложения:
   * сначала сеть, затем кэш.
   */
  event.respondWith(
    fetch(request)
      .then(response => {

        if (
          response &&
          response.status === 200 &&
          request.method === "GET"
        ) {
          const copy = response.clone();

          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(request, copy);
            });
        }

        return response;
      })
      .catch(() => caches.match(request))
  );

});