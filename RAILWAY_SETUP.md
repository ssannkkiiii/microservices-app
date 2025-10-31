# 🚂 Налаштування на Railway

## 📋 Огляд сервісів

Ваш проєкт містить наступні сервіси:

1. **RabbitMQ** - `rabbitmq-production-ca4e.up.railway.app` (порт 5672)
2. **Backend (Python)** - `microservices-app-production.up.railway.app` (порт 8000)
3. **Go Worker** - `respectful-serenity-production.up.railway.app` (порт 8001)
4. **API Gateway** - `helpful-patience-production.up.railway.app` (порт 8080)
5. **UI** - `microservices-to-do-production.up.railway.app` (порт 8002)

## 🔧 Налаштування змінних оточення на Railway

### 1. RabbitMQ сервіс
**URL:** `rabbitmq-production-ca4e.up.railway.app:5672`

Цей сервіс не потребує змінних оточення. Просто переконайтеся, що він запущений та має volume для збереження даних.

**Отримайте Connection URL:**
- Перейдіть до налаштувань RabbitMQ сервісу на Railway
- Знайдіть **Connection URL** або **AMQP URL** в змінних оточення або в налаштуваннях
- Скопіюйте його (формат: `amqp://user:password@rabbitmq-production-ca4e.up.railway.app:5672`)
- АБО використовуйте internal domain: `amqp://guest:guest@rabbitmq.railway.internal:5672`

### 2. Backend сервіс (microservices-app)
**URL:** `microservices-app-production.up.railway.app:8000`

Додайте змінну оточення:

| Key | Value | Опис |
|-----|-------|------|
| `RABBIT_URL` | `amqp://guest:guest@rabbitmq.railway.internal:5672` | Internal Railway domain для RabbitMQ<br>АБО `amqp://user:pass@rabbitmq-production-ca4e.up.railway.app:5672` |

### 3. Go Worker сервіс (respectful-serenity)
**URL:** `respectful-serenity-production.up.railway.app:8001`

Додайте змінну оточення:

| Key | Value | Опис |
|-----|-------|------|
| `RABBIT_URL` | `amqp://guest:guest@rabbitmq.railway.internal:5672` | Той самий Connection URL з RabbitMQ<br>АБО `amqp://user:pass@rabbitmq-production-ca4e.up.railway.app:5672` |

### 4. API Gateway сервіс
**URL:** `helpful-patience-production.up.railway.app:8080`

Додайте змінну оточення:

| Key | Value | Опис |
|-----|-------|------|
| `BACKEND_WS_URL` | `ws://microservices-app.railway.internal:8000/ws` | Internal Railway domain для backend сервісу<br>**АЛЬТЕРНАТИВА:** Якщо internal domain не працює:<br>`wss://microservices-app-production.up.railway.app/ws` |

**Примітка:** Спочатку спробуйте internal domain. Якщо це не працює, використайте public domain з `wss://` (без порту, Railway автоматично проксує).

### 5. UI сервіс
**URL:** `microservices-to-do-production.up.railway.app:8002`

Цей сервіс не потребує змінних оточення. Код автоматично підключиться до API Gateway через `wss://helpful-patience-production.up.railway.app/ws`.

## 🌐 Як переглянути UI проект

### Відкрийте UI в браузері:

**Публічний URL:** `https://microservices-to-do-production.up.railway.app`

1. Просто відкрийте цей URL в браузері
2. UI автоматично підключиться до API Gateway (`helpful-patience-production.up.railway.app`)
3. Якщо підключення не працює, перевірте консоль браузера (F12)

### Альтернатива (якщо автоматичне підключення не працює):

Додайте параметр URL:
```
https://microservices-to-do-production.up.railway.app?gateway=helpful-patience-production.up.railway.app
```

## 🔍 Перевірка роботи

### 1. Перевірте логи сервісів:
- **Backend:** Має підключатися до RabbitMQ та показувати "Connected to RabbitMQ"
- **Go Worker:** Має підключатися до RabbitMQ та показувати "🐹 Go worker started, waiting for messages..."
- **API Gateway:** Має підключатися до Backend та показувати "✅ Gateway: Connected to backend"

### 2. Перевірте WebSocket підключення:
- Відкрийте UI в браузері
- Відкрийте консоль браузера (F12)
- Перевірте, чи є повідомлення про успішне підключення до API Gateway

### 3. Протестуйте переклад:
- Введіть текст для перекладу
- Виберіть мови
- Натисніть "Перекласти"
- Перевірте, чи з'являється результат

## 🐛 Troubleshooting

### Проблема: UI не підключається до API Gateway
**Рішення:**
- Перевірте, чи API Gateway запущений
- Перевірте публічний URL API Gateway
- Спробуйте використати URL параметр: `?gateway=your-api-gateway-url.railway.app`
- Перевірте логи API Gateway

### Проблема: "Failed to connect to RabbitMQ"
**Рішення:**
- Перевірте, чи `RABBIT_URL` правильно встановлено в Backend та Go Worker
- Перевірте, чи RabbitMQ сервіс запущений
- Переконайтеся, що використовуєте правильний Connection URL з RabbitMQ

### Проблема: Backend не підключається до Go Worker
**Рішення:**
- Перевірте, чи Go Worker запущений та підключений до RabbitMQ
- Перевірте, чи черга `translate_requests` існує в RabbitMQ
- Перевірте логи Go Worker

### Проблема: WebSocket connection failed
**Рішення:**
- Перевірте, чи використовується правильний протокол (wss:// для HTTPS, ws:// для HTTP)
- Перевірте CORS налаштування в API Gateway
- Перевірте, чи BACKEND_WS_URL правильно встановлено в API Gateway

## 📝 Приклад налаштувань для вашого проєкту

### RabbitMQ
```
Service URL: rabbitmq-production-ca4e.up.railway.app:5672
Connection URL (internal): amqp://guest:guest@rabbitmq.railway.internal:5672
Connection URL (public): amqp://user:pass@rabbitmq-production-ca4e.up.railway.app:5672
```

### Backend (microservices-app)
```
Service URL: microservices-app-production.up.railway.app:8000
Змінна оточення:
  RABBIT_URL=amqp://guest:guest@rabbitmq.railway.internal:5672
```

### Go Worker (respectful-serenity)
```
Service URL: respectful-serenity-production.up.railway.app:8001
Змінна оточення:
  RABBIT_URL=amqp://guest:guest@rabbitmq.railway.internal:5672
```

### API Gateway (helpful-patience)
```
Service URL: helpful-patience-production.up.railway.app:8080
Змінна оточення:
  BACKEND_WS_URL=ws://microservices-app.railway.internal:8000/ws
```

### UI (microservices-to-do)
```
Service URL: microservices-to-do-production.up.railway.app:8002
Публічний URL: https://microservices-to-do-production.up.railway.app
(Не потребує змінних оточення)
```

## ✅ Чек-лист перед запуском

- [ ] RabbitMQ запущений та має Connection URL
- [ ] Backend має змінну `RABBIT_URL`
- [ ] Go Worker має змінну `RABBIT_URL`
- [ ] API Gateway має змінну `BACKEND_WS_URL`
- [ ] Всі сервіси успішно деплояться (зелені чекмарки)
- [ ] UI доступний через публічний URL
- [ ] Логи показують успішні підключення

---

**Готово! 🎉** Тепер ваш мікросервісний додаток повинен працювати на Railway.

