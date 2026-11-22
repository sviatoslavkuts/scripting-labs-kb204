# Лабораторна робота №3: FastAPI та SQLite (Варіант 14)

## 1. Предметна область
- **Тема**: Реєстр ризиків контейнерної конфігурації.
- **Категорії компонентів**: `image`, `runtime`, `secrets`.
- **Одиниця вимірювання**: `score` (оцінка ризику від 0 до 10 включно).
- **Поріг**: 6.0.
- **Назва запису**: Знахідка контейнерного аудиту.

## 2. Інструкція з запуску

1. **Встановлення залежностей** (виконувати з кореня репозиторію):
   ```bash
   pip install -r requirements.txt
   ```

2. **Ініціалізація та заповнення бази даних початковими даними**:
   ```bash
   python -m labs.lab03.seed
   ```

3. **Запуск FastAPI сервера розробки**:
   ```bash
   python -m uvicorn labs.lab03.main:app --reload --host 127.0.0.1 --port 8000
   ```

4. **Перевірка документації**:
   Відкрийте у браузері інтерактивний Swagger UI: `http://127.0.0.1:8000/docs`.

## 3. Приклади основних запитів (cURL)

- **Перевірка доступності (`/ping`)**:
  ```bash
  curl -i "http://127.0.0.1:8000/ping"
  ```

- **Отримання інформації про студента (`/student`)**:
  ```bash
  curl -i "http://127.0.0.1:8000/student"
  ```

- **Отримання категорій (`/categories`)**:
  ```bash
  curl -i "http://127.0.0.1:8000/categories"
  ```

- **Фільтрація записів (`/records`)**:
  ```bash
  curl -i "http://127.0.0.1:8000/records?category_id=1&status=new&limit=5&offset=0"
  ```

- **Створення нового запису (POST)**:
  ```bash
  curl -i -X POST "http://127.0.0.1:8000/records" \
    -H "Content-Type: application/json" \
    -d '{"code": "V14-TEST", "title": "Знахідка контейнерного аудиту тест", "category_id": 1, "value": 7.5, "status": "new"}'
  ```

- **Пакетне створення записів з транзакцією (`/records/bulk`)**:
  ```bash
  curl -i -X POST "http://127.0.0.1:8000/records/bulk" \
    -H "Content-Type: application/json" \
    -d '[{"code": "V14-BULK-1", "title": "Елемент 1", "category_id": 1, "value": 4.0, "status": "new"}, {"code": "V14-BULK-2", "title": "Елемент 2", "category_id": 2, "value": 8.5, "status": "in_progress"}]'
  ```