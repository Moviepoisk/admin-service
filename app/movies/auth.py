import http
import json
from enum import StrEnum, auto

import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class Roles(StrEnum):
    ADMIN = auto()
    SUBSCRIBER = auto()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_API_LOGIN_URL

        headers = {
            'User-Agent': 'My User Agent 1.0',
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
            'grant_type': '',
            'username': username,
            'password': password,
            'scope': '',
            'client_id': '',
            'client_secret': '',
        }

        response = requests.post(url, headers=headers, data=data)

        print(response)
        print(response.content)
        print(response.status_code)
        data = response.json()
        print(data)
        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()

        headers = {
            'User-Agent': 'My User Agent 1.0',
            'accept': 'application/json',
            'Authorization': f'Bearer {data.get('access_token')}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        url = settings.AUTH_API_ME_URL
        response = requests.post(
            url, headers=headers)

        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()

        try:
            user, created = User.objects.get_or_create(id=data['id'],)
            user.email = data.get('email')
            user.login = data.get('login')
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.is_admin = True  # data.get('role') == Roles.ADMIN
            user.is_active = True  # data.get('is_active')
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
