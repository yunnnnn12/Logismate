import requests

def get_wind_speed_kmh(lat, lng):
    # StormGlass API 요청
    response = requests.get(
        'https://api.stormglass.io/v2/weather/point',
        params={
            'lat': lat,
            'lng': lng,
            'params': 'windSpeed',
        },
        headers={
            'Authorization': 'c5b4ac30-e6da-11ef-806a-0242ac130003-c5b4ace4-e6da-11ef-806a-0242ac130003'
        }
    )

    # JSON 데이터 파싱
    json_data = response.json()

    # 가장 최근 시간의 풍속 데이터 추출
    latest_wind_speed_mps = json_data['hours'][0]['windSpeed']['noaa']
    
    # m/s에서 km/h로 변환 (1 m/s = 3.6 km/h)
    latest_wind_speed_kmh = latest_wind_speed_mps * 3.6

    return latest_wind_speed_kmh


