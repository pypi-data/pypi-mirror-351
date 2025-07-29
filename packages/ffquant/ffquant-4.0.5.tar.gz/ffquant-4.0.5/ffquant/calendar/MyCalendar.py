import os
from datetime import datetime, timedelta
from ffquant.utils.Logger import stdout_log
import requests

__ALL__ = ['MyCalendar']

class MyCalendar:

    """
    Daily tradable range item should be in the format of "HHMM-HHMM"
    """
    DAILY_TRADABLE_RANGES = []

    def __init__(self):
        self.base_url = 'http://192.168.25.98'

    """
    Checks if a given stock symbol is tradable at a specific date and time.

    Parameters:
        symbol (str): The stock symbol to check.
        dt (str): The date and time(Hong Kong timezone) to check. Format: 'YYYY-mm-dd HH:MM:SS'.

    Returns:
        bool: True if the symbol is tradable, False otherwise.
    """
    def isSymbolTradable(self, symbol: str, dt: str, debug = False) -> bool:
        if len(self.DAILY_TRADABLE_RANGES) > 0:
            for range in self.DAILY_TRADABLE_RANGES:
                start, end = range.split('-')
                dtime = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
                start_dt = dtime.replace(hour=int(start[:2]), minute=int(start[2:]), second=0, microsecond=0)
                end_dt = dtime.replace(hour=int(end[:2]), minute=int(end[2:]), second=0, microsecond=0)
                if dtime >= start_dt and dtime <= end_dt:
                    return True
            return False
        else:
            broker = None
            if str(symbol).__contains__('@'):
                symbol, broker = symbol.split('@')

            url = "http://192.168.25.247:8220/current/trade/status"
            params = {
                "symbol": symbol,
                "time":dt
            }

            response = requests.get(url, params=params).json()
            if debug:
                stdout_log(f"MyCalendar, response: {response}, url: {url}, params: {params}")

            if response.get('code') == "200":
                return response['results']['isTradeOpen'] and response['results']['status'] == 'ACTIVE'
            else:
                return False
    
    def getTradableSymbols(self, kline_time_str: str) -> list:
        kline_time = datetime.strptime(kline_time_str, '%Y-%m-%d %H:%M:%S')
        start_datetime_str = kline_time.strftime('%Y-%m-%d %H:%M')
        end_datetime_str = (kline_time + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M')
        url = "http://192.168.25.96:8000/api/symbol/available/"
        params = {
            "start_datetime": start_datetime_str,
            "end_datetime": end_datetime_str
        }

        symbols = []
        response = requests.get(url, params=params).json()
        for item in response:
            symbols.append(item['symbol'])
        return symbols

if __name__ == "__main__":
    calendar = MyCalendar()
    # for hour in range(24):
    #     for minute in range(60):
    #         dt = f'2024-10-29 {hour:02d}:{minute:02d}:00'
    #         stdout_log(dt + ": " + ("Tradable" if calendar.isSymbolTradable('CAPITALCOM:HK50@tv', dt) else "Untradable"))
    print(calendar.getTradableSymbols('2025-04-29 09:30:00'))