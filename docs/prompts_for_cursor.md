# 🔥 Полезные промпты для разработки (Cursor / ChatGPT)

---

## 🧱 1. Структура проекта

### 📌 Архитектура проекта (бэкенд)
```
Act as a senior backend developer. I’m building a small web application with FastAPI and PostgreSQL. Propose a clean, modular folder structure and briefly explain each folder’s purpose.
```

### 📌 Архитектура проекта (фронтенд)
```
Suggest a scalable file/folder structure for a React + Tailwind CSS project with reusable components, pages, and hooks. Target: small business website with admin panel.
```

---

## ⚙️ 2. Генерация компонентов (UI / UX)

### 📌 Кнопка (React + Tailwind)
```
Generate a reusable React Button component using Tailwind CSS. Support: primary/secondary styles, disabled state, fullWidth option.
```

### 📌 Модалка
```
Create a responsive modal component in React with TailwindCSS. Include close button, ESC support, and backdrop.
```

### 📌 Форма с валидацией
```
Create a contact form with name/email/message fields and validation using React Hook Form. Send data to a FastAPI backend.
```

---

## 🔌 3. API и серверная логика

### 📌 FastAPI маршрут
```
Write a FastAPI POST route to receive a JSON payload with user data (name, email). Validate inputs using Pydantic and return a success message.
```

### 📌 CRUD (FastAPI + SQLAlchemy)
```
Create a SQLAlchemy model and CRUD routes for a Product entity (name, price, stock). Add typing and docstrings.
```

### 📌 Форма входа
```
Create a login route in FastAPI that accepts email and password, validates them against a user table, and returns a JWT token.
```

---

## 🗃️ 4. База данных и модели

### 📌 Модель User
```
Generate a SQLAlchemy model for a User with fields: id, name, email, hashed_password, created_at. Add constraints and typing.
```

### 📌 Генерация миграций
```
Explain how to use Alembic with SQLAlchemy for handling database migrations. Give a sample `alembic.ini` config and command sequence.
```

---

## 🛠️ 5. Утилиты и вспомогательные функции

### 📌 Парсинг строки запроса
```python
# TASK: Parse URL query parameters into a Python dict manually
# Example: "a=1&b=hello" → {"a": "1", "b": "hello"}
def parse_query(query: str) -> dict:
```

### 📌 Генерация уникального слага
```
Write a Python function that takes a string and returns a URL-friendly slug. Remove special characters, convert to lowercase.
```

---

## 🌐 6. Мультиязычность

### 📌 Подключение i18n (Jinja2 + Flask/FastAPI)
```
Explain how to implement multilingual support using gettext (.po/.mo) in a Jinja2-based site. Include how to switch languages via URL.
```

### 📌 Перевод строки в шаблоне
```jinja2
<h1>{{ _('Welcome to our website') }}</h1>
```

---

## 📉 7. Минимизация токенов в Cursor

### 📌 Формат запроса через комментарий
```js
// HELP ME: Add a click handler to this button that copies text from an input
<button id="copyBtn">Copy</button>
```

### 📌 Короткие локальные промпты
```
Just generate the JSX for a responsive navbar using TailwindCSS.
```

---

## 💡 8. Примеры UI-компонентов

### 📌 Карточка товара
```
Generate a responsive product card using TailwindCSS. Includes image, title, price, and “Buy” button. Adapt for mobile.
```

### 📌 Таблица с сортировкой
```
Create a table component in React that displays user data with sortable columns and pagination.
``` 