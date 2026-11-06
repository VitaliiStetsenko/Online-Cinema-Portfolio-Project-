# Online Cinema API

Backend API для онлайн-кинотеатра на FastAPI. Проект реализует учетные записи и роли, каталог фильмов, профиль с аватаром, избранное, оценки, комментарии, реакции, уведомления и корзину.

## Содержание

- [Возможности](#возможности)
- [Технологии](#технологии)
- [Документация API](#документация-api)
- [Быстрый запуск в Docker](#быстрый-запуск-в-docker)
- [Локальный запуск](#локальный-запуск)
- [Авторизация](#авторизация)
- [API](#api)
- [Тесты и качество](#тесты-и-качество)
- [CI](#ci)

## Возможности

### Учетные записи и доступ

- Регистрация по уникальному email с проверкой сложности пароля.
- Активация учетной записи по одноразовому токену, действующему 24 часа.
- Повторная отправка activation-токена для неактивного пользователя.
- Вход по email и паролю с выдачей пары JWT: access и refresh.
- Access token действует ограниченное время, refresh token хранится в базе и используется только для обновления access token.
- Logout отзывает refresh token, поэтому его нельзя использовать повторно.
- Смена пароля с проверкой старого пароля и сброс пароля по одноразовому токену.
- Три роли: `user`, `moderator`, `admin`.
- Администратор может просматривать пользователей, менять роль и вручную активировать аккаунт.

### Профиль и аватар

- Создание, просмотр и изменение своего профиля.
- Поля профиля: имя, фамилия, пол, дата рождения, информация о себе и адрес аватара.
- Загрузка JPEG, PNG и WEBP-аватаров размером до 5 MB в MinIO.

### Каталог фильмов

- Публичный список и подробная информация о фильмах.
- Поиск по названию, описанию, актерам и режиссерам.
- Фильтры по жанру, диапазону годов выпуска и IMDb-рейтингу.
- Сортировка по названию, году, IMDb, цене или числу голосов.
- Пагинация списка.
- CRUD фильмов, жанров, режиссеров, актеров и возрастных сертификатов для moderator/admin.
- Защита от удаления фильма, который находится в чьей-либо корзине.
- Список жанров с количеством связанных фильмов.

### Взаимодействие с фильмами

- Избранное с поиском, фильтрацией, сортировкой и пагинацией.
- Оценки фильмов от 1 до 10 с возможностью изменить свою оценку.
- Средняя оценка, количество оценок и оценка текущего пользователя.
- Комментарии, редактирование и удаление собственных комментариев, ответы на комментарии.
- Лайки и дизлайки комментариев и фильмов.
- Внутренние уведомления об ответах и реакциях на комментарии.

### Корзина и фоновые задачи

- Одна корзина на пользователя, запрет повторного добавления фильма.
- Просмотр состава корзины и общей стоимости, удаление позиции и полная очистка.
- Celery-задачи для писем об активации и сбросе пароля.
- Celery Beat очищает истекшие activation, password-reset и refresh токены.
- Redis используется как брокер Celery, Flower предоставляет мониторинг задач.

## Технологии

- Python 3.11+, FastAPI и Pydantic Settings.
- PostgreSQL, SQLAlchemy Async и Alembic.
- JWT через Python-JOSE, хеширование паролей через bcrypt.
- Redis, Celery, Celery Beat и Flower.
- MinIO для S3-совместимого хранения аватаров.
- Docker, Docker Compose и Poetry.
- Pytest, pytest-asyncio, pytest-cov, Black, Flake8, MyPy и GitHub Actions.

## Документация API

Swagger UI и OpenAPI-схема открыты без авторизации. Защищенные методы в Swagger требуют access token через кнопку **Authorize**.

| Режим запуска | Swagger UI | OpenAPI JSON |
| --- | --- | --- |
| Docker Compose | `http://localhost:8001/docs` | `http://localhost:8001/openapi.json` |
| Локальный Uvicorn | `http://localhost:8000/docs` | `http://localhost:8000/openapi.json` |

Swagger содержит схемы запросов, ответов, обязательные параметры и коды ответов для всех endpoint. Разделы ниже служат краткой картой API и описанием кастомных действий.

## Быстрый запуск в Docker

### Требования

- Docker Desktop с Docker Compose.
- Git.

### 1. Клонирование и конфигурация

```powershell
git clone https://github.com/VitaliiStetsenko/Online-Cinema-Portfolio-Project-.git
cd Online-Cinema-Portfolio-Project-
git checkout develop
Copy-Item .env.example .env
```

В `.env` обязательно замените `SECRET_KEY`. Для отправки реальных email укажите рабочие SMTP-данные.

Основные настройки:

```env
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/online_cinema
SECRET_KEY=replace-with-a-long-random-secret
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
```

### 2. Запуск и миграции

```powershell
docker compose up --build -d
docker compose exec app alembic upgrade head
```

### Сервисы

| Сервис | Адрес |
| --- | --- |
| API и Swagger | `http://localhost:8001/docs` |
| Flower | `http://localhost:5555` |
| MinIO API | `http://localhost:9010` |
| MinIO Console | `http://localhost:9011` |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

Остановить сервисы:

```powershell
docker compose down
```

Удалить также тома PostgreSQL и MinIO:

```powershell
docker compose down -v
```

## Локальный запуск

Этот режим запускает FastAPI на компьютере, а PostgreSQL, Redis и MinIO оставляет в Docker.

```powershell
poetry install
docker compose up -d db redis minio
Copy-Item .env.example .env
```

Для локального `.env` замените имена Docker-сервисов:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/online_cinema
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
MINIO_ENDPOINT=localhost:9010
```

Примените миграции и запустите API:

```powershell
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

Локальный Swagger: `http://localhost:8000/docs`.

При необходимости отдельно запустите Celery:

```powershell
poetry run celery -A app.tasks.celery_app worker --loglevel=info
poetry run celery -A app.tasks.celery_app beat --loglevel=info
poetry run celery -A app.tasks.celery_app flower --port=5555
```

## Авторизация

Большинство действий пользователя требуют заголовок:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

Получите токены через `POST /api/auth/login`. В Swagger нажмите **Authorize**, вставьте только значение access token и подтвердите. Refresh token предназначен исключительно для `POST /api/auth/refresh` и не дает доступа к защищенным endpoint.

Пароль должен быть длиной от 8 до 100 символов и содержать строчную и заглавную буквы, цифру и специальный символ.

## API

Все перечисленные пути начинаются с `/api`, если не указано иное. Полные схемы JSON находятся в Swagger.

### Служебные маршруты

| Метод | Путь | Доступ | Действие |
| --- | --- | --- | --- |
| GET | `/` | public | Health check: возвращает статус API. |
| GET | `/docs` | public | Swagger UI. |
| GET | `/openapi.json` | public | OpenAPI-схема. |

### Аутентификация: `/auth`

| Метод | Путь | Параметры/тело | Действие |
| --- | --- | --- | --- |
| POST | `/register` | `email`, `password` | Создает неактивного пользователя и ставит отправку activation-токена в очередь. |
| POST | `/activate/{token}` | path `token` | Активирует аккаунт по действующему токену. |
| POST | `/resend-activation` | `email` | Выпускает новый activation-токен для неактивного пользователя. |
| POST | `/login` | `email`, `password` | Возвращает `access_token`, `refresh_token`, `token_type`. |
| POST | `/refresh` | `refresh_token` | Создает новый access token. |
| POST | `/logout` | `refresh_token` | Удаляет refresh token из базы. |
| POST | `/change-password` | `old_password`, `new_password` | Меняет пароль текущего пользователя. Требует access token. |
| POST | `/request-password-reset` | `email` | Создает и отправляет reset-токен для активного пользователя. |
| POST | `/reset-password` | `token`, `new_password` | Устанавливает новый пароль по действующему reset-токену. |

Пример регистрации для Docker:

```powershell
curl.exe -X POST "http://localhost:8001/api/auth/register" `
  -H "Content-Type: application/json" `
  -d "{\"email\": \"user@example.com\", \"password\": \"SecurePass123!\"}"
```

### Пользователи: `/users`

| Метод | Путь | Доступ | Действие |
| --- | --- | --- | --- |
| GET | `/me` | active user | Возвращает аккаунт и профиль текущего пользователя. |
| POST | `/me/profile` | active user | Создает профиль. Тело: `first_name`, `last_name`, `gender`, `date_of_birth`, `info`. |
| PUT | `/me/profile` | active user | Обновляет профиль; создает его автоматически, если профиля нет. |
| POST | `/me/avatar` | active user | Загружает multipart-поле `avatar` в JPEG, PNG или WEBP до 5 MB. |
| GET | `` | admin | Возвращает список учетных записей. |
| PATCH | `/{user_id}` | admin | Меняет `group` (`user`, `moderator`, `admin`) и/или `is_active`. |

### Фильмы: `/movies`

| Метод | Путь | Доступ | Действие |
| --- | --- | --- | --- |
| GET | `` | public | Возвращает постраничный каталог. |
| GET | `/{movie_id}` | public | Возвращает подробную карточку фильма. |
| POST | `` | moderator/admin | Создает фильм. |
| PUT | `/{movie_id}` | moderator/admin | Обновляет поля фильма и его связи. |
| DELETE | `/{movie_id}` | moderator/admin | Удаляет фильм, если его нет в корзинах. |

Параметры `GET /movies`:

| Параметр | Значение | Назначение |
| --- | --- | --- |
| `page`, `page_size` | `1`, `1..100` | Страница и число результатов. |
| `query` | строка | Поиск по названию, описанию, актеру и режиссеру. |
| `genre_id` | integer | Фильтр по жанру. |
| `year_from`, `year_to` | `1888..2100` | Диапазон года выпуска. |
| `imdb_from`, `imdb_to` | `0..10` | Диапазон IMDb. |
| `sort_by` | `name`, `year`, `imdb`, `price`, `votes` | Поле сортировки. |
| `sort_order` | `asc`, `desc` | Направление сортировки. |

Тело создания фильма содержит `name`, `year`, `time`, `imdb`, `votes`, `description`, `price`, `certification_id` и необязательные массивы `genre_ids`, `director_ids`, `star_ids`. Дополнительно доступны `meta_score` и `gross`.

### Управление справочниками: `/catalog`

| Ресурс | Public | Moderator/admin |
| --- | --- | --- |
| `/genres` | `GET` | `POST`, `PUT /{entity_id}`, `DELETE /{entity_id}` |
| `/directors` | `GET` | `POST`, `PUT /{entity_id}`, `DELETE /{entity_id}` |
| `/stars` | `GET` | `POST`, `PUT /{entity_id}`, `DELETE /{entity_id}` |
| `/certifications` | `GET` | `POST`, `PUT /{entity_id}`, `DELETE /{entity_id}` |
| `/genres/with-counts` | `GET` | - |

Создание использует тело `{ "name": "..." }`. Обновление принимает такое же тело. Endpoint `GET /genres/with-counts` возвращает для каждого жанра `id`, `name` и `movie_count`.

### Избранное: `/favorites`

| Метод | Путь | Действие |
| --- | --- | --- |
| GET | `` | Возвращает постраничный список избранных фильмов текущего пользователя. |
| POST | `/{movie_id}` | Добавляет фильм в избранное. Повторное добавление отклоняется. |
| DELETE | `/{movie_id}` | Удаляет фильм из избранного. |

`GET /favorites` поддерживает параметры каталога: `page`, `page_size`, `query`, `genre_id`, `year_from`, `year_to`, `imdb_from`, `imdb_to`, `sort_by`, `sort_order`. Для `sort_by` также доступно `added_at`.

### Оценки, комментарии и уведомления

| Метод | Путь | Действие |
| --- | --- | --- |
| PUT | `/movies/{movie_id}/rating` | Создает или изменяет свою оценку. Тело: `{ "score": 1..10 }`. |
| GET | `/movies/{movie_id}/rating` | Возвращает средний балл, количество оценок и оценку текущего пользователя. |
| POST | `/movies/{movie_id}/comments` | Создает комментарий. Тело: `text`, необязательный `parent_comment_id`. |
| GET | `/movies/{movie_id}/comments` | Возвращает комментарии фильма с количеством реакций. |
| PUT | `/comments/{comment_id}` | Изменяет собственный комментарий. Тело: `text`. |
| DELETE | `/comments/{comment_id}` | Удаляет собственный комментарий. |
| PUT | `/comments/{comment_id}/reaction?is_like=true` | Ставит или изменяет лайк/дизлайк комментария. |
| PUT | `/movies/{movie_id}/reaction?is_like=true` | Ставит или изменяет лайк/дизлайк фильма. |
| GET | `/notifications` | Возвращает уведомления текущего пользователя. |
| PATCH | `/notifications/{notification_id}/read` | Помечает уведомление прочитанным. |

Все методы этого раздела требуют активного пользователя.

### Корзина: `/cart`

| Метод | Путь | Действие |
| --- | --- | --- |
| GET | `` | Возвращает текущую корзину, позиции и `total_price`; при первом вызове создает пустую корзину. |
| POST | `/{movie_id}` | Добавляет фильм в корзину. Повторное добавление отклоняется. |
| DELETE | `/{movie_id}` | Удаляет указанную позицию. |
| DELETE | `` | Очищает корзину. |

Все методы корзины требуют активного пользователя.

## Тесты и качество

Тесты используют отдельную SQLite in-memory базу. Для запуска не нужны Docker, PostgreSQL, Redis, SMTP или MinIO: внешние вызовы изолируются в тестах.

```powershell
# Все тесты
poetry run pytest tests/

# Покрытие кода
poetry run pytest tests/ --cov=app --cov-report=term-missing

# HTML-отчет покрытия
poetry run pytest tests/ --cov=app --cov-report=html

# Форматирование, линтер и типы
poetry run black --check app tests
poetry run flake8 app tests --max-line-length=120 --exclude=__pycache__
poetry run mypy app --ignore-missing-imports
```

Последняя локальная проверка: **22 passed**, общее line coverage **87%**.

## CI

GitHub Actions запускается для `push` и pull request в ветки `develop` и `main`. Pipeline устанавливает зависимости через Poetry, выполняет Black, Flake8, MyPy, Pytest с coverage и публикует `coverage.xml` в Codecov. Конфигурация: `.github/workflows/ci.yml`.

## Важные замечания

- Перед реальным использованием смените значения `SECRET_KEY`, SMTP-пароль и MinIO credentials из `.env.example`.
- Docker Compose настроен для разработки: исходный код монтируется в контейнер, а Uvicorn работает с `--reload`.
- После первого Docker-запуска примените миграции командой `docker compose exec app alembic upgrade head`.
- Письма отправляются Celery worker через SMTP. Активацию и сброс пароля завершайте вызовами API из Swagger или клиентского приложения, передавая токен в `POST /api/auth/activate/{token}` или `POST /api/auth/reset-password`.
- Swagger и OpenAPI публичны; доступ к пользовательским, модераторским и административным действиям ограничивается JWT и ролями.

## Автор

Vitalii Stetsenko
