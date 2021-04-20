from django.urls import path

from .views import CorporationInfoView, CorporationSearchView

urlpatterns = [
    path('', CorporationInfoView.as_view()),
    path('/search', CorporationSearchView.as_view())
]
