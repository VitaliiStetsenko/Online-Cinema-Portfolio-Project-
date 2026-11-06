# Online Cinema - Platform API

Платформа онлайн-кинотеатра с полным функционалом управления пользователями, каталогом фильмов, корзиной покупок и системой рейтингов.

## Технологии

- **FastAPI** - современный веб-фреймворк для создания API
- **PostgreSQL** - основная база данных
- **SQLAlchemy** - ORM для работы с БД
- **Alembic** - миграции базы данных
- **Redis** - кеширование и брокер сообщений
- **Celery** - асинхронные задачи (отправка email, очистка токенов)
- **MinIO** - хранилище для файлов (аватары пользователей)
- **Docker & Docker Compose** - контейнеризация
- **Poetry** - управление зависимостями
- **Pytest** - тестирование
- **GitHub Actions** - CI/CD

## Функциональность

### 1. Авторизация и аутентификация
- Регистрация пользователей с проверкой email
- Активация аккаунта через email (токен действителен 24 часа)
- Повторная отправка ссылки активации
- Вход с JWT токенами (access + refresh)
- Обновление access токена через refresh токен
- Logout с отзывом refresh токена
- Смена пароля (с проверкой старого пароля)
- Восстановление пароля через email
- Три роли пользователей: User, Moderator, Admin

### 2. Профили пользователей
- Просмотр своего профиля
- Создание и редактирование профиля (имя, фамилия, пол, дата рождения, информация)
- Загрузка аватара (поддержка MinIO)

### 3. Каталог фильмов
- CRUD операции для фильмов (только модераторы/админы)
- CRUD для жанров, актеров, режиссеров, возрастных рейтингов
- Защита от удаления фильма, находящегося в корзинах пользователей
- Уникальность фильма по комбинации (название, год, длительность)

### 4. Просмотр и поиск
- Пагинация каталога
- Полнотекстовый поиск по названию, описанию, актерам, режиссерам
- Фильтрация по жанру, году выпуска, рейтингу IMDb
- Сортировка по названию, году, IMDb, цене, количеству голосов
- Список жанров с количеством фильмов

### 5. Избранное
- Добавление фильмов в избранное
- Просмотр списка избранного с пагинацией
- Удаление из избранного

### 6. Рейтинги и комментарии
- Оценка фильмов по 10-балльной шкале
- Средний рейтинг и количество оценок
- Создание, редактирование и удаление комментариев
- Лайки и дизлайки к комментариям
- Подсчет лайков/дизлайков

### 7. Корзина покупок
- Добавление фильмов в корзину
- Защита от дублирования фильмов
- Удаление отдельных фильмов
- Полная очистка корзины
- Расчет общей стоимости

### 8. Автоматизация
- Celery задачи для отправки email (активация, восстановление пароля)
- Celery Beat для периодической очистки истекших токенов
- Flower для мониторинга Celery

## Установка и запуск

### Требования
- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)
- Poetry (для управления зависимостями)

### Быстрый старт с Docker

1. Клонируйте репозиторий:
```bash
git clone https://github.com/VitaliiStetsenko/Online-Cinema-Portfolio-Project-.git
cd Online-Cinema-Portfolio-Project-
```

2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

3. Отредактируйте `.env` и укажите свои настройки (особенно SMTP для email):
```env
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/online_cinema
SECRET_KEY=your-secret-key-here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

4. Запустите все сервисы:
```bash
docker-compose up -d
```

5. Примените миграции базы данных:
```bash
docker-compose exec app alembic upgrade head
```

6. Доступ к сервисам:
- **API**: http://localhost:8000
- **Swagger документация**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Flower (Celery monitoring)**: http://localhost:5555
- **MinIO Console**: http://localhost:9001

### Локальная разработка

1. Установите Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Установите зависимости:
```bash
poetry install
```

3. Запустите PostgreSQL, Redis и MinIO через Docker:
```bash
docker-compose up -d db redis minio
```

4. Активируйте виртуальное окружение и запустите приложение:
```bash
poetry shell
uvicorn app.main:app --reload
```

## API Endpoints

### Авторизация (`/api/auth`)
- `POST /auth/register` - Регистрация нового пользователя
- `POST /auth/activate/{token}` - Активация аккаунта
- `POST /auth/resend-activation` - Повторная отправка активации
- `POST /auth/login` - Вход в систему
- `POST /auth/refresh` - Обновление access токена
- `POST /auth/logout` - Выход из системы
- `POST /auth/change-password` - Смена пароля
- `POST /auth/request-password-reset` - Запрос сброса пароля
- `POST /auth/reset-password` - Сброс пароля

### Пользователи (`/api/users`)
- `GET /users/me` - Получить свой профиль
- `POST /users/me/profile` - Создать профиль
- `PUT /users/me/profile` - Обновить профиль

### Каталог (`/api/catalog`)
- `GET /catalog/genres` - Список жанров
- `POST /catalog/genres` - Создать жанр (модератор)
- `DELETE /catalog/genres/{id}` - Удалить жанр (модератор)
- `GET /catalog/directors` - Список режиссеров
- `POST /catalog/directors` - Создать режиссера (модератор)
- `DELETE /catalog/directors/{id}` - Удалить режиссера (модератор)
- `GET /catalog/stars` - Список актеров
- `POST /catalog/stars` - Создать актера (модератор)
- `DELETE /catalog/stars/{id}` - Удалить актера (модератор)
- `GET /catalog/certifications` - Список возрастных рейтингов
- `POST /catalog/certifications` - Создать рейтинг (модератор)
- `DELETE /catalog/certifications/{id}` - Удалить рейтинг (модератор)
- `GET /catalog/genres/with-counts` - Жанры с количеством фильмов

### Фильмы (`/api/movies`)
- `GET /movies` - Список фильмов с фильтрацией и поиском
- `GET /movies/{id}` - Детали фильма
- `POST /movies` - Создать фильм (модератор)
- `PUT /movies/{id}` - Обновить фильм (модератор)
- `DELETE /movies/{id}` - Удалить фильм (модератор)

### Избранное (`/api/favorites`)
- `GET /favorites` - Список избранных фильмов
- `POST /favorites/{movie_id}` - Добавить в избранное
- `DELETE /favorites/{movie_id}` - Удалить из избранного

### Рейтинги и комментарии (`/api`)
- `PUT /movies/{movie_id}/rating` - Поставить оценку фильму
- `GET /movies/{movie_id}/rating` - Получить рейтинг фильма
- `POST /movies/{movie_id}/comments` - Написать комментарий
- `GET /movies/{movie_id}/comments` - Список комментариев
- `PUT /comments/{id}` - Обновить комментарий
- `DELETE /comments/{id}` - Удалить комментарий
- `PUT /comments/{id}/reaction` - Поставить лайк/дизлайк

### Корзина (`/api/cart`)
- `GET /cart` - Просмотр корзины
- `POST /cart/{movie_id}` - Добавить фильм в корзину
- `DELETE /cart/{movie_id}` - Удалить фильм из корзины
- `DELETE /cart` - Очистить корзину

## Примеры использования

### Регистрация и вход
```bash
# Регистрация
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123"}'

# После активации - вход
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123"}'
```

### Работа с фильмами
```bash
# Получить список фильмов
curl http://localhost:8000/api/movies?page=1&page_size=20

# Поиск фильмов
curl "http://localhost:8000/api/movies?query=inception&year_from=2010"

# Фильтрация по жанру
curl "http://localhost:8000/api/movies?genre_id=1&sort_by=imdb&sort_order=desc"
```

### Работа с корзиной
```bash
# Добавить фильм в корзину
curl -X POST http://localhost:8000/api/cart/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Просмотр корзины
curl http://localhost:8000/api/cart \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Тестирование

Запуск тестов:
```bash
poetry run pytest
```

С покрытием кода:
```bash
poetry run pytest --cov=app --cov-report=html
```

Проверка кода:
```bash
# Форматирование
poetry run black app tests

# Линтинг
poetry run flake8 app tests

# Проверка типов
poetry run mypy app
```

## CI/CD

Проект использует GitHub Actions для автоматической проверки кода при каждом push:
- Форматирование (Black)
- Линтинг (Flake8)
- Проверка типов (MyPy)
- Запуск тестов (Pytest)
- Отчет о покрытии кода

## Структура проекта

```
.
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Конфигурация и безопасность
│   ├── db/               # Настройка БД
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Бизнес-логика
│   ├── tasks/            # Celery задачи
│   └── main.py           # Главный файл приложения
├── tests/                # Тесты
├── alembic/              # Миграции БД
├── .github/workflows/    # GitHub Actions
├── docker-compose.yml    # Docker конфигурация
├── Dockerfile            # Docker образ приложения
├── pyproject.toml        # Poetry зависимости
└── README.md             # Документация
```

## Модели базы данных

### Пользователи
- `UserGroup` - Группы пользователей (User, Moderator, Admin)
- `User` - Пользователи
- `UserProfile` - Профили пользователей
- `ActivationToken` - Токены активации
- `PasswordResetToken` - Токены сброса пароля
- `RefreshToken` - Refresh токены

### Фильмы
- `Movie` - Фильмы
- `Genre` - Жанры
- `Star` - Актеры
- `Director` - Режиссеры
- `Certification` - Возрастные рейтинги

### Взаимодействие
- `Favorite` - Избранные фильмы
- `Rating` - Оценки фильмов
- `Comment` - Комментарии
- `CommentLike` - Лайки/дизлайки комментариев

### Корзина
- `Cart` - Корзина пользователя
- `CartItem` - Позиции в корзине

## Лицензия

MIT License

## Автор

Vitalii Stetsenko
