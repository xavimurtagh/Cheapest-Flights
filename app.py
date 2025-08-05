import csv
import os
import pandas as pd
import requests
from flask import Flask, flash, redirect, render_template, request, send_from_directory, session, jsonify, abort
from flask_session import Session
import re
from datetime import datetime
from helper import apology
from scored_searched_flights_new import score
import pandas as pd
from collections import defaultdict
import requests
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

def slugify(value):
    value = str(value)
    value = value.lower()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    value = value.strip('-')
    return value

def remove_brackets(text):
    return re.sub(r'\s*\(.*?\)', '', text)

app.jinja_env.filters['slugify'] = slugify

# Tequila API endpoint and API key (replace with your own)
TEQUILA_API_ENDPOINT = "https://api.tequila.kiwi.com/v2/search"
TEQUILA_API_KEY = os.environ.get('TEQUILA_API_KEY')


@app.route('/', methods=['GET','POST'])
def search_flights():
    if request.method == "POST":
        # Get data from the request

        # Prepare the request parameters
        url = "https://api.tequila.kiwi.com/v2/search"
        headers = {
            "apikey": os.environ.get('TEQUILA_API_KEY'),
        }
        CURRENCY = request.form.get('currency')
        if request.form.get('search-type') == 'one-way':
            dist = 1
            limit = 500
        else:
            dist = 2
            limit = 1000
        try:
            params = {
                'fly_from': (request.form.get('origin').split('('))[-1].strip(')'),
                'fly_to': ','.join([part.split('(')[-1].strip(')') for part in (request.form.get('selected_destinations')).split(';')]),           #(request.form.get('selected-destinations-container').split('('))[-1].strip(')'),
                'date_from': datetime.strptime(request.form.get('departure-from'),("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'date_to': datetime.strptime(request.form.get('departure-to'),("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'return_from': datetime.strptime(request.form.get('return-from'),("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'return_to': datetime.strptime(request.form.get('return-to'),("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'nights_in_dst_from': request.form.get('nights-from'),
                'nights_in_dst_to': request.form.get('nights-to'),
                'curr': CURRENCY,
                'limit': limit,
                'enable_vi': 'true',
                'ret_from_diff_city': 'false',
                'max_stopovers': request.form.get('direct'),

            }
        except:
            params = {
                'fly_from': (request.form.get('origin').split('('))[-1].strip(')'),
                'fly_to': ','.join([part.split('(')[-1].strip(')') for part in (request.form.get('selected_destinations')).split(';')]),          #(request.form.get('selected-destinations-container').split('('))[-1].strip(')'),
                'date_from': datetime.strptime(request.form.get('departure-from'),("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'date_to': datetime.strptime(request.form.get('departure-to'),("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'nights_in_dst_from': request.form.get('nights-from'),
                'nights_in_dst_to': request.form.get('nights-to'),
                'curr': CURRENCY,
                'limit': limit,
                'enable_vi': 'true',
                'ret_from_diff_city': 'false',
                'max_stopovers': request.form.get('direct'),
            }

        #return jsonify(params)

        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json()
        except:
            apology('Your search filters didnt make sense please try again')
        
        try:
            flight_data, prices, country_codes, dates, city_codes = score(data,dist, CURRENCY)
        except:
            return render_template('no_results.html')
        #return jsonify(flight_data)

            # Pass the flight data to the template
        if dist == 1:
            return render_template('search_results_one_way.html', data=flight_data, CURR = CURRENCY, length = len(flight_data), prices = prices, country_codes=country_codes, dates=dates, city_codes=city_codes)
        return render_template('search_results.html', data=flight_data, CURR = CURRENCY, length = len(flight_data), prices = prices, country_codes=country_codes, dates=dates, city_codes=city_codes)

       #return redirect('/get_flight_data')


    else:
        return render_template("index.html")
    


@app.route('/advanced_search', methods=['GET','POST'])
def advanced_search_flights():
    if request.method == "POST":
        # Get data from the request

        # Prepare the request parameters
        url = "https://api.tequila.kiwi.com/v2/search"
        headers = {
            "apikey": os.environ.get('TEQUILA_API_KEY'),
        }
        CURRENCY = request.form.get('currency')
        if request.form.get('search-type') == 'one-way':
            dist = 1
            limit = 500
        else:
            dist = 2
            limit = 1000
        try:
            params = {
                'fly_from': (request.form.get('origin').split('('))[-1].strip(')'),
                'fly_to': (','.join([part.split('(')[-1].strip(')') for part in (request.form.get('selected_destinations')).split(';')]) )| '',           #(request.form.get('selected-destinations-container').split('('))[-1].strip(')'),
                'date_from': datetime.strptime(request.form.get('departure-from'),("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'date_to': datetime.strptime(request.form.get('departure-to'),("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'return_from': datetime.strptime(request.form.get('return-from'),("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'return_to': datetime.strptime(request.form.get('return-to'),("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'nights_in_dst_from': request.form.get('nights-from'),
                'nights_in_dst_to': request.form.get('nights-to'),
                'curr': CURRENCY,
                'limit': limit,
                'ret_from_diff_city': request.form.get('ret_from_diff_city'),
                'ret_to_diff_city': request.form.get('ret_to_diff_city'),
                'max_stopovers': request.form.get('max_stopovers'),
                'max_fly_duration': request.form.get('max_fly_duration'),
                'selected_cabins': request.form.get('selected_cabins'),
                'adult_hold_bag': request.form.get('adult_hold_bag'),
                'adult_hand_bag': request.form.get('adult_hand_bag'),
                'fly_days': request.form.get('fly_days'),
                'ret_fly_days': request.form.get('ret_fly_days'),
                'only_working_days': request.form.get('only_working_days'),
                'only_weekends': request.form.get('only_weekends'),
                'price_from': request.form.get('price_from'),
                'price_to': request.form.get('price_to'),
                'dtime_from': request.form.get('dtime_from'),
                'dtime_to': request.form.get('dtime_to'),
                'atime_from': request.form.get('atime_from'),
                'atime_to': request.form.get('atime_to'),
                'stopover_from': request.form.get('stopover_from'),
                'stopover_to': request.form.get('stopover_to'),
                'max_sector_stopovers': request.form.get('max_sector_stopovers'),
                'conn_on_diff_airport': request.form.get('conn_on_diff_airport'),
                'ret_from_diff_airport': request.form.get('ret_from_diff_airport'),
                'ret_to_diff_airport': request.form.get('ret_to_diff_airport'),
                'ret_dtime_from': request.form.get('ret_dtime_from'),
                'ret_dtime_to': request.form.get('ret_dtime_to'),
                'ret_atime_from': request.form.get('ret_atime_from'),
                'ret_atime_to': request.form.get('ret_atime_to')
            }
        except:
            params = {
                'fly_from': (request.form.get('origin').split('('))[-1].strip(')'),
                'fly_to': ','.join([part.split('(')[-1].strip(')') for part in (request.form.get('selected_destinations')).split(';')]),          #(request.form.get('selected-destinations-container').split('('))[-1].strip(')'),
                'date_from': datetime.strptime(request.form.get('departure-from'),("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'date_to': datetime.strptime(request.form.get('departure-to'),("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'nights_in_dst_from': request.form.get('nights-from'),
                'nights_in_dst_to': request.form.get('nights-to'),
                'curr': CURRENCY,
                'limit': limit,
                'ret_from_diff_city': request.form.get('ret_from_diff_city'),
                'ret_to_diff_city': request.form.get('ret_to_diff_city'),
                'max_stopovers': request.form.get('max-stopovers'),
                'max_fly_duration': request.form.get('max-fly-duration'),
                'selected_cabins': request.form.get('selected_cabins'),
                'adult_hold_bag': request.form.get('adult_hold_bag'),
                'adult_hand_bag': request.form.get('adult_hand_bag'),
                'fly_days': request.form.get('fly_days'),
                'ret_fly_days': request.form.get('ret_fly_days'),
                'only_working_days': request.form.get('only_working_days'),
                'only_weekends': request.form.get('only_weekends'),
                'price_from': request.form.get('price_from'),
                'price_to': request.form.get('price_to'),
                'dtime_from': request.form.get('dtime_from'),
                'dtime_to': request.form.get('dtime_to'),
                'atime_from': request.form.get('atime_from'),
                'atime_to': request.form.get('atime_to'),
                'stopover_from': request.form.get('stopover_from'),
                'stopover_to': request.form.get('stopover_to'),
                'max_sector_stopovers': request.form.get('max_sector_stopovers'),
                'conn_on_diff_airport': request.form.get('conn_on_diff_airport'),
                'ret_from_diff_airport': request.form.get('ret_from_diff_airport'),
                'ret_to_diff_airport': request.form.get('ret_to_diff_airport')
            }

        # Make the API request to Tequila
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json()
        except:
            apology('Your search filters didnt make sense please try again')

        try:
            flight_data, prices, country_codes, dates, city_codes = score(data,dist,CURRENCY)

        except:
            return redirect('no_results.html')

        prices = [[round(float(p[0]),2)] for p in prices]
        #data['percentage'] = [float(p) for p in data['percentage']]

        # Pass the flight data to the template

        if dist == 1:
            return render_template('search_results_one_way.html', data=flight_data, CURR = CURRENCY, length = len(flight_data), prices = prices, country_codes=country_codes, dates=dates, city_codes=city_codes)
        return render_template('search_results.html', data=flight_data, CURR = CURRENCY, length = len(flight_data), prices = prices, country_codes=country_codes, dates=dates, city_codes=city_codes)

    else:
        return render_template("advanced_search.html")
    

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.template_filter('floatformat')
def floatformat(value, precision=0):
    try:
        return round(float(value), precision)
    except (ValueError, TypeError):
        return int(value)

@app.route('/destination_search', methods=['GET', 'POST'])
def destination_search():
    if request.method == 'POST':
        url = "https://api.tequila.kiwi.com/v2/search"
        headers = {
            "apikey": os.environ.get('TEQUILA_API_KEY'),
        }
        form = request.form
        CURRENCY = form.get('currency')
        search_type = form.get('search-type', 'one-way')
        if search_type == 'one-way':
            dist = 1
            limit = 600
        else:
            dist = 2
            limit = 1000
        try:
            params = {
                'fly_from': (form.get('origin', '').split('('))[-1].strip(')'),
                'fly_to': ','.join(form.getlist('destinations')),
                'date_from': datetime.strptime(form.get('departure-from'), ("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'date_to': datetime.strptime(form.get('departure-to'), ("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'nights_in_dst_from': form.get('nights-from'),
                'nights_in_dst_to': form.get('nights-to'),
                'curr': CURRENCY,
                'limit': limit,
                'ret_from_diff_city': 'false',
                'max_stopovers': request.form.get('direct'),
                }
        except:
            params = {
                'fly_from': (form.get('origin', '').split('('))[-1].strip(')'),
                'fly_to': ','.join(form.getlist('destinations')),
                'date_from': datetime.strptime(form.get('departure-from'), ("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'date_to': datetime.strptime(form.get('departure-to'), ("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'return_from': datetime.strptime(form.get('return-from'), ("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'return_to': datetime.strptime(form.get('return-to'), ("%Y-%m-%d")).strftime("%d/%m/%Y"),
                'nights_in_dst_from': form.get('nights-from'),
                'nights_in_dst_to': form.get('nights-to'),
                'curr': CURRENCY,
                'limit': limit,
                'ret_from_diff_city': 'false',
                'max_stopovers': request.form.get('direct'),
            }

        #return jsonify(params)

        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json()
        except:
            apology('Your search filters didnt make sense please try again')
        
        #return jsonify(data)

        try:
            flight_data, prices, country_codes, dates, city_codes = score(data,dist, CURRENCY)
        except:
            return render_template('no_results.html')

            # Pass the flight data to the template
        if dist == 1:
            return render_template('search_results_one_way.html', data=flight_data, CURR = CURRENCY, length = len(flight_data), prices = prices, country_codes=country_codes, dates=dates, city_codes=city_codes)
        return render_template('search_results.html', data=flight_data, CURR = CURRENCY, length = len(flight_data), prices = prices, country_codes=country_codes, dates=dates, city_codes=city_codes)
    else:
        destinations = []
        with open('final_destinations.csv', newline='', encoding='latin-1') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert all score fields to int
                for field in [
                    'food_score','nightlife_score','nature_score','weather_score','culture_score',
                    'safety_score','cost_score','transport_score','activities_score','history_score','under_radar_score'
                ]:
                    row[field] = int(row[field]) if row[field] else 0
                    #row[field].append(row['airport_code'])
                destinations.append(row)
        return render_template('dest_flight_search.html', destinations=destinations)

@app.route('/api/destinations/')
def api_destinations():
    destinations = []
    with open('final_destinations.csv', encoding='latin-1') as f:
        reader = csv.DictReader(f)
        for row in reader:
            destinations.append({
                'destination_name': row['destination_name'],
                'country': row['country'],
                'food_score': row['food_score'],
                'nightlife_score': row['nightlife_score'],
                'nature_score': row['nature_score'],
                'weather_score': row['weather_score'],
                'culture_score': row['culture_score'],
                'safety_score': row['safety_score'],
                'cost_score': row['cost_score'],
                'transport_score': row['transport_score'],
                'activities_score': row['activities_score'],
                'history_score': row['history_score'],
                'under_radar_score': row['under_radar_score'],
                'country_code': row['country_code'],
                'airport_code': row.get('airport_code', ''),
            })
    return jsonify(destinations)

@app.route('/api/search_airports/', methods=['POST'])
def api_search_airports():
    data = request.get_json()
    airport_codes = data.get('airport_codes', [])
    # You can process the airport_codes as needed here
    return jsonify({'airport_codes': airport_codes})



def get_monthly_weather(lat, lon):
    url = (
        "https://climate-api.open-meteo.com/v1/climate"
        f"?latitude={lat}&longitude={lon}"
        "&start_year=1991&end_year=2020"
        "&temperature_unit=celsius"
        "&precipitation_unit=mm"
        "&format=json"
        "&monthly=temperature_2m_mean,precipitation_sum"
    )
    resp = requests.get(url)
    data = resp.json()
    print(data)
    months = data['monthly']['time']
    temps = data['monthly']['temperature_2m_mean']
    rainfall = data['monthly']['precipitation_sum']
    return months, temps, rainfall

# Load the CSV data once at startup
destinations_df = pd.read_csv('final_destinations.csv', encoding='latin-1')

@app.route('/destinations')
def destinations():
    # Group by region and country
    countries = defaultdict(list)
    for _, row in destinations_df.iterrows():
        country = remove_brackets(row['country'])
        country_code = row['country_code'].upper()  # Ensure country code is uppercase
        destination_name = row['destination_name']
        airport_code = row.get('airport_code', '')
        countries[country].append((destination_name, country_code, airport_code))
    return render_template('all_destinations.html', countries=countries)



@app.route('/destinations/<country_code>/<airport_code>')
def destination(country_code, airport_code, destination_name = None):
    # Find the row for the requested destination (case-insensitive)
    row = destinations_df[destinations_df['airport_code'].str.lower() == airport_code.lower()]
    #row = row[row['country_code'].str.lower() == country_code.lower()]
    if row.empty:
        return render_template('unknown_destination_template.html', destination_name=airport_code)
    if len(row) > 1:
        return render_template(
            'multiple_destinations.html',
            destinations=row['destination_name'].tolist(),
            country_code=country_code,
            airport_code=airport_code
        )
    data = row.iloc[0].to_dict()

    #lat, lon = get_lat_lon(data['destination_name'], country_code)
    #data['latitude'] = lat or ''
    #data['longitude'] = lon or ''

    # Example: add extra fields for the template if needed
    data['destination_name'] = data.get('destination_name', '')
    data['hero_image'] = data.get('hero_image', '/static/default.jpg')
    data['country'] = data.get('country', '')
    data['destination_tagline'] = data.get('destination_tagline', '')
    data['destination_description'] = data.get('destination_description', 'No description available.')
    data['scores'] = {
        'food': data.get('food_score', 0),
        'nightlife': data.get('nightlife_score', 0),
        'culture': data.get('culture_score', 0),
        'safety': data.get('safety_score', 0),
        'transport': data.get('transport_score', 0),
        'cost': data.get('cost_score', 0),
        'weather': data.get('weather_score', 0),
        'nature': data.get('nature_score', 0),
        'activities': data.get('activities_score', 0),
        'history': data.get('history_score', 0),
        'under_radar': data.get('under_radar_score', 0)
    }
    data['costs'] = {
        'accommodation': data.get('accommodation_cost', 0),
        'food': data.get('food_cost', 0),
        'transport': data.get('transport_cost', 0),
        'activities': data.get('activities_cost', 0)
    }
    data['temperature_data'] = [data.get(f'{month}_temp', 0) for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']]
    data['rainfall_data'] = [data.get(f'{month}_rain', 0) for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']]
    data['attractions'] = []
    for i in range(1, 7):
        data['attractions'].append({
            'name': data.get(f'nearby_place_{i}', ''),
            'distance': data.get(f'nearby_distance_{i}', 0),
            'type': data.get(f'nearby_type_{i}', '')
        })
    data['best_time_to_visit'] = data.get('best_time', 'N/A')
    data['population'] = data.get('population', 0)
    data['language'] = data.get('language', 'N/A')
    data['currency'] = data.get('currency', 'N/A')
    data['timezone'] = data.get('timezone', 'N/A')
    data['tips'] = []
    for i in range(1, 6):
        tip = data.get(f'tip_{i}', '')
        if tip:
            data['tips'].append(tip)
    data['country_code'] = country_code.upper()
    data['geonames_id'] = int(data.get('geonames_id', 0))
    data['country_name'] = remove_brackets(data.get('country', ''))
    data['photos'] = [data.get(f'photo{i}', '') for i in range(2, 8)]
    return render_template('destination_template.html', **data)


@app.route('/destinations/<country_code>/<airport_code>/<destination_name>')
def destination_with_name(country_code, airport_code, destination_name):
    # Find the row matching both airport_code and destination_name (case-insensitive)
    row = destinations_df[
        (destinations_df['airport_code'].str.lower() == airport_code.lower()) &
        (destinations_df['destination_name'].str.lower() == destination_name.replace('-', ' ').lower())
    ]
    if row.empty:
        return render_template('unknown_destination_template.html', destination_name=destination_name)
    data = row.iloc[0].to_dict()

    data['destination_name'] = data.get('destination_name', '')
    data['hero_image'] = data.get('hero_image', '/static/default.jpg')
    data['country'] = data.get('country', '')
    data['destination_tagline'] = data.get('destination_tagline', '')
    data['destination_description'] = data.get('destination_description', 'No description available.')
    data['scores'] = {
        'food': data.get('food_score', 0),
        'nightlife': data.get('nightlife_score', 0),
        'culture': data.get('culture_score', 0),
        'safety': data.get('safety_score', 0),
        'transport': data.get('transport_score', 0),
        'cost': data.get('cost_score', 0),
        'weather': data.get('weather_score', 0),
        'nature': data.get('nature_score', 0),
        'activities': data.get('activities_score', 0),
        'history': data.get('history_score', 0),
        'under_radar': data.get('under_radar_score', 0)
    }
    data['costs'] = {
        'accommodation': data.get('accommodation_cost', 0),
        'food': data.get('food_cost', 0),
        'transport': data.get('transport_cost', 0),
        'activities': data.get('activities_cost', 0)
    }
    data['temperature_data'] = [data.get(f'{month}_temp', 0) for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']]
    data['rainfall_data'] = [data.get(f'{month}_rain', 0) for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']]
    data['attractions'] = []
    for i in range(1, 7):
        data['attractions'].append({
            'name': data.get(f'nearby_place_{i}', ''),
            'distance': data.get(f'nearby_distance_{i}', 0),
            'type': data.get(f'nearby_type_{i}', '')
        })
    data['best_time_to_visit'] = data.get('best_time', 'N/A')
    data['population'] = data.get('population', 0)
    data['language'] = data.get('language', 'N/A')
    data['currency'] = data.get('currency', 'N/A')
    data['timezone'] = data.get('timezone', 'N/A')
    data['tips'] = []
    for i in range(1, 6):
        tip = data.get(f'tip_{i}', '')
        if tip:
            data['tips'].append(tip)
    data['country_code'] = country_code.upper()
    data['geonames_id'] = int(data.get('geonames_id', 0))
    data['country_name'] = remove_brackets(data.get('country', ''))
    data['photos'] = [data.get(f'photo{i}', '') for i in range(2, 8)]
    return render_template('destination_template.html', **data)



@app.errorhandler(500)
@app.errorhandler(404)
def internal_server_error(e: Exception) -> str:
    return apology("Hmmm that's not meant to happen, please check you've filled everything in correctly and try again.", 500)

@app.route('/faq')
def faq():
    return render_template("faq.html")    

@app.route('/big_trip')
def big_trip():
    return render_template("big_trip.html")   

@app.route('/holiday_builder')
def holiday_builder():
    return render_template("holiday_builder.html")   


if __name__ == '__main__':
    app.run(debug=True)



'''
        To DO:
    1.  Round prices to 2 decimal points
    2.  Make algorithm do it based on percentage of price 
    3.  Score this 
    4.  Make sure cant pick date before today
    5.  Get more flights in
    6.  Get all stats in
    7.  Add searched flights to dataset
    8.  Option for days to fly on eg just weekends


'''
