from django.urls import path
from .views import StockPriceView

urlpatterns = [
    path('/price', StockPriceView.as_view()),
]
