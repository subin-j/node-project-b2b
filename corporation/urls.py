from django.urls import path

from .views import CorporationInfoView, CorporationSearchView ,IncomeStatementView

urlpatterns = [
    path('', CorporationInfoView.as_view()),
    path('/search', CorporationSearchView.as_view()),
    path('/income-statement', IncomeStatementView.as_view()),
]
