import http
from enum import StrEnum, auto

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.db import IntegrityError

User = get_user_model()

class Roles(StrEnum):
    ADMIN = auto()
    SUBSCRIBER = auto()

class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        # Авторизация пользователя
        auth_response = self._get_auth_response(username, password)
        if not auth_response or auth_response.status_code != http.HTTPStatus.OK:
            print("Auth response error or not OK")
            return None

        auth_data = auth_response.json()
        if "access_token" not in auth_data:
            print("No access token in auth data")
            return None

        # Получение информации о пользователе
        user_response = self._get_user_response(auth_data.get("access_token"))
        if not user_response or user_response.status_code != http.HTTPStatus.OK:
            print("User response error or not OK")
            return None

        user_data = user_response.json()
        user = self._create_or_update_user(user_data)
        return user

    def _get_auth_response(self, username, password):
        url = settings.AUTH_API_LOGIN_URL
        headers = {
            "User-Agent": "My User Agent 1.0",
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "",
            "username": username,
            "password": password,
            "scope": "",
            "client_id": "",
            "client_secret": "",
        }
        response = requests.post(url, headers=headers, data=data)
        print("Auth response status:", response.status_code)
        print("Auth response content:", response.content)
        return response

    def _get_user_response(self, access_token):
        url = settings.AUTH_API_ME_URL
        headers = {
            "User-Agent": "My User Agent 1.0",
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(url, headers=headers)
        print("User response status:", response.status_code)
        print("User response content:", response.content)
        return response

    def _create_or_update_user(self, data):
        try:
            # Проверка на наличие обязательных полей
            required_fields = ["id", "email", "login", "first_name", "last_name"]
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValueError(f"{field} not provided or is empty in data")

            # Получение или создание пользователя по ID
            user, created = User.objects.get_or_create(id=data["id"])

            # Обновление полей пользователя, если они не пустые
            user.email = data["email"]
            user.username = data["login"]
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.is_active = True
            user.is_admin = True

            # Проверка перед сохранением, чтобы избежать нарушения уникальных ограничений
            if User.objects.filter(username=user.username).exclude(id=user.id).exists():
                raise IntegrityError(f"Username {user.username} already exists.")

            user.save()
            print(f"User {user} created or updated")
            print(f"User details after save: {user.__dict__}")
            return user

        except IntegrityError as e:
            print(f"IntegrityError occurred: {e}")
            return None
        except KeyError as e:
            print(f"Missing key in data: {e}")
            return None
        except ValueError as e:
            print(f"Value error: {e}")
            return None
        except Exception as e:
            print(f"Exception occurred: {e}")
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
