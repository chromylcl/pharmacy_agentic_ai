import { useState, useEffect } from 'react';
import { Activity, ShieldAlert, Database, Zap, FileText, AlertTriangle, CheckCircle2, TrendingUp, Users, ArrowUpRight, Send } from 'lucide-react';
import { pharmacyService } from '../services/api';

const glassClasses = "bg-white/30 backdrop-blur-[32px] saturate-[180%] border border-white/60 shadow-[0_24px_48px_-12px_rgba(0,0,0,0.1)]";

export default function AdminPortal() {
  const [activeTab, setActiveTab] = useState('overview');
  const [inventoryCount, setInventoryCount] = useState(0);
  const [lowStockCount, setLowStockCount] = useState(0);
  const [refillCount, setRefillCount] = useState(0);
  const [topProducts, setTopProducts] = useState([]);
  const [systemLogs, setSystemLogs] = useState([]);
  const [refreshKey, setRefreshKey] = useState(0);

  // Test Email State
  const [testPatientId, setTestPatientId] = useState('');
  const [testMedicineName, setTestMedicineName] = useState('');
  const [testEmailStatus, setTestEmailStatus] = useState('');

  const handleTestEmail = async (e) => {
    e.preventDefault();
    setTestEmailStatus('Sending...');
    try {
      const res = await pharmacyService.testRefillEmail(testPatientId, testMedicineName);
      setTestEmailStatus(res.data.message);
      setTimeout(() => setTestEmailStatus(''), 5000);
    } catch (err) {
      setTestEmailStatus('Error sending email');
      setTimeout(() => setTestEmailStatus(''), 5000);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [invRes, lowRes, refillRes, prodRes, logsRes] = await Promise.all([
          pharmacyService.getInventory(),
          pharmacyService.getLowStock(),
          pharmacyService.getRefillAlerts(),
          pharmacyService.getProducts(),
          pharmacyService.getTraces()
        ]);
        setInventoryCount(invRes.data.length);
        setLowStockCount(lowRes.data.length);
        setRefillCount(refillRes.data.length);

        const logs = logsRes.data || [];
        setSystemLogs(logs);

        const sorted = prodRes.data.sort((a, b) => a.stock - b.stock).slice(0, 5);
        setTopProducts(sorted);
      } catch (err) {
        console.error("Failed to load admin data", err);
      }
    };
    fetchData();
  }, [refreshKey]);

  const handleRefill = async (medicineName) => {
    try {
      await pharmacyService.refillStock(medicineName, 50);
      setRefreshKey(prev => prev + 1);
    } catch (err) {
      console.error("Failed to refill", err);
    }
  };

  const stats = [
    { label: 'Total Inventory', value: inventoryCount.toString(), icon: <Database size={18} />, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { label: 'Low Stock Alerts', value: lowStockCount.toString(), icon: <AlertTriangle size={18} />, color: 'text-amber-500', bg: 'bg-amber-500/10' },
    { label: 'Refill Alerts', value: refillCount.toString(), icon: <ShieldAlert size={18} />, color: 'text-rose-500', bg: 'bg-rose-500/10' }
  ];

  return (
    <div className="w-full max-w-7xl mx-auto p-6 md:p-12 h-full overflow-y-auto scrollbar-hide space-y-12 animate-in fade-in duration-1000">

      {/* HEADER SECTION */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-8">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 text-white mb-4">
            <span className="text-[9px] font-black uppercase tracking-widest">System Architecture v2.4</span>
          </div>
          <h1 className="text-5xl font-black text-slate-900 tracking-tighter leading-none">Command Center</h1>
          <p className="text-slate-400 font-bold mt-4 uppercase tracking-[0.3em] text-[10px]">Real-time Agentic Pharmacy Monitoring</p>
        </div>

        <div className="flex gap-4">
          {stats.map((stat, i) => (
            <div key={i} className={`${glassClasses} px-6 py-4 rounded-[2.5rem] flex items-center gap-5 shadow-inner`}>
              <div className={`p-3 rounded-2xl ${stat.bg} ${stat.color}`}>{stat.icon}</div>
              <div>
                <p className="text-[9px] font-black uppercase text-slate-400 tracking-widest mb-1">{stat.label}</p>
                <p className="text-xl font-black text-slate-900">{stat.value}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ANALYTICS GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">

        {/* AGENT COMPLIANCE GAUGE (REAL DATA) */}
        <div className={`${glassClasses} p-10 rounded-[4rem] flex flex-col items-center justify-center text-center relative group`}>
          <div className="absolute top-10 right-10 text-blue-500 bg-blue-500/10 p-2 rounded-full">
            <Zap size={20} />
          </div>

          <h3 className="brand-font font-black text-slate-400 uppercase tracking-widest text-[10px] mb-8">Agent Safety Compliance</h3>

          <div className="relative w-56 h-56 mb-10 group-hover:scale-105 transition-transform duration-700">
            {(() => {
              const verified = systemLogs.filter(l => l.status === 'Verified').length;
              const total = systemLogs.length;
              const rate = total > 0 ? Math.round((verified / total) * 100) : 100;
              const isSafe = rate >= 80;

              return (
                <>
                  <svg className="w-full h-full transform -rotate-90 scale-110">
                    <circle cx="112" cy="112" r="100" stroke="currentColor" strokeWidth="14" fill="transparent" className="text-slate-200/40" />
                    <circle cx="112" cy="112" r="100" stroke="currentColor" strokeWidth="14" fill="transparent"
                      strokeDasharray={628} strokeDashoffset={628 * (1 - (rate / 100))}
                      className={`${isSafe ? 'text-blue-500 drop-shadow-[0_0_15px_rgba(59,130,246,0.4)]' : 'text-amber-500 drop-shadow-[0_0_15px_rgba(245,158,11,0.4)]'} transition-all duration-1000 ease-out`} />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-6xl font-black text-slate-900">{rate}<span className="text-2xl text-slate-400">%</span></span>
                    <span className={`text-[11px] font-black uppercase tracking-widest mt-2 ${isSafe ? 'text-blue-600' : 'text-amber-600'}`}>
                      {isSafe ? 'Verified Safe' : 'Warnings Active'}
                    </span>
                  </div>
                </>
              );
            })()}
          </div>
          <p className="text-xs font-bold text-slate-400 max-w-[220px] leading-relaxed">
            Based on <span className="text-slate-600 font-black">{systemLogs.length}</span> live agent orchestrations logged this session.
          </p>
        </div>

        {/* LIVE INVENTORY STOCK GRAPHS */}
        <div className={`${glassClasses} lg:col-span-2 p-10 rounded-[4rem] flex flex-col`}>
          <div className="flex justify-between items-center mb-8">
            <h3 className="brand-font font-black text-slate-400 uppercase tracking-widest text-[10px]">Critical Stock Levels (Bottom 5)</h3>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-blue-600 text-[10px] font-black uppercase">
              <Database size={12} /> Syncing
            </div>
          </div>

          <div className="space-y-6 flex-1 justify-center flex flex-col">
            {topProducts.map((prod, idx) => {
              const maxStock = 100; // Arbitrary visualization maximum
              const percentage = Math.min((prod.stock / maxStock) * 100, 100);
              const isCrit = percentage < 15;
              return (
                <div key={idx} className="space-y-2 group">
                  <div className="flex justify-between items-center text-xs font-bold font-mono">
                    <span className="text-slate-700 truncate max-w-[150px]">{prod.name}</span>
                    <div className="flex items-center gap-3">
                      <span className={isCrit ? 'text-rose-500 flex items-center gap-1 font-black animate-pulse' : 'text-slate-500'}>
                        {isCrit && <AlertTriangle size={12} />} {prod.stock} / {maxStock}
                      </span>
                      {isCrit && (
                        <button
                          onClick={() => handleRefill(prod.name)}
                          className="bg-slate-900 hover:bg-blue-600 text-white px-3 py-1 rounded-full text-[9px] uppercase tracking-widest transition-colors shadow-lg active:scale-95"
                        >
                          Refill +50
                        </button>
                      )}
                    </div>
                  </div>
                  <div className="h-4 w-full bg-white/50 rounded-full overflow-hidden border border-white/60 shadow-inner break-inside-avoid">
                    <div
                      className={`h-full rounded-full transition-all duration-1000 ease-out origin-left ${isCrit ? 'bg-gradient-to-r from-rose-500 to-rose-400 shadow-[0_0_10px_rgba(244,63,94,0.5)]' : 'bg-gradient-to-r from-blue-500 to-cyan-400'}`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* AGENT TRACE LOGS */}
        <div className={`${glassClasses} lg:col-span-2 p-10 rounded-[4rem] flex flex-col`}>
          <div className="flex justify-between items-center mb-10">
            <h3 className="brand-font font-black text-slate-400 uppercase tracking-widest text-[10px]">Agent Execution History</h3>
            <button className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-blue-600 hover:text-blue-800 transition-colors">
              Full Logs <ArrowUpRight size={14} />
            </button>
          </div>

          <div className="space-y-4 flex-1">
            {systemLogs.length === 0 && <p className="text-sm font-bold text-slate-400">No traces logged yet.</p>}
            {systemLogs.map((log, i) => (
              <div key={i} className="flex items-center justify-between p-5 rounded-[2rem] bg-white/40 border border-white/60 hover:bg-white/70 hover:scale-[1.01] transition-all group cursor-pointer shadow-sm">
                <div className="flex items-center gap-6">
                  <div className={`p-4 text-white rounded-2xl transition-colors ${log.status === 'Verified' ? 'bg-slate-900 group-hover:bg-blue-600' : 'bg-rose-500'}`}>
                    <Activity size={20} />
                  </div>
                  <div>
                    <p className="text-lg font-black text-slate-900">Trace: {log.trace_id}</p>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter mt-1">{log.agent_count} Agents Synchronized • {log.execution_time}s Total Execution</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="h-2 w-24 bg-slate-200 rounded-full overflow-hidden hidden md:block">
                    <div className={`h-full w-[100%] ${log.status === 'Verified' ? 'bg-emerald-500' : 'bg-rose-500'}`}></div>
                  </div>
                  <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest ${log.status === 'Verified' ? 'bg-emerald-500/10 text-emerald-600' : 'bg-rose-500/10 text-rose-600'}`}>{log.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* REFILL SIMULATOR */}
        <div className={`${glassClasses} p-10 rounded-[4rem] flex flex-col`}>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-indigo-500/10 rounded-2xl text-indigo-500"><Send size={20} /></div>
            <h3 className="brand-font font-black text-slate-800 text-lg">Test Refill Reminders</h3>
          </div>
          <p className="text-xs text-slate-500 mb-6 font-medium">Manually trigger a simulated Email Notification to a specific patient's inbox indicating low supply.</p>
          <form onSubmit={handleTestEmail} className="space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-2">Patient ID or Email</label>
              <input type="text" value={testPatientId} onChange={(e) => setTestPatientId(e.target.value)} required className="w-full bg-white/50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-bold focus:outline-none focus:border-indigo-400" placeholder="e.g. user@example.com" />
            </div>
            <div>
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-2">Medicine Name</label>
              <input type="text" value={testMedicineName} onChange={(e) => setTestMedicineName(e.target.value)} required className="w-full bg-white/50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-bold focus:outline-none focus:border-indigo-400" placeholder="e.g. Panadol" />
            </div>
            <button type="submit" disabled={testEmailStatus === 'Sending...'} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl transition-colors shadow-lg active:scale-95 disabled:opacity-50">
              {testEmailStatus === 'Sending...' ? 'Triggering...' : 'Dispatch Mock Email'}
            </button>
          </form>
          {testEmailStatus && testEmailStatus !== 'Sending...' && (
            <div className="mt-4 p-3 bg-emerald-50 text-emerald-600 text-xs font-bold border border-emerald-100 rounded-xl">
              {testEmailStatus}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}