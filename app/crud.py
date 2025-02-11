from fastapi import FastAPI, HTTPException, status, Depends
from app.database import connect
from mysql.connector.connection import MySQLConnection
from mysql.connector import IntegrityError
from app.schema import ForwarderCreate
conn = connect()


def addForwarder(conn : MySQLConnection, forwarder: ForwarderCreate):
    cursor = conn.cursor()

    try:
        add_forwarder = """
        INSERT INTO forwarder (name, transport_modes, additional_services, insurance_types, trade_terms, special_requirements)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        
        # transportModes, additionalServices, insuranceType, tradeTerms, specialRequirements은 세트이므로
        # 각 세트를 문자열로 변환하여 저장합니다.
        transport_modes_str = ', '.join(forwarder.transport_modes)
        additional_services_str = ', '.join(forwarder.additional_services)
        insurance_types_str = ', '.join(forwarder.insurance_types)
        trade_terms_str = ', '.join(forwarder.trade_terms)
        special_requirements_str = ', '.join(forwarder.special_requirements)

        value = (
            forwarder.name, 
            transport_modes_str, 
            additional_services_str, 
            insurance_types_str, 
            trade_terms_str, 
            special_requirements_str
        )
        
        print(f"삽입할 값: {value}")

        cursor.execute(add_forwarder, value)

        conn.commit()

        return {"message": f"{forwarder.name} 저장 완료!"}

    except IntegrityError:
        return {"message": f"{forwarder.name}은 이미 존재합니다!"}

    finally:
        cursor.close()

