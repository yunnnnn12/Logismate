from fastapi import FastAPI 
from datetime import datetime
from pydantic import BaseModel
from typing import Set, List, Dict, Optional


class ForwarderCreate(BaseModel):
    name: str
    transport_modes: Set[str]  #운송 모드
    additional_services: Set[str]  #추가 서비스
    insurance_types: Set[str]  #보험 종류
    trade_terms: Set[str]  #거래 조건
    special_requirements: Set[str]  #특별 요구 사항

class CargoResponse(BaseModel):
    ship_mmsi: str
    ship_name: Optional[str] = "Unknown"  # 기본값 설정
    location: dict
    navigational_status: Optional[str] = "Unknown"  # 기본값 설정


class ETAResponse(BaseModel):
    expected_arrival_time: datetime
    
    

