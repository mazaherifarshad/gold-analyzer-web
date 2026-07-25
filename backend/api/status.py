from fastapi import APIRouter
from sqlalchemy import text

from database.database import SessionLocal

router = APIRouter(
    tags=["Status"]
)


@router.get("/status")
def status():

    db = SessionLocal()

    try:

        db.execute(text("SELECT 1"))

        return {

            "application": "Gold Analyzer Pro",

            "version": "2.0",

            "api": "Online",

            "database": "Connected",

            "analysis_engine": "Ready"

        }

    finally:

        db.close()