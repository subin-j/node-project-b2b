from django.urls import path
from .views import StockPriceView, StockCandleChart

urlpatterns = [
    path('/candle-chart', StockCandleChart.as_view()),
    path('/current_price', )
]
