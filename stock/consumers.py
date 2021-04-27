import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from anser_b2b.settings import manager_queue


class UserConnection(object):
    def __init__(self, connection, ticker_group, channel):
        self.connection = connection
        self.ticker_group = ticker_group
        self.channel = channel


class StockConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super(StockConsumer, self).__init__(*args, **kwargs)
        self.queue = manager_queue

    def connect(self):
        self.ticker            = self.scope['url_route']['kwargs']['ticker']
        self.ticker_group_name = 'ticker_{}'.format(self.ticker)

        async_to_sync(self.channel_layer.group_add)(
            self.ticker_group_name,
            self.channel_name
        )
        self.accept()

        user_conn = UserConnection(True, self.ticker_group_name, self.channel_name)
        self.queue.put(user_conn)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.ticker_group_name,
            self.channel_name
        )

        user_conn = UserConnection(False, self.ticker_group_name, self.channel_name)
        self.queue.put(user_conn)

    def push_current_price(self, event):
        current_price = event['current_price']
        ticker        = event['ticker']
        current_time  = event['current_time']
        change_rate   = event['change_rate']

        self.send(text_data=json.dumps({
            'current_price': current_price,
            'ticker'       : ticker,
            'current_time' : current_time,
            'change_rate'  : change_rate
        }))
