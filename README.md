# Тестовое задание Python (Postgres, Elasticsearch)

FastAPI приложение, реализует полнотекстовый поиск в индексе и удаление записей из базы данных

Основная база данных: PostgreSQL

В рамках хранения индексируемых данных, был выбран Elasticsearch, который в разы быстрее индексов реляционной базы

## Usage

Для запуска требуется git и docker

Скопируйте репозиторий и запустите контейнеры (make up)

```bash
git https://github.com/TiJon8/python-test-case.git
cd python-test-case
make up
```

Приложение запуститься на 8000 порту. Swagger UI будет доступен по http://127.0.0.1:8000/docs (или /redoc)

## API

#### Релевантный поиск постов по запросу

```http
GET /posts/search?q=новый+скин
```

| Parameter | Type     | Description                 |
| :-------- | :------- | :-------------------------- |
| `q`       | `string` | **Required**. текст запроса |

Если query-параметр не передать, возникнет ошибка 422

#### Удаление поста

```http
DELETE /posts/{post_id}
```

| Parameter | Type  | Description            |
| :-------- | :---- | :--------------------- |
| `id`      | `int` | **Required**. ID поста |

Если ID не найден, вернется 404, в противном случае 204
