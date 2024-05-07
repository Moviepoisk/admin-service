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
из репозитория infra
```
docker compose up -d postgres
```

применить sql в БД из файла movies_database.ddl

создать все таблицы

```
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
```


------
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