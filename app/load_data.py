import datetime
import sqlite3
import uuid

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from contextlib import contextmanager
from dataclasses import astuple, dataclass, field, fields
from typing import List, Type

import os
from dotenv import load_dotenv

from contextlib import closing


@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    yield conn
    conn.close()


@dataclass(frozen=True)
class Genre:
    name: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class Filmwork:
    title: str
    description: str
    creation_date: datetime.datetime
    rating: float
    type: str
    file_path: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class GenreFilmwork:
    genre_id: uuid.UUID
    film_work_id: uuid.UUID
    created_at: datetime.datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class Person:
    full_name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class PersonFilmwork:
    person_id: uuid.UUID
    film_work_id: uuid.UUID
    created_at: datetime.datetime
    role: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


class PostgresSaver:
    def save_all(self, connection, items, table_name) -> None:
        """Сохранить все"""
        # Получаем названия колонок таблицы (полей датакласса)
        column_names = [field.name for field in fields(items[0])]  # id, name
        names_string = ", ".join(column_names)
        # В зависимости от количества колонок генерируем под них %s.
        col_count = ", ".join(["%s"] * len(column_names))  # '%s, %s
        with connection.cursor() as cursor:
            data = list(astuple(row) for row in items)
            args = ",".join(
                cursor.mogrify(f"({col_count})", item).decode("utf-8") for item in data
            )
            query = (
                f"INSERT INTO content.{table_name} ({names_string}) "
                f"VALUES {args} "
                f" ON CONFLICT (id) DO NOTHING"
            )
            cursor.execute(query)
            connection.commit()

    def extract_data(self, connection, table_name: str, obj_type: Type) -> List:
        with connection.cursor() as curs:
            curs.execute(f"SELECT * FROM content.{table_name};")
            data = curs.fetchall()
            return [obj_type(**dict(item)) for item in data]

    def count_records(self, connection, table_name: str) -> int:
        """Возвращает количество записей в указанной таблице"""
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM content.{table_name};")
            count = cursor.fetchone()[0]
            return count


class SQLiteExtractor:
    def extract_data_batch(
        self,
        connection: sqlite3.Connection,
        table_name: str,
        obj_type: Type,
        batch_size: int,
    ) -> List:
        curs = connection.cursor()
        curs.execute(f"SELECT * FROM {table_name};")
        while True:
            batch = curs.fetchmany(batch_size)
            if not batch:
                break
            yield [obj_type(**dict(item)) for item in batch]

    def extract_data(
        self, connection: sqlite3.Connection, table_name: str, obj_type: Type
    ) -> List:
        curs = connection.cursor()
        curs.execute(f"SELECT * FROM {table_name};")
        data = curs.fetchall()
        return [obj_type(**dict(item)) for item in data]


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    print("Начат перенос данных")

    print("Создание класса для сохранения в Postgres")
    postgres_saver = PostgresSaver()

    print("Создание класса для считывания из Sqlite")
    sqlite_extractor = SQLiteExtractor()

    table_type_to_transfer = {
        "genre": Genre,
        "person": Person,
        "film_work": Filmwork,
        "genre_film_work": GenreFilmwork,
        "person_film_work": PersonFilmwork,
    }
    batch_size = 1000

    for table in table_type_to_transfer:
        total = postgres_saver.count_records(pg_conn, table)
        if total == 0:
            print(f"Считывание таблицы {table}")
            data_batch_generator = sqlite_extractor.extract_data_batch(
                connection, table, table_type_to_transfer[table], batch_size
            )
            print(f"Запись таблицы {table}")
            for data_batch in data_batch_generator:
                postgres_saver.save_all(pg_conn, data_batch, table)


if __name__ == "__main__":
    load_dotenv()

    DATABASE_NAME = os.getenv("DB_NAME")
    DATABASE_USER = os.getenv("DB_USER")
    DATABASE_PASSWORD = os.getenv("DB_PASSWORD")
    DATABASE_HOST = os.getenv("DB_HOST")
    DATABASE_PORT = "5432"

    dsl = {
        "dbname": DATABASE_NAME,
        "user": DATABASE_USER,
        "password": DATABASE_PASSWORD,
        "host": DATABASE_HOST,
        "port": int(DATABASE_PORT),
    }

    with conn_context("db.sqlite") as sqlite_conn:
        # Используем contextlib.closing для управления psycopg2.connect
        with closing(psycopg2.connect(**dsl, cursor_factory=DictCursor)) as pg_conn:
            load_from_sqlite(sqlite_conn, pg_conn)
