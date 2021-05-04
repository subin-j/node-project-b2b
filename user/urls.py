from django.urls import path

from .views import (SignUpView, SignInView, 
                    ProfileView, GridLayoutView,
                    SMSCodeRequestView ,SMSCodeCheckView)

urlpatterns = [
    path('/sign-up', SignUpView.as_view()),
    path('/sign-in', SignInView.as_view()),
    path('/profile', ProfileView.as_view()),
    path('/grid-layout', GridLayoutView.as_view()),
    path('/auth-code', SMSCodeRequestView.as_view()),
    path('/auth-code/check', SMSCodeCheckView.as_view()),
]
