import json
import os
import shutil

import nmap


def ensure_nmap_binary_on_path():
    if shutil.which("nmap"):
        return

    candidates = [
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Nmap", "nmap.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Nmap", "nmap.exe"),
        r"C:\Program Files (x86)\Nmap\nmap.exe",
        r"C:\Program Files\Nmap\nmap.exe",
    ]

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            nmap_dir = os.path.dirname(candidate)
            os.environ["PATH"] = f"{nmap_dir}{os.pathsep}{os.environ.get('PATH', '')}"
            return


ensure_nmap_binary_on_path()


def run_nmap_scan(target: str, profile: str):
    nm = nmap.PortScanner()
    
    args_map = {
        "quick": "-sn",
        "standard": "-sV -p 1-1000",
        "stealth": "-sS -T4",
        "vulnerability": "-sV -O --script vuln"
    }
    
    arguments = args_map.get(profile, "-sV")
    
    def parse_results(scanner):
        results = []
        for host in scanner.all_hosts():
            host_info = {
                "ip": host,
                "hostname": scanner[host].hostname(),
                "status": scanner[host].state(),
                "ports": []
            }
            
            for proto in scanner[host].all_protocols():
                ports = scanner[host][proto].keys()
                for port in sorted(ports):
                    port_state = scanner[host][proto][port]['state']
                    service = scanner[host][proto][port]['name']
                    version = scanner[host][proto][port].get('version', '')
                    host_info["ports"].append({
                        "port": port,
                        "protocol": proto,
                        "state": port_state,
                        "service": service,
                        "version": version
                    })
            results.append(host_info)
        return results

    try:
        nm.scan(hosts=target, arguments=arguments)
        return parse_results(nm)
    except Exception as e:
        err_msg = str(e)
        print(f"Nmap execution error: {err_msg}")
        # If privileged scan fails on an unprivileged host, fallback to TCP connect scan
        if "privileges" in err_msg.lower() or "root" in err_msg.lower():
            try:
                print("Retrying scan with unprivileged connect scan flags (-sT -p 1-1000)...")
                nm.scan(hosts=target, arguments="-sT -p 1-1000")
                return parse_results(nm)
            except Exception as fallback_err:
                print(f"Fallback scan also failed: {fallback_err}")
                return []
        return []
