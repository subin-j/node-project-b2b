from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/stock/price/<str:ticker>', consumers.StockConsumer.as_asgi()),
]
