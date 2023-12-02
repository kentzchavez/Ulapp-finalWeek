from datetime import datetime, timedelta
import requests
import pytz

def get_yesterday_data(api_key, city):
    try:
        # Fetch yesterday's date
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        base_url = "http://api.weatherapi.com/v1/history.json"
        params = {
            'key': api_key,
            'q': city,
            'dt': yesterday,
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract yesterday's hourly forecast data
        hourly_forecast = data['forecast']['forecastday'][0]['hour']

        return hourly_forecast

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred while fetching yesterday's data: {e}")
        print(f"Response content: {response.content}")
        return []

    except Exception as e:
        print(f"Error fetching yesterday's weather data: {e}")
        return []


def get_weather_data(api_key, city):
    try:
        # Fetch today's and tomorrow's data
        base_url = "http://api.weatherapi.com/v1/forecast.json"
        params = {
            'key': api_key,
            'q': city,
            'days': 2,  # Fetch data for today and tomorrow
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Print the entire response content for debugging
        print(f"Response content: {data}")

        # Extract UV index
        uv_index = data['current']['uv'] if 'current' in data and 'uv' in data['current'] else "N/A"

        # Fetch yesterday's hourly data
        yesterday_data = get_yesterday_data(api_key, city)

        # Extract today's and tomorrow's hourly forecast data
        hourly_forecast_today = data['forecast']['forecastday'][0]['hour']
        hourly_forecast_tomorrow = data['forecast']['forecastday'][1]['hour']

        # Concatenate yesterday's, today's, and tomorrow's hourly data
        hourly_forecast = yesterday_data + hourly_forecast_today + hourly_forecast_tomorrow

        # Extract temperature and chance of rain for each hour
        hourly_data = [{'time': datetime.strptime(hour['time'], '%Y-%m-%d %H:%M').strftime('%I%p').lstrip('0'),
                        'temp_c': int(hour['temp_c']),
                        'chance_of_rain': hour['chance_of_rain']}
                       for hour in hourly_forecast]

        # Use sunrise-sunset.org to get sunrise and sunset times
        sunrise_sunset_url = f"https://api.sunrise-sunset.org/json?lat={data['location']['lat']}&lng={data['location']['lon']}&formatted=0"
        sunrise_sunset_response = requests.get(sunrise_sunset_url)
        sunrise_sunset_data = sunrise_sunset_response.json()

        # Convert sunrise and sunset times to Philippine local time
        ph_timezone = pytz.timezone('Asia/Manila')
        sunrise_utc = datetime.fromisoformat(sunrise_sunset_data['results']['sunrise'])
        sunset_utc = datetime.fromisoformat(sunrise_sunset_data['results']['sunset'])
        sunrise_ph = sunrise_utc.astimezone(ph_timezone).strftime('%I:%M%p')
        sunset_ph = sunset_utc.astimezone(ph_timezone).strftime('%I:%M%p')

        return {
            'uv_index': uv_index,
            'hourly_forecast': hourly_data,
            'sunrise': sunrise_ph,
            'sunset': sunset_ph
        }

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        print(f"Response content: {response.content}")
        return {
            'uv_index': "N/A",
            'hourly_forecast': [],
            'sunrise': "N/A",
            'sunset': "N/A"
        }
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return {
            'uv_index': "N/A",
            'hourly_forecast': [],
            'sunrise': "N/A",
            'sunset': "N/A"
        }
