from django.urls import path

from .views import HolderSharesView

urlpatterns = [
    path('/shareholders',HolderSharesView.as_view()),
]