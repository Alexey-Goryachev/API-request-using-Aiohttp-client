from datetime import datetime, timedelta
import json
import platform
import sys

import aiohttp
import asyncio


#функция получения json данных за конкретную дату 
async def fetch_data(session, date):
    url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={date}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error status: {response.status} for {url}")
    except aiohttp.ClientConnectorError as err:
                print(f'Connection error: {url}', str(err))

# функция обработки данных по курсам EUR и USD и дополнительных валют
async def get_exchange(response, additional_currencies=[]):
    exchange_data = {}
    additional_currencies = list(map(str.upper, sys.argv[2:]))
    try:
        for currency_code in ['EUR', 'USD'] + additional_currencies:
            exchange_rate, *_ = list(filter(lambda el: el['currency'] == currency_code, response['exchangeRate']))
            exchange_data[currency_code] = {'sale': exchange_rate['saleRateNB'], 'purchase': exchange_rate['purchaseRateNB']}
        data = {response['date']: exchange_data}        
    except ValueError:
        print('Additional currencies not found, please specify the data and repeat the request')
        for currency_code in ['EUR', 'USD']:
            exchange_rate, *_ = list(filter(lambda el: el['currency'] == currency_code, response['exchangeRate']))
            exchange_data[currency_code] = {'sale': exchange_rate['saleRateNB'], 'purchase': exchange_rate['purchaseRateNB']}
        data = {response['date']: exchange_data}                        
    return data             

#Основная функция выполнения запросов
async def main():
    results = []
    async with aiohttp.ClientSession() as session:   
        tasks = [] 
        for day  in range(1, int(sys.argv[1]) + 1):
            date = datetime.now() - timedelta(days=day)
            formatted_date = date.strftime("%d.%m.%Y")
            tasks.append(fetch_data(session, formatted_date))
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        for response in responses:
            try:
                data = await get_exchange(response)
                results.append(data)
            except TypeError:
                        pass
    return results

#функция обработки количества дней для получения запроса
def days_request():
    if len(sys.argv) < 2:
        print("Please provide the number of days as an argument.")
        sys.exit(1)
    try:
        days = int(sys.argv[1])
        if days > 10:
            print("The number of days cannot exceed 10.")
            sys.exit(1)
    except ValueError:
        print("Invalid argument. Please provide a valid number of days.")
        sys.exit(1)

    
if __name__ == "__main__":
    days_request()
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    r = asyncio.run(main())
    print(json.dumps(r, indent=2))

