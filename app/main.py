import os
from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2 import errors
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, EmailStr
from fastapi import status


class ServiceRequestCreate(BaseModel):
    description: str
    customer_name: str
    customer_email: EmailStr


app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "servicedb")
DB_USER = os.getenv("DB_USER", "serviceuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "servicepass")


def get_db_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=5,
        cursor_factory=RealDictCursor,
    )

@app.get("/service-requests/{request_id}")
def get_service_request(request_id: int):
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                  "SELECT id, description, customer_name, customer_email "
                  "FROM service_requests " 
                  "WHERE id = %s",
                  (request_id,),
                )
                row = cur.fetchone()
            
    except errors.QueryCanceled:
        raise HTTPException(status_code=504, detail="Database timeout")

    except Exception:
        raise HTTPException(status_code=500, detail="Database error")
    
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    
    return row

@app.get("/service-requests")
def find_by_email(customer_email: str):
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, description, customer_name, customer_email "
                "FROM service_requests " 
                "WHERE customer_email = %s "
                "ORDER BY id",
                (customer_email,),
            )
            return cur.fetchall()

@app.post("/service-requests", status_code=status.HTTP_201_CREATED)
def create_service_request(payload: ServiceRequestCreate):
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO service_requests (description, customer_name, customer_email)
                VALUES (%s, %s, %s)
                RETURNING id, description, customer_name, customer_email
                """,
                (payload.description, payload.customer_name, payload.customer_email),
            )
            row = cur.fetchone()
            conn.commit()
            return row



@app.get("/health")
def health():
    print("Health Check")
    return {"status": "ok"}