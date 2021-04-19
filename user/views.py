import jwt
import bcrypt
from enum import Enum

from django.http  import JsonResponse
from django.views import View

from .models import User

from my_settings      import SECRET_KEY, HASHING_ALGORITHM
from utils.decorators import auth_check


class SignUpView(View):
    pass


class SignInView(View):
    pass


class EditProfileView(View):
    pass


class DeleteAccountView(View):
    pass
