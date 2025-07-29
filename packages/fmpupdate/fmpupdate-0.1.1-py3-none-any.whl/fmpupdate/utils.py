import requests
import pandas as pd

def get_top_gainers(api_key):
    top_gainers = requests.get(f'https://financialmodelingprep.com/stable/biggest-gainers?apikey={api_key}').json()
    df = pd.DataFrame(top_gainers)
    return df

def get_top_losers(api_key):
    top_losers = requests.get(f'https://financialmodelingprep.com/stable/biggest-gainers?apikey={api_key}').json()
    df = pd.DataFrame(top_losers)
    return df