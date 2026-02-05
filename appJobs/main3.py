import os
from datetime import datetime
from typing import Literal, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import errors

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr


# ---------- Pydantic Schemas (schemas.py) ----------
JobOrderStatus = Literal["NEW", "SCHEDULED", "IN_PROGRESS", "DONE", "CANCELLED"]

class CustomerCreate(BaseModel):
    cust_name: str
    cust_email: EmailStr

class CustomerOut(BaseModel):
    cust_id: int
    cust_name: str
    cust_email: EmailStr

class JobCreate(BaseModel):
    job_title: str

class JobOut(BaseModel):
    job_id: int
    job_title: str

class JobOrderCreate(BaseModel):
    cust_id: int
    job_id: int
    customer_note: Optional[str] = None

class JobOrderOut(BaseModel):
    job_order_id: int
    cust_id: int
    job_id: int
    created_at: datetime
    status: JobOrderStatus
    customer_note: Optional[str] = None


# ---------- App / DB ----------
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

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Customers ----------
@app.post("/customers", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate):
    email = str(payload.cust_email).strip().lower()

    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO customers (cust_name, cust_email)
                    VALUES (%s, %s)
                    RETURNING cust_id, cust_name, cust_email
                    """,
                    (payload.cust_name, email),
                )
                row = cur.fetchone()
                conn.commit()
                return row

    except errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Customer email already exists")
    except Exception:
        raise HTTPException(status_code=500, detail="Database error")


@app.get("/customers/{cust_id}", response_model=CustomerOut)
def get_customer(cust_id: int):
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT cust_id, cust_name, cust_email
                FROM customers
                WHERE cust_id = %s AND deleted_at IS NULL
                """,
                (cust_id,),
            )
            row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    return row


# ---------- Jobs ----------
@app.post("/jobs", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate):
    title = payload.job_title.strip()

    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO jobs (job_title)
                    VALUES (%s)
                    RETURNING job_id, job_title
                    """,
                    (title,),
                )
                row = cur.fetchone()
                conn.commit()
                return row

    except errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Job title already exists")
    except Exception:
        raise HTTPException(status_code=500, detail="Database error")


@app.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int):
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT job_id, job_title FROM jobs WHERE job_id = %s",
                (job_id,),
            )
            row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return row

from typing import Optional
from fastapi import Query

@app.get("/jobs_By", response_model=JobOut)
def get_job_by_any(
    job_id: Optional[int] = Query(None),
    job_title: Optional[str] = Query(None),
):
    if not job_id and not job_title:
        raise HTTPException(
            status_code=400,
            detail="Please provide job_id or job_title",
        )

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            if job_id:
                cur.execute(
                    "SELECT job_id, job_title FROM jobs WHERE job_id = %s",
                    (job_id,),
                )
            else:
                cur.execute(
                    "SELECT job_id, job_title FROM jobs WHERE job_title ILIKE %s",
                    (f"%{job_title}%",),
                )
            row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Job not found")

    return row


# ---------- Job Orders ----------
@app.post("/job-orders", response_model=JobOrderOut, status_code=status.HTTP_201_CREATED)
def create_job_order(payload: JobOrderCreate):
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            # validate FK แบบง่าย ๆ (เหมือน logic ใน main3.py)
            cur.execute("SELECT 1 FROM customers WHERE cust_id=%s AND deleted_at IS NULL", (payload.cust_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=400, detail="Invalid cust_id")

            cur.execute("SELECT 1 FROM jobs WHERE job_id=%s", (payload.job_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=400, detail="Invalid job_id")

            cur.execute(
                """
                INSERT INTO job_orders (cust_id, job_id, customer_note)
                VALUES (%s, %s, %s)
                RETURNING job_order_id, cust_id, job_id, created_at, status, customer_note
                """,
                (payload.cust_id, payload.job_id, payload.customer_note),
            )
            row = cur.fetchone()
            conn.commit()
            return row


@app.get("/job-orders/{job_order_id}", response_model=JobOrderOut)
def get_job_order(job_order_id: int):
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT job_order_id, cust_id, job_id, created_at, status, customer_note
                FROM job_orders
                WHERE job_order_id = %s
                """,
                (job_order_id,),
            )
            row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Job order not found")
    return row


@app.get("/customers/{cust_id}/job-orders", response_model=list[JobOrderOut])
def list_customer_job_orders(cust_id: int):
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM customers WHERE cust_id=%s AND deleted_at IS NULL", (cust_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Customer not found")

            cur.execute(
                """
                SELECT job_order_id, cust_id, job_id, created_at, status, customer_note
                FROM job_orders
                WHERE cust_id = %s
                ORDER BY created_at DESC
                """,
                (cust_id,),
            )
            return cur.fetchall()
