import os
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')


def fetch_weather(city: str):
    if not OPENWEATHER_API_KEY:
        return None, "Missing OPENWEATHER_API_KEY environment variable. Set OPENWEATHER_API_KEY in your environment."

    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'units': 'metric',
        'appid': OPENWEATHER_API_KEY
    }

    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        return None, f"OpenWeather error {response.status_code}: {response.text}"

    data = response.json()
    main = data.get('main', {})
    weather = data.get('weather', [{}])[0]

    result = {
        'city': data.get('name'),
        'country': data.get('sys', {}).get('country'),
        'temperature_celsius': main.get('temp'),
        'temperature_feels_like_celsius': main.get('feels_like'),
        'temperature_min_celsius': main.get('temp_min'),
        'temperature_max_celsius': main.get('temp_max'),
        'humidity_percent': main.get('humidity'),
        'pressure_hPa': main.get('pressure'),
        'weather_main': weather.get('main'),
        'weather_description': weather.get('description'),
        'wind_speed_mps': data.get('wind', {}).get('speed'),
        'clouds_percent': data.get('clouds', {}).get('all')
    }
    return result, None


@app.route('/weather', methods=['GET'])
def weather_query():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'Query parameter city is required, e.g. /weather?city=London'}), 400

    weather, error = fetch_weather(city)
    if error:
        return jsonify({'error': error}), 500

    return jsonify(weather)


@app.route('/weather/<city>', methods=['GET'])
def weather_city(city):
    weather, error = fetch_weather(city)
    if error:
        return jsonify({'error': error}), 500

    return jsonify(weather)


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    error_message = None
    city = ''

    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        if city:
            weather_data, error_message = fetch_weather(city)

    return render_template('index.html', weather=weather_data, error=error_message, city=city)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
