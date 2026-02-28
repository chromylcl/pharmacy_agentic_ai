import React from 'react';
import { ShoppingBag, Pill, Search, FileText, ChevronRight } from 'lucide-react';

const QuickActions = ({ onAction }) => {
  const actions = [
    { label: 'Browse Store', icon: <ShoppingBag />, color: 'text-emerald-500', prompt: 'I want to see the medicine catalog.' },
    { label: 'Refill Check', icon: <Pill />, color: 'text-blue-500', prompt: 'Do I have any pending refills?' },
    { label: 'Consult AI', icon: <Search />, color: 'text-purple-500', prompt: 'I need medical advice for my symptoms.' },
    { label: 'Upload RX', icon: <FileText />, color: 'text-amber-500', prompt: 'TRIGGER_RX_UPLOAD' }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-5 w-full max-w-3xl mx-auto">
      {actions.map((action, idx) => (
        <button
          key={idx}
          onClick={() => onAction(action.prompt)}
          className="group relative flex items-center justify-between p-6 bg-white/40 backdrop-blur-xl border border-white/60 rounded-[2.5rem] hover:bg-white/70 hover:scale-[1.02] hover:shadow-2xl transition-all duration-500 text-left active:scale-[0.98]"
        >
          <div className="flex items-center gap-5">
            <div className={`p-4 bg-white rounded-3xl shadow-sm group-hover:shadow-lg transition-all ${action.color}`}>
              {React.cloneElement(action.icon, { size: 24, strokeWidth: 2.5 })}
            </div>
            <div>
              <h3 className="font-black text-slate-800 text-lg tracking-tight">{action.label}</h3>
              <p className="text-[10px] font-black uppercase tracking-[0.15em] text-slate-400 mt-1">Select Workflow</p>
            </div>
          </div>
          <div className="opacity-0 group-hover:opacity-100 transition-all translate-x-[-10px] group-hover:translate-x-0 text-slate-400">
            <ChevronRight size={20} />
          </div>
        </button>
      ))}
    </div>
  );
};

export default QuickActions;