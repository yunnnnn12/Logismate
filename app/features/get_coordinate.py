import requests

def get_coordinates_openweather(city, api_key):
    # OpenWeather Geocoding API 엔드포인트
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    # 요청 파라미터 설정
    params = {
        'q': city,  # 도시명
        'appid': api_key  # 발급받은 API 키
    }
    
    # API 호출
    response = requests.get(base_url, params=params)
    
    # 응답이 성공적인지 확인
    if response.status_code == 200:
        data = response.json()
        lat = data['coord']['lat']  # 위도
        lon = data['coord']['lon']  # 경도
        return lat, lon
    else:
        print("Error: City not found or API limit reached")
        return None


