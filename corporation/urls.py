from django.urls import path

from .views import MainShareHoldersView

urlpatterns = [
    path('/main-shareholders',MainShareHoldersView.as_view()),
]