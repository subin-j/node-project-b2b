from django.urls import path

from .views      import DeleteAccountView

urlpatterns = [
    path('/delete-account',DeleteAccountView.as_view())
]
