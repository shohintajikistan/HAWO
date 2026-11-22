# SHOHIN WEATHER 🇹🇯

Погодное PWA-приложение для Таджикистана.

## Возможности

- 🌤 Текущая погода
- 🕐 Почасовой прогноз
- 📅 Прогноз на 7 дней
- 💧 Влажность
- 💨 Ветер
- 🌡 Давление
- 👁 Видимость
- 🌫 Качество воздуха
- 📍 GPS
- 🔍 Поиск города
- 📱 PWA
- 🇹🇯 Только Таджикистан

## Технологии

- HTML
- CSS
- JavaScript
- WeatherAPI
- Cloudflare Workers
- GitHub Pages
- PWA

## Архитектура

SHOHIN WEATHER
↓
Cloudflare Worker
↓
WeatherAPI

API-ключ WeatherAPI хранится только
в Cloudflare Worker и не публикуется
в GitHub или приложении.

## Автор

SHOHIN


## SHOHIN AI Image Generator

В HAWO добавлен отдельный раздел генерации изображений по текстовому описанию.

- Интерфейс: `image-generator.html`
- Backend-шаблон для Hugging Face Space: `ai-backend/`
- Модель по умолчанию: `black-forest-labs/FLUX.1-schnell`
- Токен модели хранится только в Secrets backend, не в браузере и не в GitHub.

### Подключение генерации

1. Создайте Hugging Face Space с SDK Docker.
2. Скопируйте содержимое папки `ai-backend/` в корень Space.
3. В Settings → Variables and secrets добавьте Secret `HF_TOKEN` с разрешением Inference Providers.
4. После запуска скопируйте адрес Space (например, `https://имя-пользователя-hawo-ai.hf.space`).
5. Откройте SHOHIN AI в HAWO и вставьте адрес backend в поле API.

Важно: сам интерфейс уже находится в HAWO, но генерация начнёт работать только после развёртывания backend и добавления действующего токена. Запросы к провайдеру могут быть платными или ограничиваться доступными кредитами.
