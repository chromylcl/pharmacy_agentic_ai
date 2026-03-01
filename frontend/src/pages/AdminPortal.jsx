import { useState, useEffect } from 'react';
import { Activity, ShieldAlert, Database, Zap, FileText, AlertTriangle, CheckCircle2, TrendingUp, Users, ArrowUpRight } from 'lucide-react';
import { pharmacyService } from '../services/api';

const glassClasses = "bg-white/30 backdrop-blur-[32px] saturate-[180%] border border-white/60 shadow-[0_24px_48px_-12px_rgba(0,0,0,0.1)]";

export default function AdminPortal() {
  const [activeTab, setActiveTab] = useState('overview');
  const [inventoryCount, setInventoryCount] = useState(0);
  const [lowStockCount, setLowStockCount] = useState(0);
  const [refillCount, setRefillCount] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [invRes, lowRes, refillRes] = await Promise.all([
          pharmacyService.getInventory(),
          pharmacyService.getLowStock(),
          pharmacyService.getRefillAlerts()
        ]);
        setInventoryCount(invRes.data.length);
        setLowStockCount(lowRes.data.length);
        setRefillCount(refillRes.data.length);
      } catch (err) {
        console.error("Failed to load admin data", err);
      }
    };
    fetchData();
  }, []);

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
        
        {/* PDC RISK GAUGE */}
        <div className={`${glassClasses} p-10 rounded-[4rem] flex flex-col items-center justify-center text-center relative group`}>
          <div className="absolute top-10 right-10 text-emerald-500 bg-emerald-500/10 p-2 rounded-full">
            <TrendingUp size={20} />
          </div>
          
          <h3 className="brand-font font-black text-slate-400 uppercase tracking-widest text-[10px] mb-8">Clinical Adherence (PDC)</h3>
          
          <div className="relative w-56 h-56 mb-10">
             <svg className="w-full h-full transform -rotate-90 scale-110">
                <circle cx="112" cy="112" r="100" stroke="currentColor" strokeWidth="14" fill="transparent" className="text-slate-200/40" />
                <circle cx="112" cy="112" r="100" stroke="currentColor" strokeWidth="14" fill="transparent" 
                        strokeDasharray={628} strokeDashoffset={628 * (1 - 0.88)}
                        className="text-emerald-500 transition-all duration-1000 ease-out drop-shadow-[0_0_15px_rgba(16,185,129,0.4)]" />
             </svg>
             <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-6xl font-black text-slate-900">88<span className="text-2xl text-slate-400">%</span></span>
                <span className="text-[11px] font-black text-emerald-600 uppercase tracking-widest mt-2">Nominal Range</span>
             </div>
          </div>
          <p className="text-xs font-bold text-slate-400 max-w-[220px] leading-relaxed">
            Patient compliance levels are up <span className="text-emerald-600">+4.2%</span> since last sequence scan.
          </p>
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
            {[1, 2, 3, 4].map((_, i) => (
              <div key={i} className="flex items-center justify-between p-5 rounded-[2rem] bg-white/40 border border-white/60 hover:bg-white/70 hover:scale-[1.01] transition-all group cursor-pointer shadow-sm">
                <div className="flex items-center gap-6">
                  <div className="p-4 bg-slate-900 text-white rounded-2xl group-hover:bg-blue-600 transition-colors">
                    <Activity size={20} />
                  </div>
                  <div>
                    <p className="text-lg font-black text-slate-900">Trace: RX-904-{i}2B</p>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter mt-1">7 Agents Synchronized • 1.1s Total Execution</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                   <div className="h-2 w-24 bg-slate-200 rounded-full overflow-hidden hidden md:block">
                      <div className="h-full bg-emerald-500 w-[100%]"></div>
                   </div>
                   <span className="px-4 py-1.5 rounded-full bg-emerald-500/10 text-emerald-600 text-[10px] font-black uppercase tracking-widest">Verified</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}