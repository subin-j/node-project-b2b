import jwt
import bcrypt
import json
import re

from enum import Enum
from json import JSONDecodeError

from django.http  import JsonResponse
from django.views import View

from .models import User

from my_settings      import SECRET_KEY, HASHING_ALGORITHM
#from utils.decorators import auth_check


class SignUpView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            email            = data['email']
            password         = data['password']
            corporation_name = data['corporation_name']

            p_email    = re.compile(r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9_-]+\.[a-zA-Z-.]+$')
            p_password = re.compile(r'^(?=.*[!-/:-@])(?!.*[ㄱ-ㅣ가-힣]).{8,20}$')

            if not p_email.match(email):
                return JsonResponse({'message': 'EMAIL_FORM_IS_NOT_VALID'}, status=400)
            if not p_password.match(password):
                return JsonResponse({'message': 'PASSWORD_FORM_IS_NOT_VALID'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'message': 'EMAIL_ALREADY_EXISTS'}, status=422)
            
            hashed_pw         = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            decoded_hashed_pw = hashed_pw.decode('utf-8')

            User.objects.create(
                        email            = email,
                        password         = decoded_hashed_pw,
                        corporation_name = corporation_name
                        )
            return JsonResponse({'message': 'SUCCESS'}, status=201)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)
        except JSONDecodeError:
            return JsonResponse({'meesage': 'JSON_DECODE_ERROR'}, status=400)


    def get(self, request):
        email = request.GET.get('email')
        if not email:
            return JsonResponse({'message': 'EMAIL_IS_NOT_GIVEN'})

        if User.objects.filter(email=email).exists():
            return JsonResponse({'message': 'DUPLICATE'}, status=200)
        return JsonResponse({'message': 'NOT_DUPLICATE'}, status=200)
        

class SignInView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = User.objects.get(email=data['email'])

            if bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
                access_token = jwt.encode({'user_id': user.id}, SECRET_KEY, algorithm=HASHING_ALGORITHM)
                return JsonResponse({'message': 'SUCCESS', 'access_token': access_token}, status=200)
            return JsonResponse({'message': 'INVALID_PASSWORD'}, status=401)
        
        except User.DoesNotExist:
            return JsonResponse({'message': 'USER_DOES_NOT_EXIST'}, status=404)
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)
        except JSONDecodeError:
            return JsonResponse({'meesage': 'JSON_DECODE_ERROR'}, status=400)


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