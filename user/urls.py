from django.urls import path

from .views import (SignUpView, SignInView, 
                    EditProfileView, DeleteAccountView)

urlpatterns = [
    path('/sign-up', SignUpView.as_view()),
    path('/sign-in', SignInView.as_view()),
    path('/user', EditProfileView.as_view()),
    path('',DeleteAccountView.as_view())
]
