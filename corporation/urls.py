from django.urls import path

from .views import IncomeStatementView, CorpExcelExporter

urlpatterns = [
    path('/income-statement', IncomeStatementView.as_view()),
    path('/excels', CorpExcelExporter.as_view()),
]
