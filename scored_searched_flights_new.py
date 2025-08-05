from datetime import datetime
import json
from flight_to_csv import convert
import csv
import numpy as np
import pandas as pd
import xgboost as xgb
import os
#from currency_converter import CurrencyConverter

from format import format_search, check_if_empty

def score(data,mult, currency='EUR'):
    """Scores the searched flights data and returns a DataFrame with additional calculated fields.
    Args:
        data (dict): The flight search data.
        mult (int): Multiplier for distance.
        currency (str): Currency code for conversion.
    Returns:
        pd.DataFrame: A DataFrame containing the scored flight data.
        list: List of prices.
        list: List of city codes.
        list: List of dates.
        list: List of city codes.
    """
    if check_if_empty(data):
        return check_if_empty(data)
    searched_df, prices, codes, dates, city_codes = format_search(data, mult)
    #c = CurrencyConverter()
    if not os.path.isfile('user_searched_flights.csv'):
        searched_df.to_csv('user_searched_flights.csv')
    else: # else it exists so append without writing the header
        searched_df.to_csv('user_searched_flights.csv', mode='a', header=False)
    searched_df.drop('fare_category',axis=1, inplace=True)
    #searched_df.drop('bags_price',axis=1, inplace=True)
    #searched_df.drop('arrival_month',axis=1, inplace=True)
    searched_df['distance'] = searched_df['distance'] * mult
    n_days = []
    week= {
        'Monday':1,
        'Tuesday':2,
        'Wednesday':3,
        'Thursday':4,
        'Friday':5,
        'Saturday':6,
        'Sunday':7
    }
    
    searched_df['days'] = week.get(searched_df['day'].loc(), 1)
    searched_df['price_per_distance'] = searched_df['price'] / searched_df['distance']
    searched_df['weekend_score'] = searched_df['day'].apply(lambda x: 1 if x in ['Friday', 'Saturday'] else 0.5 if x in ['Thursday', 'Sunday'] else 0.1)
    searched_df['departure_daytime_score'] = searched_df['departure_hour'].apply(lambda x: 1 if 9 <= x <= 18 else 0.5)
    searched_df['arrival_daytime_score'] = searched_df['arrival_hour'].apply(lambda x: 1 if 10 <= x <= 21 else 0.5)
    searched_df['quality_per_duration'] = searched_df['quality'] / searched_df['duration']
    searched_df.drop('quality',axis=1, inplace=True)

    month_weights = {1: 0.5, 2: 0.6, 3: 0.7, 4: 0.9, 5: 0.8, 6: 1.2, 7: 1.6, 8: 1.3, 9: 0.7, 10: 1.0, 11: 0.6, 12: 1.0 }
    searched_df['departure_month'] = searched_df['departure_month'].apply(lambda x: month_weights.get(x, 1.0))
    searched_df['arrival_month'] = searched_df['arrival_month'].apply(lambda x: month_weights.get(x, 1.0))

    
    X = searched_df[['duration', 'departure_month',
       'departure_hour', 'arrival_month', 'arrival_hour', 'days',
       'weekend_score', 'departure_daytime_score',
       'arrival_daytime_score', 'quality_per_duration']]
    y = searched_df[['price_per_distance']]  
    model = xgb.XGBRegressor()
    best_model = xgb.XGBRegressor()
    #diff_model = xgb.XGBRegressor()
    model.load_model('model.json')
    best_model.load_model('best_model.json')
    #diff_model.load_model('diff_model.json')
    y_pred_model = model.predict(X)
    y_pred = best_model.predict(X)
    searched_df['XGBdifference'] = searched_df['price'].values - y_pred * searched_df['distance'].values
    searched_df['modeldifference'] = searched_df['price'].values - y_pred_model * searched_df['distance'].values
    #searched_df['orgdifference'] = searched_df['price'].values - y_pred_org
    #searched_df['noqualdifference'] = searched_df['price'].values - y_pred_noqual
    searched_df['XGBprice'] = y_pred * searched_df['distance'].values
    searched_df['modelprice'] = y_pred_model * searched_df['distance'].values
    #searched_df['orgprice'] = y_pred_org
    #searched_df['noqualprice'] = y_pred_noqual
    searched_df['avgdifference'] = (searched_df['XGBdifference'] + searched_df['modeldifference'])/2  # + searched_df['orgdifference'] + searched_df['noqualdifference']
    searched_df['avgprice'] = (searched_df['XGBprice'] + searched_df['modelprice'])/2 #  + y_pred_org + y_pred_noqual 
    #X_test = searched_df.iloc[:,[1,6,7,8,9,10,11,12,13]].values
    #diff_est = diff_model.predict(X_test)
    #searched_df['undervalued'] = diff_est
    searched_df['price'] = round(searched_df['price'], 2)
    searched_df['avgprice'] = round(searched_df['avgprice'], 2)
    searched_df['percentage'] = round((searched_df['avgprice']/searched_df['price'] *100)-100, 2)
    searched_df['hours'] = searched_df['duration'] // 3600
    searched_df['minutes'] = round((searched_df['duration'] / 3600 - searched_df['hours'])*60 , 0).astype('int64')
    searched_df['avgprice'] = round(searched_df['avgprice'], 2)
    searched_df['savings'] = round(searched_df['avgprice'] - searched_df['price'] ,2)
    searched_df['distance'] = round(searched_df['distance'], 0)
    #searched_df['x_price'] = searched_df['avgprice'].apply(lambda x: round(c.convert(x, 'EUR', currency), 2))


    under_over = []

    '''
    ranges_list = [(-INF, -50, 'Very Under'),()]
    
        for x in range_list:
            if x[0] < avgdifference < x[1]:
                under_over.append(x[2])
    '''

    for avgdifference in searched_df['avgdifference']:
        if avgdifference <= -50:
            under_over.append('Very Under')
        elif -50 < avgdifference <= -30:
            under_over.append('Under')
        elif -30 < avgdifference <= -10:
            under_over.append('Slightly Under')
        elif -10 < avgdifference <= 5:
            under_over.append('Expected')
        elif 5 < avgdifference <= 30:
            under_over.append('Slightly Over')
        elif 30 < avgdifference <= 50:
            under_over.append('Over')
        else:
            under_over.append('Very Over')
    searched_df['under_over'] = under_over
    # Specify the CSV file name
    #searched_df.to_csv('searched_flight_data.csv')
    return searched_df.sort_values('percentage'), prices, codes, dates, city_codes

'''
if __name__ == '__main__':
    file = open("flight_data.json")
    flight_data = json.load(file)
    print(score(flight_data))
    '''