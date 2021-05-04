import jwt
import bcrypt
import json
import re
import base64
import random
import time
import hmac
import hashlib
import requests
import redis
import datetime

from enum import Enum
from json import JSONDecodeError

from django.http  import JsonResponse, HttpResponse
from django.views import View
from django.db    import transaction

from .models import User, GridLayout

from my_settings      import (
                            SECRET_KEY, HASHING_ALGORITHM, NAVER_ACCESS_KEY,
                            FROM_PHONE_NUMBER, SMS_SERVICE_ID, NAVER_SECRET_KEY,
                            REDIS_HOST, REDIS_PORT
                            )
from utils.decorators import auth_check
from utils.eng2kor    import engkor
from utils.redis_connection import RedisConnection


SMS_AUTH_CONTENT = 'Anser B2B Service\n Authentication Code: '
COUNTRY_CODE = '82'
SMS_AUTH_TIMEOUT = 300


class SignUpView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            email             = data['email']
            password          = data['password']
            corporation_name  = data['corporation_name']
            name              = data['name']
            auth_phone_number = data['auth_phone_number']

            rd   = RedisConnection()
            auth = rd.conn.hgetall(auth_phone_number)
            if not auth:
                return JsonResponse({'message': 'CODE_AUTH_ERROR'}, status=400)                

            is_verified = auth['is_verified']
            if is_verified != '1':
                return JsonResponse({'message': 'PHONE_NUMBER_VERIFICATION_NOT_COMPLETE'}, status=400)

            p_email        = re.compile(r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9_-]+\.[a-zA-Z-.]+$')
            p_password     = re.compile(r'^(?=.*[!-/:-@])(?!.*[ㄱ-ㅣ가-힣]).{8,20}$')
            p_phone_number = re.compile(r'^[0-9]{11}$')

            if not p_email.match(email):
                return JsonResponse({'message': 'EMAIL_FORM_NOT_VALID'}, status=400)
            if not p_password.match(password):
                return JsonResponse({'message': 'PASSWORD_FORM_NOT_VALID'}, status=400)
            if not p_phone_number.match(auth_phone_number):
                return JsonResponse({'message': 'PHONE_NUMBER_NOT_VALID'}, status=400)
            if not len(name) < 100:
                return JsonResponse({'message': 'NAME_TOO_LONG'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'message': 'EMAIL_ALREADY_EXISTS'}, status=422)
            
            hashed_pw         = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            decoded_hashed_pw = hashed_pw.decode('utf-8')

            User.objects.create(
                        email            = email,
                        password         = decoded_hashed_pw,
                        corporation_name = corporation_name,
                        name             = name,
                        phone_number     = auth_phone_number
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
                user_info    = {
                    'name'            : user.name,
                    'corporation_name': user.corporation_name,
                    'email'           : user.email,
                    'is_verified'     : user.is_verified
                }

                return JsonResponse({'message': 'SUCCESS', 'access_token': access_token, 'user': user_info}, status=200)
            return JsonResponse({'message': 'INVALID_PASSWORD'}, status=401)
        
        except User.DoesNotExist:
            return JsonResponse({'message': 'USER_DOES_NOT_EXIST'}, status=404)
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)
        except JSONDecodeError:
            return JsonResponse({'meesage': 'JSON_DECODE_ERROR'}, status=400)


class ProfileView(View):
    def __init__(self):
        super(ProfileView, self).__init__()
        self.login_user = None

    @transaction.atomic
    @auth_check
    def patch(self, request):
        try:
            data = json.loads(request.body)

            new_password = data.get('new_password', '')
            new_corporation_name = data.get('new_corporation_name', '')
            self.login_user = request.user

            if not new_password and not new_corporation_name:
                return JsonResponse({'message': 'DATA_NOT_FILLED'}, status=400)

            if new_password:
                edit_password = self.edit_password(new_password)
                if isinstance(edit_password, JsonResponse):
                    transaction.set_rollback(True)
                    return edit_password

            if new_corporation_name:
                edit_corporation_name = self.edit_corporation_name(new_corporation_name)
                if isinstance(edit_corporation_name, JsonResponse):
                    transaction.set_rollback(True)
                    return edit_corporation_name

            return JsonResponse({'message':'SUCCESS'}, status=201)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)

    def edit_password(self, new_password):
        p_password = re.compile(r'^(?=.*[!-/:-@])(?!.*[ㄱ-ㅣ가-힣]).{8,20}$')
        if not p_password.match(new_password):
            return JsonResponse({'message': 'PASSWORD_FORM_IS_NOT_VALID'}, status=400)

        password_check = bcrypt.checkpw(new_password.encode('utf-8'), self.login_user.password.encode('utf-8'))
        if password_check:
            return JsonResponse({'message':'SAME_PASSWORD'}, status=400)

        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode('utf-8')
        self.login_user.password = hashed_password
        self.login_user.save()
        return True
    
    def edit_corporation_name(self, new_corporation_name):
        if new_corporation_name == self.login_user.corporation_name:
            return JsonResponse({'message':'SAME_CORP_NAME'}, status=400)

        self.login_user.corporation_name = new_corporation_name
        self.login_user.save()
        return True

    @auth_check
    def delete(self, request):
        try:
            user_id = request.user.id
            user    = User.objects.get(id= user_id)
            user.delete()
            return HttpResponse(status=204)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)


class GridLayoutView(View):
    @auth_check
    def get(self, request):
        user_id = request.user.id
        grid_layouts = GridLayout.objects.filter(user_id=user_id)

        if grid_layouts:
            layout =[
                {
                'id':grid_layout.grid_id,
                'x': grid_layout.x,
                'y': grid_layout.y,
                'w': grid_layout.w,
                'h': grid_layout.h,
                'is_draggable': grid_layout.is_draggable 
            } for grid_layout in grid_layouts if grid_layout.is_displyed]
            return JsonResponse({'layout': layout}, status=200)

        if not grid_layouts:
            return JsonResponse({'layout': 'default'}, status=200)

    @auth_check
    def put(self, request):
        try:
            data        = json.loads(request.body)
            user_id     = request.user.id
            new_layouts = data['newLayout']
            
            grid_ids = list()
            for layout in new_layouts:    
                grid_id      = layout['id']
                x            = layout['x']
                y            = layout['y']
                w            = layout['w']
                h            = layout['h']
                is_draggable = layout.get('isDraggable', True)

                grid_layout = GridLayout.objects.filter(grid_id=grid_id, user_id=user_id)
                if grid_layout.exists():
                    grid_layout.update(
                        x            = x,
                        y            = y,
                        w            = w,
                        h            = h,
                        is_draggable = is_draggable,
                        is_displyed  = True
                    )
                else: 
                    GridLayout.objects.create(
                        grid_id      = grid_id,
                        user_id      = user_id,
                        x            = x,
                        y            = y,
                        w            = w,
                        h            = h,
                        is_draggable = is_draggable
                        )
                grid_ids.append(grid_id)
            GridLayout.objects.exclude(grid_id__in=grid_ids).update(is_displyed=False)

            return JsonResponse({'messge': 'SUCCESS'}, status=201)
   
        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"}, status=400)
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)
        except JSONDecodeError:
            return JsonResponse({'meesage': 'JSON_DECODE_ERROR'}, status=400)
        except IntegrityError:
            return JsonResponse({'message': 'INTEGRITY_ERROR'}, status=400)


class SMSCodeRequestView(View):
    def post(self, request):
        try:
            data              = json.loads(request.body)
            auth_phone_number = data['auth_phone_number']

            random_code        = str(random.randint(1000, 9999))
            hashed_random_code = bcrypt.hashpw(random_code.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            is_verified        = '0'

            auth = {'hashed_random_code': hashed_random_code, 'is_verified': is_verified}

            rd = RedisConnection()
            rd.conn.hmset(auth_phone_number, auth)
            rd.conn.expire(auth_phone_number, SMS_AUTH_TIMEOUT)

            timestamp         = str(int(time.time() * 1000))
            signature         = self.make_signature()

            headers = {
                'Content-Type':'application/json; charset=UTF-8',
                'x-ncp-apigw-timestamp':timestamp,
                'x-ncp-iam-access-key': NAVER_ACCESS_KEY,
                'x-ncp-apigw-signature-v2':signature
            } 
            
            body = {
                "type": "sms",
                "countryCode": COUNTRY_CODE,
                "from": "{}".format(FROM_PHONE_NUMBER),
                "content": "{}{}".format(SMS_AUTH_CONTENT, random_code),
                "messages":[
                    {
                        "to": "{}".format(auth_phone_number)
                    }
                ]
            }

            sms_service_url = 'https://sens.apigw.ntruss.com/sms/v2/services/{}/messages'.format(SMS_SERVICE_ID)
            response        = requests.post(sms_service_url, headers=headers, data=json.dumps(body))
            
            if response.status_code == 202:
                return JsonResponse({'message': 'CODE_SEND_SUCCESS'})
            return JsonResponse({'message': 'CODE_SEND_ERROR'})

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)            
        except JSONDecodeError:
            return JsonResponse({'message': 'JSON_DECODE_ERROR'}, status=400)

    def make_signature(self):
        timestamp   = int(time.time() * 1000)
        timestamp   = str(timestamp)

        secret_key  = bytes(NAVER_SECRET_KEY, 'UTF-8')

        method      = "POST"
        uri         = '/sms/v2/services/{}/messages'.format(SMS_SERVICE_ID)

        message     = method + " " + uri + "\n" + timestamp + "\n" + NAVER_ACCESS_KEY
        message     = bytes(message, 'UTF-8')

        signing_key = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
        return signing_key   
        

class SMSCodeCheckView(View):
    def post(self, request):
        try:
            data              = json.loads(request.body)
            auth_code         = data['auth_code']
            auth_phone_number = data['auth_phone_number']

            rd   = RedisConnection()
            auth = rd.conn.hgetall(auth_phone_number)
            if not auth:
                return JsonResponse({'message': 'CODE_EXPIRED'}, status=400)

            hashed_random_code = auth['hashed_random_code']

            if not bcrypt.checkpw(auth_code.encode('utf-8'), hashed_random_code.encode('utf-8')):
                return JsonResponse({'message': 'CODE_NOT_MATCHED'}, status=400)

            auth['is_verified'] = '1'
            rd.conn.hmset(auth_phone_number, auth)
            return JsonResponse({'message': 'SUCCESS'}, status=201)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)            
        except JSONDecodeError:
            return JsonResponse({'message': 'JSON_DECODE_ERROR'}, status=400)
