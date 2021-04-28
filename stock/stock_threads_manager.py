import threading
import time
import datetime

from stock.stock_price_crawler import get_current_price
from channels.layers           import get_channel_layer
from asgiref.sync              import async_to_sync

from utils.debugger import debugger


SUICIDE_TIME = 5
PRICE_PUSH_CYCLE = 5


class StockAgentsManger(threading.Thread):
    def __init__(self, queue):
        super(StockAgentsManger, self).__init__(name='StockAgentsManger')
        self.daemon        = True
        self.stock_agents  = dict()
        self.queue         = queue
        self.stop_flag     = threading.Event()
        self.channels_lock = threading.Lock()

    def add_stock_price_agent(self, ticker_group, channel):
        agent = self.stock_agents.get(ticker_group, None)
        if agent is None or not agent.is_alive():
            agent = StockPriceCrawlerAgent(ticker_group, self.stop_flag, self.channels_lock)
            agent.start()
            self.stock_agents[ticker_group] = agent

            debugger.info('starting thread : {}'.format(agent))
        agent.add_channel(channel)

    def remove_stock_price_agent(self, ticker_group, channel):
        self.stock_agents[ticker_group].remove_channel(channel)
    
    def stop(self):
        self.stop_flag.set()
    
    def run(self):
        while not self.stop_flag.is_set():
            user_conn = self.queue.get()
            if user_conn.connection:
                self.add_stock_price_agent(user_conn.ticker_group, user_conn.channel)
            else:
                self.remove_stock_price_agent(user_conn.ticker_group, user_conn.channel)


class StockPriceCrawlerAgent(threading.Thread):
    def __init__(self, ticker_group, stop_flag, channels_lock):
        super(StockPriceCrawlerAgent, self).__init__(name=ticker_group)
        self.ticker_group  = ticker_group
        self.ticker        = ticker_group.split('_')[-1]
        self.channels      = list()
        self.channels_lock = channels_lock
        self.channel_layer = get_channel_layer()

        self.stop_flag    = stop_flag
        self.suicide_time = None

    def add_channel(self, channel):
        with self.channels_lock:
            self.channels.append(channel)
    
    def remove_channel(self, channel):
        with self.channels_lock:
            self.channels.remove(channel)
        
        if self.is_empty():
            self.set_suicide_time()
    
    def set_suicide_time(self):
        self.suicide_time = time.time()

    def is_empty(self):
        with self.channels_lock:
            return len(self.channels) == 0

    def run(self):
        while not self.stop_flag.is_set():
            if self.suicide_time:
                if not self.is_empty():
                    self.suicide_time = None
                else:
                    if time.time() > self.suicide_time + SUICIDE_TIME:
                        break

            current_price, open_price = get_current_price(self.ticker)     
            
            change_rate  = (current_price - open_price) / open_price * 100
            current_time = str(datetime.datetime.now())

            async_to_sync(self.channel_layer.group_send)(
                self.ticker_group,
                {
                    'type'         : 'push_current_price',
                    'ticker'       : self.ticker,
                    'current_price': current_price,
                    'current_time' : current_time,
                    'change_rate'  : change_rate
                }
            )

            if not self.is_empty():
                time.sleep(PRICE_PUSH_CYCLE)
        debugger.info('Breaking Thread : {}'.format(self))
