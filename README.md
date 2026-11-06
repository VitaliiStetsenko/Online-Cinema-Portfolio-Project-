# Online Cinema API

Backend API для онлайн-кинотеатра. Проект реализован на FastAPI и предоставляет регистрацию пользователей, JWT-аутентификацию, каталог фильмов, поиск, избранное, оценки, комментарии и корзину покупок.

Интерактивная документация API доступна в Swagger без авторизации: `http://localhost:8000/docs`.

## Реализованные функции

### Авторизация и безопасность

- Регистрация пользователя по email с проверкой уникальности адреса.
- Активация учетной записи по токену, который действует 24 часа.
- Повторная отправка ссылки активации для неактивного пользователя.
- Авторизация по email и паролю.
- Выдача JWT-пары: `access_token` и `refresh_token`.
- Обновление access-токена по refresh-токену.
- Logout: refresh-токен удаляется из базы, поэтому повторно использовать его нельзя.
- Смена пароля с проверкой старого пароля.
- Восстановление пароля через email-токен.
- Уникальный `jti` в JWT, чтобы несколько входов не создавали одинаковые refresh-токены.
- Роли пользователей:
  - `user` - обычный пользователь;
  - `moderator` - управление каталогом;
  - `admin` - расширенная роль администратора.

### Профили пользователей

- Просмотр своего профиля.
- Создание профиля.
- Изменение имени, фамилии, пола, даты рождения и информации о пользователе.
- В модели предусмотрено поле для адреса аватара.
- Загрузка JPEG, PNG и WEBP-аватара до 5 MB в MinIO: `POST /api/users/me/avatar`.

### Каталог фильмов

- Создание, получение, изменение и удаление фильмов.
- Управление жанрами, актерами, режиссерами и возрастными сертификатами.
- Изменять каталог могут только пользователи с ролью `moderator` или `admin`.
- Нельзя удалить фильм, который находится в пользовательской корзине.
- Уникальность фильма по сочетанию `name + year + time`.
- У фильма поддерживаются:
  - UUID;
  - название;
  - год выпуска;
  - длительность;
  - IMDb-рейтинг и количество голосов;
  - Metascore, сборы, описание и цена;
  - жанры, актеры, режиссеры и возрастной сертификат.

### Поиск и просмотр каталога

- Пагинация: `page`, `page_size`.
- Поиск по названию, описанию, актеру и режиссеру: `query`.
- Фильтрация по жанру, диапазону лет и рейтингу IMDb.
- Сортировка по названию, году, IMDb, цене или числу голосов.
- Список жанров с количеством связанных фильмов.

### Избранное

- Добавление фильма в избранное.
- Защита от повторного добавления одного фильма.
- Просмотр избранного с пагинацией.
- Удаление фильма из избранного.

### Рейтинги и комментарии

- Оценка фильма по шкале от 1 до 10.
- Изменение своей оценки без создания дубликата.
- Средняя оценка фильма, количество оценок и оценка текущего пользователя.
- Создание, редактирование и удаление комментариев.
- Редактировать и удалять можно только собственные комментарии.
- Лайки и дизлайки комментариев.
- Лайки и дизлайки фильмов.
- Ответы на комментарии через `parent_comment_id`.
- Уведомления о лайках/дизлайках и ответах на комментарии.

### Корзина

- Одна корзина на одного пользователя.
- Добавление фильма в корзину.
- Защита от добавления одного фильма дважды.
- Просмотр состава корзины и общей стоимости.
- Удаление отдельного фильма.
- Полная очистка корзины.

### Фоновые задачи и сервисы

- Celery-задачи для отправки писем об активации и сбросе пароля.
- Celery Beat для очистки истекших activation, reset и refresh токенов.
- Redis как брокер сообщений Celery.
- Flower для мониторинга Celery.
- MinIO для объектного хранения, например для будущих аватаров.

## Технологии

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic Settings
- Python-JOSE и bcrypt
- Redis
- Celery и Celery Beat
- MinIO
- Docker и Docker Compose
- Poetry
- Pytest, pytest-asyncio и pytest-cov
- Black, Flake8, MyPy
- GitHub Actions

## Структура проекта

```text
.
├── app/
│   ├── api/           # FastAPI routes
│   ├── core/          # Конфигурация и JWT/пароли
│   ├── db/            # Подключение и сессии БД
│   ├── models/        # SQLAlchemy-модели
│   ├── schemas/       # Pydantic-схемы запросов и ответов
│   ├── services/      # Бизнес-логика
│   ├── tasks/         # Celery-задачи
│   └── main.py        # Точка входа FastAPI
├── alembic/           # Настройка миграций
├── tests/             # Unit и интеграционные тесты
├── .github/workflows/ # GitHub Actions CI
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Быстрый запуск через Docker

### Что требуется

- Docker Desktop с включенным Docker Compose.
- Git.

### Шаг 1. Клонировать репозиторий

```powershell
git clone https://github.com/VitaliiStetsenko/Online-Cinema-Portfolio-Project-.git
cd Online-Cinema-Portfolio-Project-
git checkout develop
```

### Шаг 2. Создать `.env`

В PowerShell:

```powershell
Copy-Item .env.example .env
```

Для Windows CMD:

```cmd
copy .env.example .env
```

Откройте `.env` и как минимум замените `SECRET_KEY` на длинную случайную строку. Для реальной отправки писем укажите корректные параметры SMTP.

Пример минимальных настроек для Docker:

```env
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/online_cinema
SECRET_KEY=change-this-to-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=avatars
MINIO_SECURE=false

APP_TITLE=Online Cinema
APP_VERSION=1.0.0
DEBUG=true
```

Для Gmail обычно нужен отдельный пароль приложения, а не пароль от самого аккаунта.

### Шаг 3. Запустить сервисы

```powershell
docker compose up --build
```

Чтобы запустить в фоне:

```powershell
docker compose up --build -d
```

### Шаг 4. Применить миграции

В отдельном терминале:

```powershell
docker compose exec app alembic upgrade head
```

### Сервисы после запуска

| Сервис | Адрес |
| --- | --- |
| FastAPI | `http://localhost:8001` |
| Swagger UI | `http://localhost:8001/docs` |
| Flower | `http://localhost:5555` |
| MinIO API | `http://localhost:9010` |
| MinIO Console | `http://localhost:9011` |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

### Остановка контейнеров

```powershell
docker compose down
```

Для удаления также данных PostgreSQL и MinIO:

```powershell
docker compose down -v
```

## Локальный запуск без контейнера FastAPI

Этот вариант запускает FastAPI на компьютере, а PostgreSQL, Redis и MinIO оставляет в Docker.

### Что требуется

- Python 3.11 или новее.
- Poetry.
- Docker Desktop.

Проверить версию Python:

```powershell
python --version
```

### Шаг 1. Установить Poetry

PowerShell:

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

Закройте и откройте терминал, затем проверьте:

```powershell
poetry --version
```

### Шаг 2. Установить зависимости

В корне проекта:

```powershell
poetry install
```

Команда установит production и development зависимости, включая Pytest, Black, Flake8 и MyPy.

### Шаг 3. Запустить внешние сервисы

```powershell
docker compose up -d db redis minio
```

### Шаг 4. Создать локальный `.env`

```powershell
Copy-Item .env.example .env
```

Для запуска приложения с компьютера, а не из Docker, замените hostname сервисов на `localhost`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/online_cinema
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
MINIO_ENDPOINT=localhost:9000
```

Остальные параметры возьмите из `.env.example`.

### Шаг 5. Применить миграции

```powershell
poetry run alembic upgrade head
```

### Шаг 6. Запустить API

```powershell
poetry run uvicorn app.main:app --reload
```

После запуска откройте `http://localhost:8000/docs`.

### Опционально: запустить Celery локально

В разных терминалах из корня проекта:

```powershell
poetry run celery -A app.tasks.celery_app worker --loglevel=info
```

```powershell
poetry run celery -A app.tasks.celery_app beat --loglevel=info
```

```powershell
poetry run celery -A app.tasks.celery_app flower --port=5555
```

## Тесты

Тесты используют отдельную SQLite in-memory базу. Для запуска тестов не нужны PostgreSQL, Redis, SMTP, MinIO или Docker.

### Запуск всех тестов

```powershell
poetry run pytest
```

### Запуск с покрытием

```powershell
poetry run pytest --cov=app --cov-report=term-missing
```

HTML-отчет покрытия:

```powershell
poetry run pytest --cov=app --cov-report=html
```

После выполнения откройте файл `htmlcov/index.html` в браузере.

### Запуск одного файла или теста

```powershell
poetry run pytest tests/test_auth.py
```

```powershell
poetry run pytest tests/test_movies.py::test_movie_crud_and_search
```

На момент последней проверки:

```text
17 passed
Coverage: 87%
```

## Проверка качества кода

Проверить форматирование:

```powershell
poetry run black --check app tests
```

Автоматически отформатировать код:

```powershell
poetry run black app tests
```

Запустить линтер:

```powershell
poetry run flake8 app tests --max-line-length=120 --exclude=__pycache__
```

Проверить типы:

```powershell
poetry run mypy app --ignore-missing-imports
```

## API

Все запросы к API, кроме главного health-check, начинаются с `/api`.

Для защищенных endpoint передавайте access token:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

### Авторизация: `/api/auth`

| Метод | Endpoint | Назначение |
| --- | --- | --- |
| POST | `/register` | Регистрация и отправка активации |
| POST | `/activate/{token}` | Активация учетной записи |
| POST | `/resend-activation` | Новая ссылка активации |
| POST | `/login` | Вход и получение JWT-пары |
| POST | `/refresh` | Обновление токенов |
| POST | `/logout` | Отзыв refresh token |
| POST | `/change-password` | Смена пароля авторизованного пользователя |
| POST | `/request-password-reset` | Запрос токена для сброса пароля |
| POST | `/reset-password` | Сброс пароля по токену |

Пример регистрации:

```powershell
curl.exe -X POST "http://localhost:8000/api/auth/register" `
  -H "Content-Type: application/json" `
  -d "{\"email\": \"user@example.com\", \"password\": \"SecurePass123\"}"
```

### Пользователь: `/api/users`

| Метод | Endpoint | Назначение |
| --- | --- | --- |
| GET | `/me` | Получить свой профиль |
| POST | `/me/profile` | Создать профиль |
| PUT | `/me/profile` | Изменить профиль |
| POST | `/me/avatar` | Загрузить аватар в MinIO |
| GET | `` | Список пользователей, только admin |
| PATCH | `/{user_id}` | Смена роли или ручная активация, только admin |

### Фильмы: `/api/movies`

| Метод | Endpoint | Назначение |
| --- | --- | --- |
| GET | `` | Список фильмов, поиск, фильтрация и сортировка |
| GET | `/{movie_id}` | Подробная информация о фильме |
| POST | `` | Создание фильма, роль moderator/admin |
| PUT | `/{movie_id}` | Изменение фильма, роль moderator/admin |
| DELETE | `/{movie_id}` | Удаление фильма, роль moderator/admin |

Параметры списка фильмов:

| Параметр | Пример | Описание |
| --- | --- | --- |
| `page` | `1` | Номер страницы |
| `page_size` | `20` | Размер страницы, от 1 до 100 |
| `query` | `matrix` | Поиск по названию, описанию, актеру, режиссеру |
| `genre_id` | `2` | Фильтр по жанру |
| `year_from` / `year_to` | `2000`, `2024` | Диапазон лет |
| `imdb_from` / `imdb_to` | `7.5`, `10` | Диапазон IMDb |
| `sort_by` | `imdb` | `name`, `year`, `imdb`, `price`, `votes` |
| `sort_order` | `desc` | `asc` или `desc` |

Пример:

```text
GET /api/movies?query=matrix&year_from=1990&imdb_from=7&sort_by=imdb&sort_order=desc
```

### Каталог: `/api/catalog`

| Endpoint | Методы | Назначение |
| --- | --- | --- |
| `/genres` | GET, POST, DELETE | Жанры |
| `/genres/with-counts` | GET | Жанры с числом фильмов |
| `/directors` | GET, POST, DELETE | Режиссеры |
| `/stars` | GET, POST, DELETE | Актеры |
| `/certifications` | GET, POST, DELETE | Возрастные сертификаты |

`POST` и `DELETE` для каталога требуют роль `moderator` или `admin`.

### Избранное: `/api/favorites`

| Метод | Endpoint | Назначение |
| --- | --- | --- |
| GET | `` | Список избранных фильмов |
| POST | `/{movie_id}` | Добавить фильм |
| DELETE | `/{movie_id}` | Удалить фильм |

Список избранного поддерживает параметры каталога: `query`, `genre_id`, `year_from`, `year_to`, `imdb_from`, `imdb_to`, `sort_by`, `sort_order`, `page`, `page_size`.

### Оценки и комментарии

| Метод | Endpoint | Назначение |
| --- | --- | --- |
| PUT | `/api/movies/{movie_id}/rating` | Поставить оценку `score` от 1 до 10 |
| GET | `/api/movies/{movie_id}/rating` | Получить средний рейтинг |
| POST | `/api/movies/{movie_id}/comments` | Создать комментарий |
| GET | `/api/movies/{movie_id}/comments` | Список комментариев |
| PUT | `/api/comments/{comment_id}` | Изменить собственный комментарий |
| DELETE | `/api/comments/{comment_id}` | Удалить собственный комментарий |
| PUT | `/api/comments/{comment_id}/reaction?is_like=true` | Лайк или дизлайк комментария |
| PUT | `/api/movies/{movie_id}/reaction?is_like=true` | Лайк или дизлайк фильма |
| GET | `/api/notifications` | Уведомления текущего пользователя |
| PATCH | `/api/notifications/{notification_id}/read` | Отметить уведомление прочитанным |

### Корзина: `/api/cart`

| Метод | Endpoint | Назначение |
| --- | --- | --- |
| GET | `` | Текущая корзина и общая стоимость |
| POST | `/{movie_id}` | Добавить фильм |
| DELETE | `/{movie_id}` | Удалить фильм |
| DELETE | `` | Очистить корзину |

## CI/CD

GitHub Actions запускается на каждый `push` и pull request для веток `develop` и `main`.

Pipeline выполняет:

```text
poetry install
black --check app tests
flake8 app tests
mypy app --ignore-missing-imports
pytest tests/ --cov=app
```

Файл pipeline: `.github/workflows/ci.yml`.

## Важные замечания

- Перед реальным использованием замените все пароли, `SECRET_KEY` и MinIO credentials из `.env.example`.
- Для отправки email необходимо настроить SMTP.
- Перед запуском в production измените `DEBUG=false`.
- Alembic настроен в проекте; перед использованием PostgreSQL примените миграции.
- Swagger и OpenAPI-схема доступны без авторизации по `/docs` и `/openapi.json`. Защищенные API-endpoint по-прежнему требуют JWT access token.

## Автор

Vitalii Stetsenko
