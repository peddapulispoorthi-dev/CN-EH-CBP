import os
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
import threading
import logging

from database import engine, Base, get_db, init_db
from models import Scan, Host
from celery_worker import execute_scan_task, run_scan_job

# Ensure all database tables exist
init_db()

app = FastAPI(
    title="NetLens API",
    description="Nmap-Based Network Security Assessment and Infrastructure Discovery Framework",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    target: str
    profile: str = "standard"

class HostResponse(BaseModel):
    id: int
    scan_id: int
    ip_address: str
    hostname: Optional[str] = None
    status: str
    ports_data: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ScanSummaryResponse(BaseModel):
    id: int
    target: str
    profile: str
    status: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ScanDetailResponse(BaseModel):
    id: int
    target: str
    profile: str
    status: str
    created_at: Optional[datetime] = None
    hosts: List[HostResponse] = []

    model_config = ConfigDict(from_attributes=True)

@app.post("/api/scans")
def trigger_scan(payload: ScanRequest, db: Session = Depends(get_db)):
    new_scan = Scan(target=payload.target, profile=payload.profile, status="Queued")
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)
    
    # Try Celery async dispatch; gracefully fallback to background thread if Celery/Redis is offline
    dispatched = False
    try:
        execute_scan_task.delay(new_scan.id, payload.target, payload.profile)
        dispatched = True
    except Exception as ex:
        logging.info(f"Celery queue unavailable ({ex}). Dispatching scan task via local background thread.")
        thread = threading.Thread(
            target=run_scan_job,
            args=(new_scan.id, payload.target, payload.profile),
            daemon=True
        )
        thread.start()
        dispatched = True
    
    return {"scan_id": new_scan.id, "status": "Queued", "dispatched": dispatched}

@app.get("/api/scans", response_model=List[ScanSummaryResponse])
def get_scans(db: Session = Depends(get_db)):
    scans = db.query(Scan).order_by(Scan.created_at.desc()).all()
    return scans

@app.get("/api/scans/{scan_id}", response_model=ScanDetailResponse)
def get_scan_details(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "NetLens API"}

# Mount Production Frontend (SPA) if dist directory exists
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Allow API routes and OpenAPI docs to pass through
        if full_path.startswith("api/") or full_path in ("docs", "redoc", "openapi.json"):
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = os.path.join(frontend_dist, full_path)
        if file_path and os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
