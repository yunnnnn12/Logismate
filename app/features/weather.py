import requests

# city = "Seoul"

def get_weather(city):
    apikey = "0949e68d077b1657050f398746671c51"
    lang = "kr"
    api = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={apikey}&lang={lang}&units=metric"
    
    result = requests.get(api)
    data = result.json()

    weather_map = {
        "Clear": 0,   # 맑음
        "Clouds": 1,  # 구름 많음
        "Rain": 2,    # 비
        "Drizzle": 3, # 가랑비
        "Thunderstorm": 4, # 천둥+번개
        "Snow": 5,    # 눈
        "Mist": 6,    # 엷은 안개
        "Fog": 7,     # 짙은 안개
        "Haze": 8     # 연무 (스모그)
    }
    weather_status = weather_map.get(data["weather"][0]["main"], 0)
    # wind_speed = data["wind"]["speed"]  # 풍속 (m/s)

    return {
        "weather_status": weather_status,
        # "wind_speed": wind_speed
    }

# print(get_weather(city))
