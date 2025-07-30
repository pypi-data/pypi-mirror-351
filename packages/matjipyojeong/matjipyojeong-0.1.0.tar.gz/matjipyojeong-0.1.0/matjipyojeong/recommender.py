import re
import random
import pandas as pd
from .data_loader import load_restaurant_data
from .synonyms import find_synonym
from .exclude import exclude_keywords

# 음식점 데이터 로딩
df = load_restaurant_data()
df.fillna("", inplace=True)

def extract_keywords(query):
    city, district, neighborhood, restaurant_type, main_menu, station = None, None, None, None, None, None

    keywords = re.findall(r'\w+(?:에서|에|in|을|를|의|로|으로|이|가)?', query)
    keywords = [find_synonym(re.sub(r'(에서|에|in|을|를|의|로|으로|이|가)$', '', word)) for word in keywords]
    
    for keyword in keywords:
        keyword = keyword.strip().lower()

        if keyword in df['city'].str.lower().unique():
            city = keyword
        elif keyword in df['district'].str.lower().unique():
            district = keyword
        elif keyword in df['neighborhood'].str.lower().unique():
            neighborhood = keyword

        if keyword in df['restaurant_type'].str.lower().unique():
            restaurant_type = keyword
        if keyword in df['main_menu'].str.lower().unique():
            main_menu = keyword
        if keyword in df['station'].str.lower().unique():
            station = keyword

    return city, district, neighborhood, restaurant_type, main_menu, station


def search_restaurants(query):
    if any(word in query.lower() for word in exclude_keywords):
        return "정보가 없습니다."
        
    city, district, neighborhood, restaurant_type, main_menu, station = extract_keywords(query)

    if city or district or neighborhood or station:
        result = df.copy()

        if city:
            result = result[result['city'].str.lower().str.contains(city)]
        if district:
            result = result[result['district'].str.lower().str.contains(district)]
        if neighborhood:
            result = result[result['neighborhood'].str.lower().str.contains(neighborhood)]

        if restaurant_type:
            result = result[result['restaurant_type'].str.lower().str.contains(restaurant_type)]
        if main_menu:
            result = result[result['main_menu'].str.lower().str.contains(main_menu)]
        if station:
            result = result[result['station'].str.lower().str.contains(station)]

        if result.empty:
            return "정보가 없습니다."

        return result.sample(n=1).to_dict(orient="records")[0]
    else:
        return "지역 정보나 업종 정보가 없습니다."
