import React, { useState, useEffect } from 'react';
import { Server } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '';

export default function AssetTable({ scanId }) {
  const [scanData, setScanData] = useState(null);

  useEffect(() => {
    if (!scanId) return;
    const fetchDetails = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/scans/${scanId}`);
        const data = await res.json();
        setScanData(data);
      } catch (err) {
        console.error("Error fetching scan details:", err);
      }
    };
    fetchDetails();
    const interval = setInterval(fetchDetails, 3000);
    return () => clearInterval(interval);
  }, [scanId]);

  if (!scanId || !scanData) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-500">
        Select a scan to view discovered assets.
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2"><Server className="w-5 h-5 text-cyan-400"/> Discovered Hosts</h2>
          <p className="text-xs text-slate-400 font-mono mt-0.5">Target: {scanData.target} | Status: <span className="text-cyan-300 font-semibold">{scanData.status}</span></p>
        </div>
      </div>

      <div className="space-y-4">
        {scanData.hosts && scanData.hosts.length === 0 ? (
          <div className="text-center py-8 text-slate-500 font-mono text-sm">
            {scanData.status === 'Running' || scanData.status === 'Queued'
              ? 'Scan in progress... Please wait while Nmap assesses the target.'
              : 'No hosts discovered or no ports were open on this target.'}
          </div>
        ) : (
          scanData.hosts?.map((host) => {
            let ports = [];
            try {
              ports = host.ports_data ? JSON.parse(host.ports_data) : [];
            } catch (e) {
              ports = [];
            }
            return (
              <div key={host.id} className="border border-slate-800 rounded-lg p-4 bg-slate-950">
                <div className="flex justify-between items-center mb-2 font-mono">
                  <div className="flex items-center gap-2">
                    <span className="text-cyan-400 font-bold">{host.ip_address}</span>
                    {host.hostname && <span className="text-xs text-slate-400">({host.hostname})</span>}
                  </div>
                  <span className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-300">{host.status}</span>
                </div>
                {ports.length > 0 ? (
                  <div className="overflow-x-auto mt-3">
                    <table className="w-full text-left text-xs font-mono">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400">
                          <th className="pb-2">Port</th>
                          <th className="pb-2">Protocol</th>
                          <th className="pb-2">State</th>
                          <th className="pb-2">Service</th>
                          <th className="pb-2">Version</th>
                        </tr>
                      </thead>
                      <tbody>
                        {ports.map((p, idx) => (
                          <tr key={idx} className="border-b border-slate-900 hover:bg-slate-900/40">
                            <td className="py-1.5 text-cyan-300 font-semibold">{p.port}</td>
                            <td className="py-1.5 uppercase text-slate-400">{p.protocol}</td>
                            <td className="py-1.5 text-emerald-400">{p.state}</td>
                            <td className="py-1.5 font-semibold text-slate-200">{p.service}</td>
                            <td className="py-1.5 text-slate-400 truncate max-w-xs">{p.version || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-xs text-slate-500 font-mono mt-2">No open ports found on this host.</div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
