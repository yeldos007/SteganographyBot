import os
import dotenv
import requests
import random
from random import randint
dotenv.load_dotenv()
OWM_API_KEY = os.getenv("OWM_API_KEY")


# stickers = os.path.join(os.getcwd(), 'Python', 'sticker.webp')
# sti = open(stickers)

def get_stickers():
    n = random.randint(1,10)
    return f'stickers/AnimatedSticker{n}.tgs'
    
def get_random():
    data = requests.get('https://random.dog/woof.json').json()
    b = data['url']
    return b


def get_weather(city):
    api_key = OWM_API_KEY
    base_url = "http://api.openweathermap.org/data/2.5/weather"

    params = {
        'q' : city,
        'appid': api_key,
        'units': 'metric',
        'lang': 'ru'
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        main_weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity =  data['main']['humidity']

        return f"Погода в {city}: {main_weather}\n"\
               f"Температура: {temperature}°C\n" \
               f"Ощущается как: {feels_like}°C.\n" \
               f"Влажность: {humidity}%."
    
    except requests.exceptions.HTTPError as err:
        return f"Ошибка HTTP: {err}"
    except requests.exceptions.RequestException as err:
        return f"Ошибка соединения: {err}"
    except KeyError:
        return "Не удалось получить данные для этого города."
    


