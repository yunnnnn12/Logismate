import requests
from features.weather import get_weather
from features.wind_speed import get_wind_speed_kmh
from features.wave_height import get_wave_height
from features.get_coordinate import get_coordinates_openweather
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
# 스프링 한테서 출발지,도착지 스트링으로 받기 , "출발 시간"도-> 경도 위도 뽑아내서 정보 넣기 
# 날씨, 풍속, 파도 높이
# 여기서 출,도착지 경도/위도 가져와야함


def calculate_eta(departure, arrival, departure_time):

    distance = ""


    api_key = '0949e68d077b1657050f398746671c51'
    dep_lat, dep_lng = get_coordinates_openweather("Seoul", api_key)
    arr_lat, arr_lng = get_coordinates_openweather("Seoul", api_key)


    # 기존 데이터셋
    data = {
        'departure_time': [8, 10, 12, 6, 14, 16, 18, 7, 9, 11], 
        'departure_weather': [0, 1, 2, 0, 1, 2, 1, 0, 2, 1],
        'departure_wind_speed': [5, 10, 15, 8, 12, 20, 10, 5, 18, 11],
        'departure_wave_height': [0.5, 1.0, 1.2, 0.8, 0.7, 1.5, 1.3, 0.6, 1.4, 1.1],
        'arrival_weather': [1, 0, 2, 1, 2, 0, 1, 2, 0, 1],
        'arrival_wind_speed': [7, 5, 12, 8, 15, 6, 10, 14, 9, 13],
        'arrival_wave_height': [0.6, 0.4, 1.0, 0.7, 1.3, 0.5, 1.1, 1.2, 0.8, 1.0],
        'distance': [300, 450, 500, 350, 400, 600, 550, 320, 580, 460],
        'ETA': [4.5, 6.5, 7.8, 5.2, 6.0, 8.3, 7.5, 5.0, 8.0, 6.8]
    }


    df = pd.DataFrame(data)

    # X와 y 설정
    X = df[['departure_weather', 'departure_wind_speed', 'departure_wave_height',
            'arrival_weather', 'arrival_wind_speed', 'arrival_wave_height', 'distance']] #입력 데이터
    y = df['ETA'] #타겟 값

    # 모델 학습을 위한 훈련 데이터와 테스트 데이터 분리
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 선형 회귀 모델 생성 및 학습
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 테스트 데이터 예측
    y_pred = model.predict(X_test)

    # 6. 모델 성능 평가 (MAE - 평균 절대 오차)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Mean Absolute Error: {mae:.2f} 시간")

    # 새로운 데이터
    departure_time = departure_time
    distance = distance 
    departure_weather = get_weather(departure)
    departure_wind_speed = get_wind_speed_kmh(dep_lat, dep_lng)
    departure_wave_height = get_wave_height(dep_lat, dep_lng)
    arrival_weather = get_weather(arrival)
    arrival_wind_speed = get_wind_speed_kmh(arr_lat, arr_lng)
    arrival_wave_height = get_wave_height(arr_lat, arr_lng)

    '''departure_time = 10
    distance = 10 
    departure_weather = 3
    departure_wind_speed = 10
    departure_wave_height = 10
    arrival_weather = 3
    arrival_wind_speed = 10
    arrival_wave_height = 10'''


    # 새로운 데이터프레임 추가
    new_data = pd.DataFrame({
        'departure_time': [departure_time],
        'departure_weather' : [departure_weather],
        'departure_wind_speed' : [departure_wind_speed],
        'departure_wave_height' : [departure_wave_height],
        'arrival_weather' : [arrival_weather],
        'arrival_wind_speed' : [arrival_wind_speed],
        'arrival_wave_height' : [arrival_wave_height],
        'distance' : [distance]
    })

    # 새로운 데이터를 기존 데이터에 추가하고 다시 학습
    df = pd.concat([df, new_data], ignore_index=True)

    # 새로운 데이터에 대해 예측
    X_new = df[['departure_weather', 'departure_wind_speed', 'departure_wave_height',
                'arrival_weather', 'arrival_wind_speed', 'arrival_wave_height', 'distance']]

    # 새로운 데이터에 대한 ETA 예측
    y_new = model.predict(X_new)

    # ETA 계산 (departure_time + 예측된 ETA)
    df['expected_arrival_time'] = df['departure_time'] + y_new

    # 24시간을 넘지 않도록 처리
    df['expected_arrival_time'] = df['expected_arrival_time'].apply(lambda x: x if x < 24 else x - 24)

    # ETA 값을 시간 형식으로 변환하는 함수
    def format_eta_to_time(eta):
        hours = int(eta)  # 시간 부분 (정수 부분)
        minutes = round((eta - hours) * 60)  # 분 부분 (소수 부분을 60으로 곱해서 분으로 변환)
        
        # 시간과 분을 2자리로 맞추어 반환 (01:05 형식으로)
        return f"{hours:02d}:{minutes:02d}"

    # expected_arrival_time을 HH:MM 형식으로 변환하여 프론트에 반환할 수 있도록 처리
    df['formatted_expected_arrival_time'] = df['expected_arrival_time'].apply(format_eta_to_time)

    # 결과 출력
    return df['formatted_expected_arrival_time']