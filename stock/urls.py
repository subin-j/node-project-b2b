from django.urls import path
from .views import StockPriceView, StockCandleChart

urlpatterns = [
    path('/price', StockPriceView.as_view()),
    path('/candle-chart', StockCandleChart.as_view()),
]
