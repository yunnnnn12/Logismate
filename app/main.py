from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, get_mydb, connect
from app.schema import ForwarderCreate, CargoResponse, ETAResponse
import httpx, asyncio, websockets, json, requests
from typing import List, Dict
from eta_predict import calculate_eta
from requests.exceptions import Timeout, RequestException

from app.crud import addForwarder

app = FastAPI()

AIS_API_URL = "wss://stream.aisstream.io/v0/stream"
API_KEY = "0568f03934d78338bc2de3d206c85d312343d9e6"

@app.on_event("startup")
def startup_event():
    conn = connect()
    init_db(conn)

@app.post("/add/forwarder/")  # forwarder 이름 추가
def add_forwarder(forwarder: ForwarderCreate, conn=Depends(get_mydb)):
    return addForwarder(conn, forwarder)

async def get_coordinates(city: str) -> Dict[str, float]:
   base_url = "http://api.openweathermap.org/data/2.5/weather"
   params = { 
       "q": city,
       "appid": "0949e68d077b1657050f398746671c51",
       "units": "metric"
    }

   async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params)
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch weather data")
            
            data = response.json()

            if "coord" not in data:
                raise HTTPException(status_code=400, detail="Invalid city name or missing coordinate data")
            print(data["coord"]["lat"])

            return {
                "latitude": data["coord"]["lat"],
                "longitude": data["coord"]["lon"]
            }

# NavigationalStatus를 한국어로 매핑
def navigational_status_to_korean(status_code: int) -> str:
    status_map = {
        0: "엔진을 사용하여 항해 중",
        1: "정박 중",
        2: "명령을 받지 않음",
        3: "운항 제한",
        4: "흘수 제한",
        5: "계류 중",
        6: "좌초",
        7: "어업 중",
        8: "항해 중",
        9: "향후 사용 예정"
    }
    return status_map.get(status_code, "알 수 없는 상태")

# API 엔드포인트 설정
async def fetch_data_from_external_api(latitude: float, longitude: float) -> Dict:
    retries = 3
    for _ in range(retries):
        try:
            async with websockets.connect(AIS_API_URL) as websocket:
                bounding_boxes = [[[latitude - 0.1, longitude - 0.1], [latitude + 0.1, longitude + 0.1]],  # 서울 및 경기 지역
    [[latitude - 0.2, longitude - 0.2], [latitude + 0.2, longitude + 0.2]],  # 서울 및 인천, 경기도 일부
    [[latitude - 0.3, longitude - 0.3], [latitude + 0.3, longitude + 0.3]],  # 서울 및 더 넓은 범위
    [[latitude - 0.05, longitude - 0.05], [latitude + 0.05, longitude + 0.05]]] # 서울 및 수도권(선박의 출발지 경도 넣기->이거는 경도 가져오는 api(weatheropenmap)써야하나) #lat, lon 
                       # 부산 #여기에 mmsi정보 넣기 , 출발지

                subscription_message = {
                    "APIKey": API_KEY,
                    "BoundingBoxes": bounding_boxes
                }

                await websocket.send(json.dumps(subscription_message))
                print("Subscription message sent!")

                response = await websocket.recv()
                print(f"Raw response received: {response}")

                # 수신된 데이터가 문자열일 가능성이 있으므로 확인
                try:
                    data = json.loads(response)
                    print("Parsed data:", data)
                    return data
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    raise Exception("데이터를 JSON으로 파싱하는 데 실패했습니다.")
        except Exception as e:
            print(f"API 요청 중 오류 발생: {e}")
    raise Exception("여러 번의 재시도 후에도 데이터를 가져오지 못했습니다.")

# API 엔드포인트 설정
@app.get("/fetch-cargo-data", response_model=List[CargoResponse]) #mmsi를 받기, 출발지 경도위도 받기
async def get_cargo_data(city: str):
    #일단 먼저 city의 경도 위도 뽑아내는 api가져오기 그래서 ais api호출하기
    try:
        coords = await get_coordinates(city)
        data = await fetch_data_from_external_api(coords["latitude"], coords["longitude"])  # 비동기 함수 호출

        if "error" in data:
            return [{"ship_mmsi": "error", "location": {}}]  # 에러 발생 시 빈 데이터 반환

        # 외부 API에서 받은 데이터를 화물 응답 형식으로 변환
        filtered_ships = [
            {
                "ship_mmsi": ship["MMSI"],
                "ship_name": ship.get("ShipName", "Unknown").strip(),
                "location": {
                    "latitude": ship["latitude"],
                    "longitude": ship["longitude"]
                },
                "navigational_status": navigational_status_to_korean(ship.get("NavigationalStatus", "Unknown"))
            }
            for ship in data.get("ships", [])
            #if str(ship.get("MMSI")) == mmsi
        ]

        return filtered_ships if filtered_ships else [{"message": "No matching ship found"}]


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# 모델 리턴값 전해주는 api
@app.get("/get/eta/{departure}/{arrival}/{departure_time}",response_model=ETAResponse)
async def get_eta(departure: str, arrival: str, departure_time: str):
    return calculate_eta(departure, arrival, departure_time)


