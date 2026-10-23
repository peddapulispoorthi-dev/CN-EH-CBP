# NetLens: Nmap-Based Network Security Assessment and Infrastructure Discovery Framework

NetLens is a full-stack automated network assessment platform that coordinates Nmap scanning through a distributed task architecture, persists discovery metrics, and serves an interactive cyber-security operations dashboard.

---

## Architecture Overview

NetLens consists of 5 modular services:

1. **Frontend (React 18 + Vite + Tailwind CSS)**
   - Target input and scan profile selection
   - Auto-refreshing scan status and host discovery feed
   - Detailed host port, protocol, service, and version breakdown
   
2. **Backend API (FastAPI + SQLAlchemy + Pydantic v2)**
   - RESTful endpoints for scan dispatch and retrieval
   - Relational mapping between scans and discovered assets
   - Celery task submission with local async fallback

3. **Task Queue & Broker (Celery + Redis)**
   - Asynchronous execution of long-running Nmap scans
   - Decoupled workers capable of running privileged network scanning

4. **Database (PostgreSQL / SQLite Fallback)**
   - Relational persistence of scans and open port metadata

5. **Network Scanner (Nmap + Python-Nmap)**
   - Pre-configured scan profiles (`quick`, `standard`, `stealth`, `vulnerability`)

---

## Project Structure

```text
netlens/
├── docker-compose.yml
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── nmap_service.py
│   └── celery_worker.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── postcss.config.js
    ├── tailwind.config.js
    ├── index.html
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── index.css
        └── components/
            ├── ScanForm.jsx
            └── AssetTable.jsx
```

---

## Scan Profiles

| Profile | Nmap Arguments | Purpose |
| :--- | :--- | :--- |
| **Quick** | `-sn` | Host discovery (Ping Sweep) without port scan |
| **Standard** | `-sV -p 1-1000` | Common ports service & version inspection |
| **Stealth** | `-sS -T4` | Half-open SYN scan for stealthy discovery |
| **Vulnerability** | `-sV -O --script vuln` | OS fingerprinting + Nmap Scripting Engine (NSE) vulnerability checks |

---

## Running with Docker (Recommended)

1. Make sure **Docker** and **Docker Compose** are installed and running.
2. Navigate into the `netlens` folder:
   ```bash
   cd netlens
   ```
3. Build and launch all 5 containers:
   ```bash
   docker-compose up --build
   ```
4. Access the applications:
   - **Web Dashboard**: [http://localhost:5173](http://localhost:5173)
   - **FastAPI Interactive Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **API ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Running Locally on Host (Without Docker)

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Nmap** installed and accessible in system `PATH`

### 2. Backend Setup
```bash
cd netlens/backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
*(Note: If Redis / PostgreSQL are not running locally, NetLens automatically falls back to an embedded SQLite database and local background worker threads).*

### 3. Frontend Setup
```bash
cd netlens/frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.
