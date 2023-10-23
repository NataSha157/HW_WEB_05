import sys
from datetime import datetime, timedelta

import httpx
import asyncio
import platform


class HttpError(Exception):
    pass


async def request(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            raise HttpError(f"Error status: {r.status_code} for {url}")


def parser_response(my_data: dict, currencies_add: list = None) -> dict:
    currencies_base = ['USD', 'EUR']
    currencies = currencies_base + currencies_add
    my_dates = my_data.get('date')
    my_json = {}
    my_dic = {}
    for el in my_data.get('exchangeRate'):
        for cur in currencies:
            if cur == el.get("currency"):
                if el.get('saleRate') and el.get('purchaseRate'):
                    my_dic[cur] = {'sale': el.get('saleRate'), 'purchase': el.get('purchaseRate')}
                else:
                    my_dic[cur] = {'sale NB': el.get('saleRateNB'), 'purchase NB': el.get('purchaseRateNB')}

    my_json[my_dates] = my_dic
    # print(my_json)
    return my_json


async def main(index_day):
    d = datetime.now() - timedelta(days=int(index_day))
    shift = d.strftime("%d.%m.%Y")
    try:
        response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')
        return response
    except HttpError as err:
        print(err)
        return None


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    days = int(sys.argv[1])
    add_currencies = list(sys.argv[2:])

    if days > 10:
        days = 10
    for day in range(days, 0, -1):
        r = asyncio.run(main(day))
        print(parser_response(r, add_currencies))
