import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '').strip()


def fetch_weather(city: str):
    if not OPENWEATHER_API_KEY:
        return None, "Missing OPENWEATHER_API_KEY environment variable."

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


@app.route('/')
def hello_world():
    return jsonify({'message': 'Weather app is running', 'usage': '/weather?city=<city>'})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
