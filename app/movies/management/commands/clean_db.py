import datetime
import sqlite3
import uuid

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any
from django.core.management.base import BaseCommand

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
    def truncate_table(self, connection, table_name) -> None:
        """Удалить все из таблицы"""
        with connection.cursor() as cursor:
            query = (
                f"truncate table content.{table_name} cascade"
            )
            cursor.execute(query)
            connection.commit()


def clear_all_tables(pg_conn: _connection):
    """Метод для очистки всех таблиц в postgres"""
    print("Начато стирание всех данных")

    print("Создание класса для очистки в Postgres")
    postgres_saver = PostgresSaver()

    table_type_to_clear = {
        "genre": Genre,
        "person": Person,
        "film_work": Filmwork,
        "genre_film_work": GenreFilmwork,
        "person_film_work": PersonFilmwork,
    }

    for table in table_type_to_clear:
        print(f"Стирание таблицы: {table}")
        postgres_saver.truncate_table(pg_conn, table)


class Command(BaseCommand):
    """Django command to seed database"""

    def handle(self, *args: Any, **options: Any):
        self.stdout.write("Starting seeding the database...")

        load_dotenv()

        DATABASE_NAME = os.getenv("DB_NAME")
        DATABASE_USER = os.getenv("DB_USER")
        DATABASE_PASSWORD = os.getenv("DB_PASSWORD")
        DATABASE_HOST = os.getenv("DB_HOST")
        DATABASE_PORT = os.getenv("DB_PORT")

        dsl = {
            "dbname": DATABASE_NAME,
            "user": DATABASE_USER,
            "password": DATABASE_PASSWORD,
            "host": DATABASE_HOST,
            "port": int(DATABASE_PORT),
        }

        print(dsl)
        print('go-go')

        # Используем contextlib.closing для управления psycopg2.connect
        with closing(psycopg2.connect(**dsl, cursor_factory=DictCursor)) as pg_conn:
            clear_all_tables(pg_conn)

        self.stdout.write(self.style.SUCCESS("Database has beed DELETED!"))
