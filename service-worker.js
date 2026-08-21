const CACHE_NAME = "shohin-weather-v1";

const APP_FILES = [
    "./",
    "./index.html",
    "./manifest.json",
    "./icon-192.png",
    "./icon-512.png"
];


/* =========================================
   УСТАНОВКА
   ========================================= */

self.addEventListener("install", event => {

    event.waitUntil(

        caches.open(CACHE_NAME)
            .then(cache => {

                return cache.addAll(APP_FILES);

            })

    );

    self.skipWaiting();

});


/* =========================================
   АКТИВАЦИЯ
   ========================================= */

self.addEventListener("activate", event => {

    event.waitUntil(

        caches.keys()
            .then(keys => {

                return Promise.all(

                    keys
                        .filter(key =>
                            key !== CACHE_NAME
                        )
                        .map(key =>
                            caches.delete(key)
                        )

                );

            })

    );

    self.clients.claim();

});


/* =========================================
   ЗАПРОСЫ
   ========================================= */

self.addEventListener("fetch", event => {

    const request =
        event.request;


    /*
       Weather API НЕ кэшируем здесь.

       Погода должна приходить
       через Cloudflare Worker.
    */

    if (
        request.url.includes("workers.dev") ||
        request.url.includes("weatherapi.com")
    ) {

        return;

    }


    /*
       Для файлов самого приложения:

       Сначала пытаемся получить
       свежий файл из сети.

       Если интернета нет —
       используем сохранённую копию.
    */

    event.respondWith(

        fetch(request)

            .then(response => {

                if (
                    response &&
                    response.status === 200 &&
                    request.method === "GET"
                ) {

                    const copy =
                        response.clone();

                    caches.open(CACHE_NAME)
                        .then(cache => {

                            cache.put(
                                request,
                                copy
                            );

                        });

                }

                return response;

            })

            .catch(() => {

                return caches.match(request);

            })

    );

});