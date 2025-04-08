import os
import requests

def get_data(event, context):
    alpha_key = os.getenv("ALPHA_KEY")
    url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=EUR&to_symbol=INR&apikey={alpha_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        response_json = response.json()
        # Extracting the most recent data
        latest_date = list(response_json["Time Series FX (Daily)"].keys())[0]
        fx_data = response_json["Time Series FX (Daily)"][latest_date]
        fx_open = fx_data["1. open"]
        fx_high = fx_data["2. high"]
        fx_low = fx_data["3. low"]
        fx_close = fx_data["4. close"]
        return [latest_date, fx_open, fx_high, fx_low, fx_close]
    else:
        print("Error fetching data. Status code:", response.status_code)