"""
Bean-price-compatible price downloader for Yahoo Finance.

Use:

    bean-price -e "AUD:pricedl.beanprice.yahoo/ASX:VHY"
"""

from datetime import datetime

# type: ignore
from beanprice import source
from loguru import logger

from pricedl.model import SecuritySymbol
from pricedl.quotes.yahoo_finance_downloader import YahooFinanceDownloader


class Source(source.Source):
    """
    My Yahoo price source
    """

    def get_latest_price(self, ticker) -> source.SourcePrice | None:
        '''
        Downloads the latest price for the ticker.
        '''
        try:
            symbol = ticker.split(':')

            sec_symbol = SecuritySymbol(symbol[0], symbol[1])

            dl = YahooFinanceDownloader()
            response = dl.download(sec_symbol, 'AUD')

            price = response.value

            min_time = datetime.min.time()
            time = datetime.combine(response.date, min_time)
            # The datetime must be timezone aware.
            time = time.astimezone()

            quote_currency = response.currency

            return source.SourcePrice(price, time, quote_currency)
        except Exception as e:
            logger.error(e)
            return None

    def get_historical_price(self, ticker, time):
        '''
        Downloads the historical price for the ticker.
        '''
        # todo: implement
        return None
