import os
import importlib.resources
import pandas as pd

CSV_URL = "https://raw.githubusercontent.com/Bonitabueno/matjip_fairy/main/matjip_fairy_restaurants_info.csv"

def load_restaurant_data():
    df = pd.read_csv(CSV_URL)
    df.fillna("", inplace=True)
    return df