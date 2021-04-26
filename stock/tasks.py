from __future__ import absolute_import, unicode_literals
from celery import shared_task, current_app
from celery.signals import celeryd_init

import threading
import time


class StockAgentsManger(threading.Thread):
    def __init__(self, queue):
        super(StockAgentsManger, self).__init__()
        self.daemon        = True
        self.stock_agents  = dict()
        self.queue         = queue
        self.stop_flag     = threading.Event()
        self.channels_lock = threading.Lock()

    def add_stock_price_agent(self, channel, ticker_group):
        agent = self.stock_agents.get(ticker_group, None)
        if agent is None or not agent.is_alive():
            agent = StockPriceCrawlerAgent(ticker_group, self.stop_flag, self.channels_lock)
            agent.start()
            self.stock_agents[ticker_group] = agent
        agent.add_channel(channel)

    def remove_stock_price_agent(self, channel, ticker_group):
        self.stock_agents[ticker_group].remove_channel(channel)
    
    def stop(self):
        self.stop_flag.set()
    
    def run(self):
        while not self.stop_flag.is_set():
            time.sleep(5)
            print('hey')


class StockPriceCrawlerAgent(threading.Thread):
    def __init__(self, ticker_group, stop_flag, channels_lock):
        super(StockThreadsManger, self).__init__(name=ticker_group)
        self.channels = list()
        self.channels_lock = channels_lock

    def add_channel(self, channel):
        with self.channels_lock:
            self.channels.append(channel)
    
    def remove_channel(self, channel):
        with self.channels_lock:
            self.channels.remove(channel)


@shared_task
def run_manager_thread():
    stock_agents_manager = StockAgentsManger(manager_queue)
    stock_agents_manager.start()
