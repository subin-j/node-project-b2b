from django.urls import path
from .views import StockPriceView, StockCandleChart, CurrentStockPriceView

urlpatterns = [
    path('/candle-chart', StockCandleChart.as_view()),
    path('/current_price', CurrentStockPriceView.as_view()),
]
