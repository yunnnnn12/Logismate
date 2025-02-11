import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import random

# FastAPI 서버 주소
API_URL = "http://127.0.0.1:8000/add/forwarder/"

# Chrome 웹 드라이버 설정
options = Options()
options.add_argument('--headless')  # 브라우저 창 없이 실행
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 웹 페이지 열기
url = "https://www.forwarder.kr/biz/index.php?co_type=포워더"
driver.get(url)
time.sleep(1)

# 모든 회사 이름을 저장할 리스트
all_companies = set()  # 중복 방지

# '더보기' 버튼을 계속 클릭하여 모든 데이터를 로딩
while True:
    try:
        load_more_button = driver.find_element(By.XPATH, "//button[@class='load-more-btn']")
        load_more_button.click()
        time.sleep(1)  # 버튼 클릭 후 대기
        print("더보기 버튼 클릭하여 페이지 로드 완료")
    except:
        print("더보기 버튼 없음, 데이터 크롤링 완료")
        break  # 버튼이 없으면 종료

# 회사 이름 크롤링
companies = driver.find_elements(By.CLASS_NAME, "company-name")
for company in companies:
    company_name = company.text.strip()
    if company_name and company_name not in all_companies:
        all_companies.add(company_name)

# 나머지 필드 설정 (임의로 랜덤 값 할당)
transport_modes = ["해상", "항공", "철도", "트럭"]
additional_services = ["창고보관", "화물포장", "물류관리", "운송추적"]
insurance_types = ["기본 운송 보험", "전위험 보험"]
trade_terms = ["FOB", "CIF", "DAP"]
special_requirements = ["냉동 컨테이너", "위험물 취급", "특별 포장"]

# 크롤링된 데이터 FastAPI로 전송
for company in all_companies:
    forwarder_data = {
        "name": company,
        "transport_modes": random.sample(transport_modes, random.randint(1, len(transport_modes))),
        "additional_services": random.sample(additional_services, random.randint(1, len(additional_services))),
        "insurance_types": random.sample(insurance_types, random.randint(1, len(insurance_types))),
        "trade_terms": random.sample(trade_terms, random.randint(1, len(trade_terms))),
        "special_requirements": random.sample(special_requirements, random.randint(1, len(special_requirements)))
    }

    # FastAPI 서버로 POST 요청 전송
    response = requests.post(API_URL, json=forwarder_data)
    print(f"회사명: {company}, 응답: {response.json()}")

# 크롬 드라이버 종료
driver.quit()
