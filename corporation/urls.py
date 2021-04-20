from django.urls import path

from .views import IncomeStatementView

urlpatterns = [
    path('/income-statement', IncomeStatementView.as_view()),
]
