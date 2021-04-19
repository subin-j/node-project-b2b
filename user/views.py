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
from utils.decorators import auth_check


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
    @auth_check
    def patch(self, request):
        try:
            data = json.loads(request.body)

            new_password = data['new_password']
            login_user = request.user
            # 패스워드 체크
            password_check = bcrypt.check(new_password.encode('utf-8'), login_user.password.encode('utf-8'))
            # 패스워드가 같으면 메세지
            if password_check:
                return JsonResponse({'message':'SAME_PASSWORD'}, status=400)

            hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            login_user.password = hashed_password
            login_user.save()
            return JsonResponse({'message':'SUCCESS'}, status=201)
            #token = bytes(data['token'], 'utf-8')
            # password = data['password']
            # 
            # decoded_token = jwt.decode(token, SECRET_KEY, ALGORITHM)
# 
            # if not User.objects.filter(email=email).exist():
                # return JsonResponse({'message':'INVALID_USER'}, status=401)
# 
            # user          = User.objects.get(id=decoded_token['user_id'])
            # user.password = bcrypt.hashpw(password['resetPassword'].encode(), bcrypt.gensalt()).decode()
            # user.save()

            
        except:
            pass
# 일단 이메일로 유저확인
# 비밀번호 변경 (기존의 비밀번호와 새로운 비밀번호는 달라야함)
# 새로운 비밀번호 해시로 저장
class DeleteAccountView(View):
    pass
