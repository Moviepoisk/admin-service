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

        print('response: ', response)
        print("response.content", response.content)
        print("response.status_code", response.status_code)

        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()
        print('data', data)

        if 'access_token' not in data:
            return None


        

        headers = {
            'User-Agent': 'My User Agent 1.0',
            'accept': 'application/json',
            'Authorization': f"Bearer {data.get('access_token')}",
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        url = settings.AUTH_API_ME_URL
        response = requests.post(url, headers=headers)

        
        print('response 2: ', response)
        print("response.content 2", response.content)
        print("response.status_code 2", response.status_code)
        
        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()
        
        
        print("data 2", data)

        try:
            user, created = User.objects.get_or_create(id=data['id'])
            user.email = data.get('email')
            user.login = data.get('login')
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.is_admin = True  # data.get('role') == Roles.ADMIN
            user.is_active = True  # data.get('is_active')
            user.save()
            print(f"User created or updated: {user}")
        except Exception as e:
            print(f"Exception occurred: {e}")
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
