from django.urls import path

from .views import (
    MainShareHoldersView, CorporationInfoView, 
    CorporationSearchView ,IncomeStatementView,
    CorpExcelExporter , ConglomerateListView
)

urlpatterns = [
    path('', CorporationInfoView.as_view()),
    path('/search', CorporationSearchView.as_view()),
    path('/main-shareholders', MainShareHoldersView.as_view()),
    path('/income-statement', IncomeStatementView.as_view()),
    path('/excels', CorpExcelExporter.as_view()),
    path('/conglomerate', ConglomerateListView.as_view())
]
