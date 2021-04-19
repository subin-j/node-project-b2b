from django.urls import path

from .views import SignUpView, SignInView, EditProfileView

urlpatterns = [
    path('/sign-up', SignUpView.as_view()),
    path('/sign-in', SignInView.as_view()),
    path('/edit', EditProfileView.as_view())
]
