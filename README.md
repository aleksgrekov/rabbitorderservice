# Order Processing System

## Описание
Упрощённая система обработки заказов, состоящая из нескольких микросервисов, взаимодействующих через брокер сообщений RabbitMQ.

## Структура системы
- **Order Service (FastAPI)** – принимает заказы через API и отправляет их в очередь RabbitMQ.
- **Worker Service (Python + aio_pika / kombu / pika)** – обрабатывает заказы из очереди и отправляет их в БД.
- **Notification Service** – слушает очередь с обработанными заказами и отправляет уведомления.

### Order Service (FastAPI)
- API-эндпоинт `POST /order` для приёма заказов.
- Отправляет заказ в очередь `orders_queue` в RabbitMQ.

### Worker Service (Python + aio_pika / kombu / pika)
- Слушает `orders_queue`.
- Обрабатывает заказы. (Добавляет в БД.)
- После обработки отправляет заказ в `notifications_queue`.

### Notification Service
- Слушает `notifications_queue`.
- Выводит в лог `"Заказ №X обработан и уведомление отправлено"`.

## Пример взаимодействия
1. Клиент отправляет `POST /order` с JSON:
    ```json
    {
      "user_id": 123,
      "items": ["apple", "banana"],
      "total": 10.5
    }
    ```
2. **Order Service** кладёт заказ в RabbitMQ (`orders_queue`).
3. **Worker Service** забирает заказ, обрабатывает его и кладёт в `notifications_queue`.
4. **Notification Service** получает сообщение и логирует: `"Заказ №X обработан и уведомление отправлено"`.

## API Order Service
### Создать заказ
- **Метод:** `POST /order`
- **Описание:** Принимает данные заказа, отправляет их в брокер сообщений и возвращает подтверждение.
- **Запрос:**
  ```json
  {
    "user_id": 123,
    "items": ["apple", "banana"],
    "total": 10.5
  }
  ```
- **Ответы:**
  - `201 Created` – заказ принят в обработку.
    ```json
    {
      "message": "Заказ принят в обработку",
      "order": {
        "user_id": 123,
        "items": ["apple", "banana"],
        "total": 10.5
      }
    }
    ```
  - `400 Bad Request` – не удалось отправить заказ в брокер.
  - `422 Unprocessable Entity` – ошибка валидации данных.

## Запуск через Docker
### Предварительные шаги
1. Создайте `.env` файл и укажите необходимые переменные.

### Запуск
1. Соберите и запустите сервисы:
   ```sh
   docker-compose up --build
   ```
2. Order Service будет доступен по адресу: `http://localhost:8000`.
