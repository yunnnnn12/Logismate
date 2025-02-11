import arrow
import requests

def get_wave_height(lat, lng):
    start = arrow.now().floor('day')
    
    end = arrow.now().ceil('day')

    response = requests.get(
        'https://api.stormglass.io/v2/weather/point',
        params={
            'lat': lat,
            'lng': lng,
            'params': 'waveHeight',  
            'start': start.to('UTC').timestamp(), 
            'end': end.to('UTC').timestamp()  
        },
        headers={
            'Authorization': 'c5b4ac30-e6da-11ef-806a-0242ac130003-c5b4ace4-e6da-11ef-806a-0242ac130003'
        }
    )

    json_data = response.json()

    if json_data.get('hours'):
        first_hour_data = json_data['hours'][0]
        wave_height = first_hour_data.get('waveHeight', {}).get('noaa', 0)  # Get wave height (use 0 if not available)
    else:
        wave_height = 0

    return wave_height

