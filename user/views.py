import jwt
import bcrypt
import json
import re

from enum import Enum
from json import JSONDecodeError

from django.http  import JsonResponse, HttpResponse
from django.views import View
from django.db    import transaction

from .models import User, GridLayout

from my_settings      import SECRET_KEY, HASHING_ALGORITHM
from utils.decorators import auth_check
from utils.eng2kor    import engkor


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
            } for grid_layout in grid_layouts]
            return JsonResponse({'layout': layout}, status=200)

        if not grid_layouts:
            return JsonResponse({'layout': 'default'}, status=200)

    @auth_check
    def put(self, request):
        try:
            data        = json.loads(request.body)
            user_id     = request.user.id
            new_layouts = data['newLayout']
            
            for layout in new_layouts:    
                grid_id      = layout['id']
                x            = layout['x']
                y            = layout['y']
                w            = layout['w']
                h            = layout['h']
                is_draggable = layout.get('isDraggable', True)

                # id='0'인 카드의 is_draggable이 true로 들어오면 에러 리턴  
                if grid_id == '0' and is_draggable == True:
                    return JsonResponse({'message':'NOT_VALID'}, status=400)

                grid_layout = GridLayout.objects.filter(grid_id=grid_id, user_id=user_id)

                if grid_layout.exists():
                    grid_layout.update(
                        x            = x,
                        y            = y,
                        w            = w,
                        h            = h,
                        is_draggable = is_draggable
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
            return JsonResponse({'messge': 'SUCCESS'}, status=201)
   
        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"}, status=400)
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)
        except JSONDecodeError:
            return JsonResponse({'meesage': 'JSON_DECODE_ERROR'}, status=400)
        except IntegrityError:
            return JsonResponse({'message': 'INTEGRITY_ERROR'}, status=400)
