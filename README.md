# 🌐 Microservices Translation App

Мікросервісна архітектура для перекладу текстів через WebSocket з використанням RabbitMQ.

## 🏗️ Архітектура

```
┌─────────┐      ┌──────────────┐      ┌──────────┐      ┌─────────────┐      ┌──────────┐
│   UI    │─────▶│ API Gateway  │─────▶│ Backend  │─────▶│  RabbitMQ  │◀─────│Go Worker │
│ (3000)  │      │    (8080)    │      │  (8000)  │      │   (5672)   │      │          │
└─────────┘      └──────────────┘      └──────────┘      └─────────────┘      └──────────┘
```

### Компоненти:

1. **UI** (Frontend) - Простий веб-інтерфейс на порту 3000
2. **API Gateway** - Точка входу, проксує запити до backend (порт 8080)
3. **Backend** (Python/FastAPI) - Обробляє WebSocket з'єднання, працює з RabbitMQ
4. **RabbitMQ** - Message Broker для асинхронної комунікації (порти 5672, 15672)
5. **Go Worker** - Сервіс перекладу на Go (обробляє чергу translate_requests)

## 🚀 Запуск

### Вимоги:
- Docker & Docker Compose
- Git

### Інструкції:

1. **Клонуйте репозиторій** (якщо потрібно)

2. **Запустіть всі сервіси:**
```bash
cd services
docker-compose up --build
```

3. **Відкрийте браузер:**
   - **Frontend UI**: http://localhost:3000
   - **RabbitMQ Management**: http://localhost:15672 (login: `guest` / password: `guest`)

## 📝 Використання

1. Відкрийте http://localhost:3000
2. Введіть текст для перекладу
3. Виберіть мови (source/target)
4. Натисніть "Перекласти"
5. Результат з'явиться в розділі "Результати перекладу"

## 🔍 Тестування

### Перевірка всіх сервісів:

```bash
# Перевірка статусу
docker-compose ps

# Логи всіх сервісів
docker-compose logs -f

# Логи конкретного сервісу
docker-compose logs -f api-gateway
docker-compose logs -f backend
docker-compose logs -f go-worker
```

### Health checks:

- UI: http://localhost:3000
- API Gateway: http://localhost:8080/health
- RabbitMQ Management: http://localhost:15672

## 🛠️ Технології

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **API Gateway**: FastAPI, WebSocket проксування
- **Backend**: FastAPI, aio-pika, WebSocket
- **Message Broker**: RabbitMQ
- **Worker**: Go (golang), amqp091-go
- **Containerization**: Docker, Docker Compose

## 📂 Структура проєкту

```
microservices-app/
├── api_gateway/          # API Gateway сервіс
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── ui/                   # Frontend
│   ├── index.html
│   └── Dockerfile
├── services/
│   ├── client/           # Backend (Python)
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── scr/
│   ├── translate/        # Go Worker
│   │   ├── app.go
│   │   └── Dockerfile
│   └── docker-compose.yml
└── README.md
```

## 🔄 Потік даних

1. Користувач відправляє текст через UI
2. UI підключається до API Gateway через WebSocket (ws://localhost:8080/ws)
3. API Gateway проксує запит до Backend (ws://backend:8000/ws)
4. Backend створює reply queue та відправляє запит у RabbitMQ чергу `translate_requests`
5. Go Worker отримує повідомлення, перекладає текст та відправляє відповідь у reply queue
6. Backend отримує відповідь та відправляє її через WebSocket
7. API Gateway проксує відповідь до UI
8. UI відображає результат користувачу

## 🛑 Зупинка

```bash
cd services
docker-compose down
```

Для повного видалення (зображення та volumes):
```bash
docker-compose down -v --rmi all
```

## 📊 Моніторинг

- **RabbitMQ Management UI**: http://localhost:15672
  - Переглянути черги
  - Моніторити повідомлення
  - Перевірити з'єднання

## 🐛 Troubleshooting

### WebSocket не підключається:
- Перевірте, чи запущені всі сервіси: `docker-compose ps`
- Перевірте логи: `docker-compose logs api-gateway backend`

### Переклад не відображається:
- Перевірте консоль браузера (F12)
- Перевірте логи backend та go-worker
- Переконайтеся, що RabbitMQ працює

### Помилки підключення:
- Перезапустіть сервіси: `docker-compose restart`
- Перевірте мережу Docker: `docker network ls`

## 📝 Примітки

- Backend більше не експортує порт 8000 напряму - доступ тільки через API Gateway
- API Gateway має CORS для роботи з UI
- Go Worker має retry логіку для підключення до RabbitMQ
- Всі сервіси автоматично перезапускаються при помилках
