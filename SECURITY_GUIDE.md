# 🔐 Руководство по безопасности Sianoro

## Обзор

Данное руководство описывает реализованные меры безопасности в платформе недвижимости Sianoro.

## 🛡️ Реализованные меры безопасности

### 1. JWT-аутентификация для админки

**Описание:** Система аутентификации на основе JWT-токенов для доступа к административной панели.

**Файлы:**
- `backend/utils/auth.py` - Основная логика аутентификации
- `backend/routers/auth.py` - API маршруты для аутентификации
- `backend/schemas/auth.py` - Pydantic-схемы
- `backend/static/js/admin-auth.js` - Клиентская логика

**Особенности:**
- Токены с ограниченным временем жизни (24 часа)
- Хеширование паролей с помощью bcrypt
- Автоматическая проверка токенов на всех админских страницах
- Безопасное хранение токенов в localStorage

**Использование:**
```bash
# Вход в админку
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}

# Проверка токена
GET /api/auth/verify
Authorization: Bearer <token>

# Получение информации о пользователе
GET /api/auth/me
Authorization: Bearer <token>
```

### 2. Валидация данных

**Описание:** Комплексная валидация всех входных данных с помощью Pydantic.

**Файлы:**
- `backend/utils/validation.py` - Утилиты валидации
- `backend/schemas/auth.py` - Схемы для форм

**Особенности:**
- Валидация email, телефонов, паролей
- Очистка строк от HTML-тегов
- Проверка размеров и типов файлов
- Защита от XSS-атак

**Примеры:**
```python
# Валидация формы контактов
class ContactForm(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str
    
    @validator('name')
    def validate_name(cls, v):
        v = InputValidator.sanitize_string(v)
        if len(v) < 2:
            raise ValueError('Имя должно содержать минимум 2 символа')
        return v
```

### 3. Middleware безопасности

**Описание:** Набор middleware для защиты приложения.

**Файлы:**
- `backend/middleware/security.py` - Все middleware безопасности

**Реализованные меры:**

#### CORS (Cross-Origin Resource Sharing)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://sianoro.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

#### Безопасные заголовки
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy` - защита от XSS

#### Rate Limiting
- Ограничение запросов: 60 в минуту
- Применяется к API и админским маршрутам
- Автоматическая блокировка при превышении лимита

#### Trusted Hosts
- Проверка заголовка Host
- Защита от DNS-спуфинга

### 4. Валидация файлов

**Описание:** Безопасная загрузка и обработка файлов.

**Поддерживаемые типы:**
- **Изображения:** JPEG, JPG, PNG, WebP, GIF
- **Документы:** PDF, DOC, DOCX, TXT

**Ограничения:**
- Максимальный размер изображения: 5MB
- Максимальный размер документа: 10MB
- Проверка MIME-типов

**Пример использования:**
```python
from backend.utils.validation import FileValidator

# Валидация изображения
FileValidator.validate_image(uploaded_file)

# Валидация документа
FileValidator.validate_document(uploaded_file)
```

## 🔧 Настройка безопасности

### 1. Переменные окружения

Создайте файл `.env` на основе `config.env.example`:

```bash
# JWT токены
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Администратор
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2e

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://sianoro.com
TRUSTED_HOSTS=localhost,sianoro.com

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
```

### 2. Генерация хеша пароля

```python
from backend.utils.auth import get_password_hash

# Генерация хеша для пароля
password_hash = get_password_hash("your_password")
print(password_hash)
```

### 3. Настройка CORS

Отредактируйте `ALLOWED_ORIGINS` в `.env`:

```bash
# Для разработки
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8002

# Для продакшена
ALLOWED_ORIGINS=https://sianoro.com,https://www.sianoro.com
```

## 🚨 Рекомендации по безопасности

### 1. Продакшен-настройки

**Обязательно измените:**
- `JWT_SECRET_KEY` - используйте криптографически стойкий ключ
- `ADMIN_PASSWORD_HASH` - сгенерируйте новый хеш для пароля
- `ALLOWED_ORIGINS` - укажите только ваши домены
- `TRUSTED_HOSTS` - укажите только ваши домены

### 2. HTTPS

**В продакшене обязательно используйте HTTPS:**
- Настройте SSL-сертификат
- Включите `https_only=True` в SessionMiddleware
- Используйте `secure=True` для cookies

### 3. Мониторинг

**Рекомендуется настроить:**
- Логирование попыток входа
- Мониторинг rate limiting
- Алерты при подозрительной активности

### 4. Регулярные обновления

**Периодически:**
- Обновляйте зависимости
- Меняйте JWT-ключи
- Проверяйте логи на подозрительную активность

## 🔍 Тестирование безопасности

### 1. Проверка аутентификации

```bash
# Попытка доступа без токена
curl http://localhost:8002/admin

# Вход в админку
curl -X POST http://localhost:8002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Использование токена
curl http://localhost:8002/api/auth/me \
  -H "Authorization: Bearer <token>"
```

### 2. Проверка CORS

```bash
# Проверка заголовков CORS
curl -H "Origin: http://malicious-site.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: X-Requested-With" \
  -X OPTIONS http://localhost:8002/api/auth/login
```

### 3. Проверка Rate Limiting

```bash
# Множественные запросы для проверки лимита
for i in {1..70}; do
  curl http://localhost:8002/api/auth/login
done
```

## 📚 Дополнительные ресурсы

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Security Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)

## 🆘 Поддержка

При обнаружении уязвимостей безопасности:
1. Немедленно сообщите разработчикам
2. Не публикуйте информацию публично
3. Предоставьте детальное описание проблемы

---

**Версия:** 1.0  
**Дата:** 2024  
**Автор:** Sianoro Development Team 