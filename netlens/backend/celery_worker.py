import os
import json
import logging
from celery import Celery
from database import SessionLocal, init_db
from models import Scan, Host
from nmap_service import run_nmap_scan

# Ensure database tables exist
init_db()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("tasks", broker=redis_url, backend=redis_url)

def run_scan_job(scan_id: int, target: str, profile: str):
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            logging.error(f"Scan ID {scan_id} not found in database.")
            return
        
        scan.status = "Running"
        db.commit()
        
        scan_results = run_nmap_scan(target, profile)
        
        for res in scan_results:
            host_record = Host(
                scan_id=scan.id,
                ip_address=res["ip"],
                hostname=res.get("hostname", ""),
                status=res.get("status", "unknown"),
                ports_data=json.dumps(res.get("ports", []))
            )
            db.add(host_record)
            
        scan.status = "Completed"
        db.commit()
        logging.info(f"Scan {scan_id} finished successfully with {len(scan_results)} host(s).")
    except Exception as e:
        logging.error(f"Error in scan job {scan_id}: {e}", exc_info=True)
        try:
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                scan.status = "Failed"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()

@celery_app.task(bind=True)
def execute_scan_task(self, scan_id: int, target: str, profile: str):
    run_scan_job(scan_id, target, profile)
