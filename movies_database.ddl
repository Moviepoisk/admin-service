-- Создать БД
create database movies_database

-- Создать схему
CREATE SCHEMA IF NOT EXISTS content;

-- Устанавливаем расширения для генерации UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
