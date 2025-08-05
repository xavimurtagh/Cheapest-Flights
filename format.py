import csv
import json
from datetime import datetime
import pandas as pd
from geopy.geocoders import Nominatim
import requests
import pandas as pd
from flask import  render_template, redirect

def format_search(data, mult = 1):
    rows = []
    prices = []
    curr = data['currency']
    codes = []
    dates = []
    city_codes = []
    if mult == 1:
        for entry in data['data']:
            departure_datetime = datetime.strptime(entry['local_departure'], "%Y-%m-%dT%H:%M:%S.%fZ")
            arrival_datetime = datetime.strptime(entry['local_arrival'], "%Y-%m-%dT%H:%M:%S.%fZ")

            try:
                row = {
                    'deep_link': entry['deep_link'],
                    'price': entry['conversion']['EUR'],
                    'countryFrom': entry['countryFrom']['name'],
                    'countryTo': entry['countryTo']['name'],
                    'cityFrom': entry['cityFrom'],
                    'cityTo': entry['cityTo'],
                    'cityCodeFrom': entry['cityCodeFrom'],
                    'cityCodeTo': entry['cityCodeTo'],
                    'people': 1,
                    'bags_price': entry['bags_price']['1'],
                    'quality': entry['quality'],
                    'duration': entry['duration']['total'],
                    'distance': entry['distance'],
                    'fare_category': entry['route'][0]['fare_category'],
                    'departure_month': departure_datetime.strftime("%m"),
                    'departure_hour': int(departure_datetime.hour) + int((departure_datetime.minute + 30) / 60),
                    'day': departure_datetime.strftime("%A"),
                    'arrival_month': arrival_datetime.strftime("%m"),
                    'arrival_hour': int(arrival_datetime.hour) + int((arrival_datetime.minute + 30) / 60)
                }
            except:
                row = {
                    'deep_link': entry['deep_link'],
                    'price': entry['conversion']['EUR'],
                    'countryFrom': entry['countryFrom']['name'],
                    'countryTo': entry['countryTo']['name'],
                    'cityFrom': entry['cityFrom'],
                    'cityTo': entry['cityTo'],
                    'cityCodeFrom': entry['cityCodeFrom'],
                    'cityCodeTo': entry['cityCodeTo'],
                    'people': 1,
                    'bags_price': 0,
                    'quality': entry['quality'],
                    'duration': entry['duration']['total'],
                    'distance': entry['distance'],
                    'fare_category': entry['route'][0]['fare_category'],
                    'departure_month': departure_datetime.strftime("%m"),
                    'departure_hour': int(departure_datetime.hour) + int((departure_datetime.minute + 30) / 60),
                    'day': departure_datetime.strftime("%A"),
                    'arrival_month': arrival_datetime.strftime("%m"),
                    'arrival_hour': int(arrival_datetime.hour) + int((arrival_datetime.minute + 30) / 60)
                }
            rows.append(row)
            try:
                prices.append(entry['conversion'][curr])
                codes.append(entry['countryTo']['code'])
                dates.append((departure_datetime, arrival_datetime))
                city_codes.append(entry['cityCodeTo'])
            except:
                prices.append(None)
                codes.append(None)
                dates.append(None)
                city_codes.append('None')

    else:
        for entry in data['data']:
            departure_datetime = datetime.strptime(entry['local_departure'], "%Y-%m-%dT%H:%M:%S.%fZ")
            arrival_datetime = datetime.strptime(entry['local_arrival'], "%Y-%m-%dT%H:%M:%S.%fZ")
            # Find the segment in 'route' where 'return' == 1
            return_segment = next((seg for seg in entry['route'] if seg.get('return') == 1), None)
            if return_segment:
                return_datetime = datetime.strptime(return_segment['local_departure'], "%Y-%m-%dT%H:%M:%S.%fZ")
                return_arrival_datetime = datetime.strptime(return_segment['local_arrival'], "%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                return_datetime = None
                return_arrival_datetime = None

            try:
                row = {
                    'deep_link': entry['deep_link'],
                    'price': entry['conversion']['EUR'],
                    'countryFrom': entry['countryFrom']['name'],
                    'countryTo': entry['countryTo']['name'],
                    'cityFrom': entry['cityFrom'],
                    'cityTo': entry['cityTo'],
                    'cityCodeFrom': entry['cityCodeFrom'],
                    'cityCodeTo': entry['cityCodeTo'],
                    'people': entry['conversion']['EUR'] / entry['fare']['adults'],
                    'bags_price': entry['bags_price']['1'],
                    'quality': entry['quality'],
                    'duration': entry['duration']['total'],
                    'distance': entry['distance'],
                    'fare_category': entry['route'][0]['fare_category'],
                    'departure_month': departure_datetime.strftime("%m"),
                    'departure_hour': int(departure_datetime.hour) + int((departure_datetime.minute + 30) / 60),
                    'day': departure_datetime.strftime("%A"),
                    'arrival_month': arrival_datetime.strftime("%m"),
                    'arrival_hour': int(arrival_datetime.hour) + int((arrival_datetime.minute + 30) / 60)
                }
            except:
                row = {
                    'deep_link': entry['deep_link'],
                    'price': entry['conversion']['EUR'],
                    'countryFrom': entry['countryFrom']['name'],
                    'countryTo': entry['countryTo']['name'],
                    'cityFrom': entry['cityFrom'],
                    'cityTo': entry['cityTo'],
                    'cityCodeFrom': entry['cityCodeFrom'],
                    'cityCodeTo': entry['cityCodeTo'],
                    'people': entry['conversion']['EUR'] / entry['fare']['adults'],
                    'bags_price': 0,
                    'quality': entry['quality'],
                    'duration': entry['duration']['total'],
                    'distance': entry['distance'],
                    'fare_category': entry['route'][0]['fare_category'],
                    'departure_month': departure_datetime.strftime("%m"),
                    'departure_hour': int(departure_datetime.hour) + int((departure_datetime.minute + 30) / 60),
                    'day': departure_datetime.strftime("%A"),
                    'arrival_month': arrival_datetime.strftime("%m"),
                    'arrival_hour': int(arrival_datetime.hour) + int((arrival_datetime.minute + 30) / 60)
                }
            rows.append(row)
            try:
                prices.append(float(entry['conversion'][curr]))
                codes.append(entry['countryTo']['code'])
                dates.append((departure_datetime, arrival_datetime, return_datetime, return_arrival_datetime))
                city_codes.append(entry['cityCodeTo'])
            except:
                prices.append(None)
                codes.append(None)
                dates.append(None)
                city_codes.append('None')

    df = pd.DataFrame.from_dict(rows)
    prices = pd.DataFrame.from_dict(prices).values
    codes = pd.DataFrame.from_dict(codes).values
    return df, prices, codes, dates, city_codes



#   FOR WHEN IT'S SEARCHED, RETURN THE FORMAT TO PUT IN HTML 
''' HEADERS:
       ['deep_link', 'price', 'countryFrom', 'countryTo', 'cityFrom', 'cityTo',
       'people', 'distance', 'departure_month', 'departure_hour', 'day',
       'arrival_hour', 'distance_per_duration', 'quality_per_duration',
       'XGBdifference', 'modeldifference', 'XGBprice', 'modelprice',
       'avgdifference', 'avgprice', 'undervalued', 'under_over'],
       dtype='object')'''
def format_results(data):
    dt1 = datetime.datetime(month=data['departure_month'], day = data['day'], hour=data['departure_hour'])
    #data['duration'] = 
    return None

def price(data):
    dt1 = datetime.datetime(month=data['departure_month'], day = data['day'], hour=data['departure_hour'])
    #data['duration'] = 
    return None

def check_if_empty(data):
    if data['_results'] == 0:
        return redirect('no_results.html')
    return None

def get_geonames_id(city, country=None):
    """
    Fetch the GeoNames ID for a given city (and optional country).
    """
    base_url = "http://api.geonames.org/searchJSON"
    params = {
        'q': city,
        'maxRows': 1,
        'username': 'xavimurtagh',
        'country': country  # Default to GB for UK
    }
    if country:
        params['country'] = country  # Use ISO country code if available

    response = requests.get(base_url, params=params)
    data = response.json()
    if data['totalResultsCount'] > 0:
        return data['geonames'][0]['geonameId']
    else:
        return None

geolocator = Nominatim(user_agent="cheapest-flights-app")

def get_lat_lon(place_name,country_code):
    try:
        location = geolocator.geocode(place_name, country_codes=country_code.lower())
        if location:
            return location.latitude, location.longitude
    except Exception:
        pass
    return None, None