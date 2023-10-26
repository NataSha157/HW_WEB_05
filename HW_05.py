import sys
from datetime import datetime, timedelta

import aiohttp
import asyncio
import platform


async def my_request(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                result = await response.json()
                return result
            else:
                print(f"Error status: {response.status} for {url}")


async def parser_response(url, currencies_add: list = None) -> dict:
    currencies_base = ['USD', 'EUR']
    currencies = currencies_base + currencies_add
    my_data = await my_request(url)
    my_date = my_data.get('date')
    my_json = {}
    my_dic = {}
    for el in my_data.get('exchangeRate'):
        for cur in currencies:
            cur_up = cur.upper()
            if cur_up == el.get("currency"):
                if el.get('saleRate') and el.get('purchaseRate'):
                    my_dic[cur_up] = {'sale': el.get('saleRate'), 'purchase': el.get('purchaseRate')}
                else:
                    my_dic[cur_up] = {'sale NB': el.get('saleRateNB'), 'purchase NB': el.get('purchaseRateNB')}

    my_json[my_date] = my_dic
    return my_json


async def main(index_day, new_currency):
    d = datetime.now() - timedelta(days=int(index_day))
    shift = d.strftime("%d.%m.%Y")
    url = f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}'
    try:
        response = await parser_response(url, new_currency)
        return response
    except aiohttp.ClientConnectorError as err:
        print(f'Connection error: {url}', str(err))


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    days = int(sys.argv[1])
    add_currencies = list(sys.argv[2:])
    if days > 10:
        days = 10
    for day in range(days, 0, -1):
        r = asyncio.run(main(day, add_currencies))
        print(r)
