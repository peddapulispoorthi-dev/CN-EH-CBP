import React, { useState, useEffect } from 'react';
import ScanForm from './components/ScanForm';
import AssetTable from './components/AssetTable';
import { Shield, Activity } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '';

export default function App() {
  const [scans, setScans] = useState([]);
  const [selectedScan, setSelectedScan] = useState(null);

  const fetchScans = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/scans`);
      const data = await res.json();
      setScans(data);
      if (data.length > 0 && !selectedScan) {
        setSelectedScan(data[0].id);
      }
    } catch (err) {
      console.error("Error fetching scans:", err);
    }
  };

  useEffect(() => {
    fetchScans();
    const interval = setInterval(fetchScans, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto">
      <header className="flex items-center justify-between border-b border-slate-800 pb-4 mb-8">
        <div className="flex items-center space-x-3">
          <Shield className="w-8 h-8 text-cyan-400" />
          <h1 className="text-2xl font-bold tracking-wider">NETLENS <span className="text-cyan-400 text-sm font-normal">Security & Discovery</span></h1>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="space-y-6">
          <ScanForm onScanStarted={fetchScans} />
          
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Activity className="w-5 h-5 text-cyan-400"/> Scan History</h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {scans.length === 0 ? (
                <div className="text-xs text-slate-500 font-mono py-2 text-center">No scans recorded yet.</div>
              ) : (
                scans.map((scan) => (
                  <div 
                    key={scan.id} 
                    onClick={() => setSelectedScan(scan.id)}
                    className={`p-3 rounded-lg border cursor-pointer transition ${selectedScan === scan.id ? 'border-cyan-500 bg-slate-800/80' : 'border-slate-800 bg-slate-900/50 hover:bg-slate-800'}`}
                  >
                    <div className="flex justify-between font-mono text-sm">
                      <span className="text-cyan-300">{scan.target}</span>
                      <span className={`px-2 py-0.5 rounded text-xs ${scan.status === 'Completed' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : scan.status === 'Running' ? 'bg-blue-950 text-blue-400 border border-blue-800' : scan.status === 'Failed' ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}`}>{scan.status}</span>
                    </div>
                    <div className="text-xs text-slate-400 mt-1">Profile: {scan.profile}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="lg:col-span-2">
          <AssetTable scanId={selectedScan} />
        </div>
      </div>
    </div>
  );
}
