from fastapi import FastAPI, HTTPException, status
import mysql.connector

from mysql.connector.connection import MySQLConnection

def init_db(conn: MySQLConnection):
    query = """
    CREATE TABLE IF NOT EXISTS forwarder (
        forwarder_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        transport_modes VARCHAR(255),
        additional_services VARCHAR(255),
        insurance_types VARCHAR(255),
        trade_terms VARCHAR(255),
        special_requirements VARCHAR(255)
    );
    """
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()


def connect():
    mydb = mysql.connector.connect(
        host = "rootimpact10.cpuyiuu4iuwi.ap-northeast-2.rds.amazonaws.com",
        user = "admin",
        password = "RootImpact10",
        database = "server"
    )
    #logismate.cl8qqy0go6xk.ap-northeast-2.rds.amazonaws.com

    return mydb

def get_mydb():
    conn = connect()

    try:
        yield conn
    finally:
        conn.close()
