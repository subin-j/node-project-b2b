from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
    url(r'^ws/stock/price', consumers.StockConsumer.as_asgi()),
]
