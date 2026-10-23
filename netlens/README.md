# NetLens: Nmap-Based Network Security Assessment and Infrastructure Discovery Framework

NetLens is a full-stack automated network assessment platform that coordinates Nmap scanning through a distributed task architecture, persists discovery metrics, and serves an interactive cyber-security operations dashboard.

**GitHub Repository**: [https://github.com/peddapulispoorthi-dev/CN-EH-CBP](https://github.com/peddapulispoorthi-dev/CN-EH-CBP)

---

## Architecture Overview

NetLens consists of 5 modular services:

1. **Frontend (React 18 + Vite + Tailwind CSS)**
   - Target input and scan profile selection
   - Auto-refreshing scan status and host discovery feed
   - Detailed host port, protocol, service, and version breakdown
   
2. **Backend API (FastAPI + SQLAlchemy + Pydantic v2)**
   - RESTful endpoints for scan dispatch and retrieval
   - Serves the compiled Single Page Application (SPA) directly from `/`
   - Relational mapping between scans and discovered assets
   - Celery task submission with local async fallback

3. **Task Queue & Broker (Celery + Redis / Local Daemon Threads)**
   - Asynchronous execution of long-running Nmap scans
   - Decoupled workers capable of running privileged network scanning

4. **Database (PostgreSQL / SQLite Automatic Failover)**
   - Relational persistence of scans and open port metadata
   - Automated zero-config fallback to SQLite on local host

5. **Network Scanner (Nmap + Python-Nmap)**
   - Pre-configured scan profiles (`quick`, `standard`, `stealth`, `vulnerability`)
   - Automatic detection of standard Nmap installation directories on Windows & Linux

---

## Project Structure

```text
├── start_netlens.bat        # 1-Click Windows Batch Launcher
├── start_netlens.ps1        # 1-Click PowerShell Launcher
├── netlens/
│   ├── docker-compose.yml   # Multi-container orchestration
│   ├── README.md
│   ├── backend/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── nmap_service.py
│   │   └── celery_worker.py
│   └── frontend/
│       ├── Dockerfile
│       ├── package.json
│       ├── vite.config.js
│       ├── postcss.config.js
│       ├── tailwind.config.js
│       ├── index.html
│       └── src/
│           ├── App.jsx
│           ├── main.jsx
│           ├── index.css
│           └── components/
│               ├── ScanForm.jsx
│               └── AssetTable.jsx
```

---

## Scan Profiles

| Profile | Nmap Arguments | Networking Technique | Purpose |
| :--- | :--- | :--- | :--- |
| **Quick** | `-sn` | ICMP / TCP SYN-ACK ping sweeps | Fast host discovery without port scanning |
| **Standard** | `-sV -p 1-1000` | Full 3-way TCP handshake + banner grabbing | Common ports service & version inspection |
| **Stealth** | `-sS -T4` | Half-open SYN scan (`SYN` $\rightarrow$ `RST`) | Stealthy port discovery |
| **Vulnerability** | `-sV -O --script vuln` | OS fingerprinting + NSE scripts | Comprehensive vulnerability audit |

---

## Recommended Test Targets

| Target | Recommended Profile | Expected Output |
| :--- | :--- | :--- |
| `scanme.nmap.org` (or `45.33.32.156`) | **Standard (`-sV`)** | Port 22 (SSH), Port 80 (HTTP Apache) |
| `192.168.29.1` (Local Gateway) | **Standard (`-sV`)** | Port 53 (DNS), Port 80 (Router Web Portal), Port 443 |
| `192.168.29.0/24` (Subnet) | **Quick (`-sn`)** | Active devices & hostnames across Wi-Fi network |
| `127.0.0.1` (Local Machine) | **Standard (`-sV`)** | Local listening services (Port 135, 445, etc.) |

---

## Quick Start: 1-Click Unified Deployment (Recommended)

To run everything in production mode on a single port:

- **Windows Explorer**: Double-click `start_netlens.bat`
- **PowerShell**: Run `.\start_netlens.ps1`

The launcher will verify prerequisites, build the frontend, automatically detect free ports, start the server, and open `http://localhost:8000` in your default browser.

---

## Running with Docker

1. Ensure **Docker** and **Docker Compose** are installed and running.
2. Navigate into `netlens`:
   ```bash
   cd netlens
   docker-compose up --build
   ```
3. Access:
   - Dashboard: `http://localhost:5173`
   - FastAPI Docs: `http://localhost:8000/docs`

---

## Running in Development Mode

### 1. Backend
```bash
cd netlens/backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend
```bash
cd netlens/frontend
npm install
npm run dev
```
Dashboard will be live at `http://localhost:5173`.
