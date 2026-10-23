import React, { useState } from 'react';
import { Play } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '';

export default function ScanForm({ onScanStarted }) {
  const [target, setTarget] = useState('127.0.0.1');
  const [profile, setProfile] = useState('standard');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await fetch(`${API_BASE}/api/scans`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target, profile })
      });
      setTarget('');
      onScanStarted();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Play className="w-5 h-5 text-cyan-400"/> New Network Scan</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs uppercase text-slate-400 mb-1 font-mono">Target IP / CIDR</label>
          <input 
            type="text" 
            value={target} 
            onChange={(e) => setTarget(e.target.value)} 
            required
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm font-mono focus:outline-none focus:border-cyan-500"
            placeholder="e.g. 192.168.1.0/24 or 127.0.0.1"
          />
        </div>
        <div>
          <label className="block text-xs uppercase text-slate-400 mb-1 font-mono">Scan Profile</label>
          <select 
            value={profile} 
            onChange={(e) => setProfile(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value="quick">Quick Ping Discovery (-sn)</option>
            <option value="standard">Standard Service Scan (-sV)</option>
            <option value="stealth">Stealth SYN Scan (-sS)</option>
            <option value="vulnerability">Deep Vulnerability Script Scan (--script vuln)</option>
          </select>
        </div>
        <button 
          type="submit" 
          disabled={loading}
          className="w-full bg-cyan-600 hover:bg-cyan-500 font-medium py-2.5 rounded-lg transition text-sm flex items-center justify-center gap-2 disabled:opacity-50"
        >
          <Play className="w-4 h-4"/> {loading ? 'Launching...' : 'Launch Scan'}
        </button>
      </form>
    </div>
  );
}
