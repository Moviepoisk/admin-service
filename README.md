# Панель администратора

## Запуск

Для работы данного сервиса требуется Postgres и S3. Переменные конфигураций берутся из .env файла
Пример /app/config/.env.example

```bash
poetry shell
cd app
./run.sh
```

### Запуск Postgres
```
docker run -d \
  --name postgres \
  -p 5432:5432 \
  -v $HOME/postgresql/data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=123qwe \
  -e POSTGRES_USER=app \
  -e POSTGRES_DB=movies_database  \
  postgres:16
```

применить ddl файл для создания начальных схем и таблиц
```

psql -h 127.0.0.1 -U app -d movies_database -f movies_database.ddl
```

подключиться
```
psql -h 127.0.0.1 -U app -d movies_database
```

создать все служебные таблицы

python manage.py migrate

## Заполнение тестовыми данными

python manage.py seed_data
данные берутся из db.sqlite

## Очистка всей BD с тестовыми данными

python manage.py clean_db

## Создание администратора

```bash
python manage.py createsuperuser
```


указание схем на уровне БД независимо от настроек подключения

```sql
ALTER DATABASE moviepoisk SET search_path TO public,content;
```

Для сборки мультиконтейнера

```bash
docker buildx create --name multiarch --driver docker-container --use
```

чтобы запускалось на linux

`docker buildx build --platform linux/x86_64 -t arigatory/moviepoisk-admin --builder multiarch --push .`