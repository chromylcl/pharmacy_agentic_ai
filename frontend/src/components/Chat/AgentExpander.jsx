import { useState } from 'react';
import { usePharmacy } from '../../context/PharmacyContext';
import { Brain, Stethoscope, Pill, ShieldAlert, Package, CreditCard, RotateCcw, CheckCircle2, Loader2, ChevronDown, ChevronUp } from 'lucide-react';

const AGENT_CONFIG = {
  orchestrator: { icon: Brain, color: 'text-purple-500', bg: 'bg-purple-500/10', border: 'border-purple-200', label: 'Orchestrator Agent' },
  physician: { icon: Stethoscope, color: 'text-blue-500', bg: 'bg-blue-500/10', border: 'border-blue-200', label: 'GP Agent' },
  pharmacist: { icon: Pill, color: 'text-emerald-500', bg: 'bg-emerald-500/10', border: 'border-emerald-200', label: 'Pharmacist Agent' },
  regulatory: { icon: ShieldAlert, color: 'text-amber-500', bg: 'bg-amber-500/10', border: 'border-amber-200', label: 'Regulatory Agent' },
  inventory: { icon: Package, color: 'text-orange-500', bg: 'bg-orange-500/10', border: 'border-orange-200', label: 'Inventory Agent' },
  billing: { icon: CreditCard, color: 'text-slate-600', bg: 'bg-slate-100', border: 'border-slate-200', label: 'Billing Agent' },
  refill: { icon: RotateCcw, color: 'text-cyan-500', bg: 'bg-cyan-500/10', border: 'border-cyan-200', label: 'Refill Agent' }
};

const AgentExpander = () => {
  // Added safe default empty objects to prevent the crash!
  const { agentStatus = {}, traces = {} } = usePharmacy();
  const [isExpanded, setIsExpanded] = useState(true);

  // Safely check if any agent is active
  const safeAgentStatus = agentStatus || {};
  const isActive = Object.values(safeAgentStatus).some(status => status !== 'idle');

  if (!isActive) return null;

  return (
    <div className="w-full max-w-sm ml-4 mb-4">
      <button 
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 px-4 py-2 bg-white/40 backdrop-blur-md border border-white/60 rounded-full shadow-sm text-xs font-bold text-slate-600 uppercase tracking-widest hover:bg-white/60 transition-colors"
      >
        <Brain size={14} className="text-purple-500 animate-pulse" />
        Agent Network Active
        {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {isExpanded && (
        <div className="mt-3 space-y-2">
          {Object.entries(safeAgentStatus).map(([agentKey, status]) => {
            if (status === 'idle') return null;

            const config = AGENT_CONFIG[agentKey] || AGENT_CONFIG.orchestrator;
            const Icon = config.icon;
            const safeTraces = traces || {};

            return (
              <div key={agentKey} className={`flex items-start gap-3 p-3 rounded-2xl bg-white/50 border ${config.border} shadow-sm transition-all duration-500`}>
                <div className={`p-2 rounded-xl ${config.bg} ${config.color}`}>
                  {status === 'thinking' ? <Loader2 size={16} className="animate-spin" /> : <Icon size={16} />}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className={`text-xs font-bold uppercase tracking-wider ${config.color}`}>
                      {config.label}
                    </span>
                    {status === 'done' && <CheckCircle2 size={14} className="text-emerald-500" />}
                  </div>
                  
                  <div className="mt-1 text-sm text-slate-600 font-medium">
                    {status === 'thinking' 
                      ? "Analyzing query parameters and retrieving context..." 
                      : safeTraces[agentKey] || "Task completed successfully."}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default AgentExpander;