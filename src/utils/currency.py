# src/utils/currency.py
import requests

def get_usd_to_kes():
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        data = response.json()
        return data['rates']['KES']
    except:
        return 150.0  # fallback rate