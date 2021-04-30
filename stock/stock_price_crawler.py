import investpy
import json
import re

from utils.error_handlers import handle_stock_price_crawler_input_error


def get_current_price(stock_symbol):
    """
    get parameter (stock ticker symbol), and decide whether the country is south korea or united states
    south korea ticker symbol starts with a number while that of United states starts with an alphabet
    """
    x = re.match("[0-9]", stock_symbol)

    country = "south korea" if x else "united states"

    try:
        current_price_raw = investpy.stocks.get_stock_recent_data(
                                                                stock_symbol,
                                                                country,
                                                                as_json  = True,
                                                                order    = 'descending',
                                                                interval = 'Daily'
                                                            )
    except Exception as e:
        return handle_stock_price_crawler_input_error(e)

    current_price_dict = json.loads(current_price_raw)

    current_price = current_price_dict['recent'][0]['close']
    open_price = current_price_dict['recent'][0]['open']

    return current_price, open_price
