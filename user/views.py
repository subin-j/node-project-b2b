import jwt
import bcrypt
import json

from enum import Enum

from django.http  import JsonResponse
from django.views import View

from .models import User

from my_settings      import SECRET_KEY #, HASHING_ALGORITHM
#from utils.decorators import auth_check


class SignUpView(View):
    pass


class SignInView(View):
    pass


class EditProfileView(View):
    pass


class DeleteAccountView(View):
    def delete(self,request):

        # get user id from request body
        data = json.loads(request.body)
        
        user_id = data.get('user_id')

        #identify user by pk and get a QS
        user = User.objects.get(user_id = user_id)
        user.delete()

        # serealize data to be compatible with python

        # return correct response 
        return JsonResponse({'messege':'??'},status=200)