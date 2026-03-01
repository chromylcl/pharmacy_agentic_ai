import { AlertTriangle, PhoneCall, ArrowLeft, ShieldAlert } from 'lucide-react';

const EmergencyOverlay = ({ isOpen, onClose, triggerWord }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-rose-950/80 backdrop-blur-xl animate-in fade-in duration-500">
      
      {/* Background pulsing effect */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[50vw] h-[50vw] bg-rose-600/20 rounded-full blur-[100px] animate-pulse duration-1000"></div>
      </div>

      <div className="glass-panel relative w-full max-w-2xl p-8 md:p-12 border-rose-500/50 shadow-2xl shadow-rose-900/50 bg-white/10 text-center">
        
        <div className="mx-auto w-24 h-24 bg-rose-500/20 text-rose-500 rounded-full flex items-center justify-center mb-6 animate-bounce shadow-lg shadow-rose-500/20 border border-rose-500/30">
          <AlertTriangle size={48} strokeWidth={2.5} />
        </div>

        <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-4">
          Medical Emergency Detected
        </h1>
        
        <p className="text-rose-200 text-lg font-medium mb-8 max-w-xl mx-auto">
          You mentioned <span className="text-white font-bold px-2 py-0.5 bg-rose-500/40 rounded-md">"{triggerWord}"</span>. 
          AI Agents are not equipped to handle life-threatening situations. Please contact emergency services immediately.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-10 text-left">
          {/* Ambulance Card */}
          <div className="bg-rose-900/40 border border-rose-500/30 p-5 rounded-2xl flex items-center justify-between group hover:bg-rose-800/50 transition-colors cursor-pointer">
            <div>
              <p className="text-rose-300 text-xs font-bold uppercase tracking-widest mb-1">Ambulance / Medical</p>
              <p className="text-3xl font-black text-white">108</p>
            </div>
            <div className="p-3 bg-rose-500 text-white rounded-xl shadow-md group-hover:scale-110 transition-transform">
              <PhoneCall size={24} />
            </div>
          </div>

          {/* Poison Control Card */}
          <div className="bg-rose-900/40 border border-rose-500/30 p-5 rounded-2xl flex items-center justify-between group hover:bg-rose-800/50 transition-colors cursor-pointer">
            <div>
              <p className="text-rose-300 text-xs font-bold uppercase tracking-widest mb-1">Poison Control</p>
              <p className="text-3xl font-black text-white">1066</p>
            </div>
            <div className="p-3 bg-amber-500 text-white rounded-xl shadow-md group-hover:scale-110 transition-transform">
              <ShieldAlert size={24} />
            </div>
          </div>
        </div>

        <div className="flex justify-center">
          <button 
            onClick={onClose}
            className="flex items-center gap-2 px-6 py-3 rounded-full bg-white/10 hover:bg-white/20 text-white font-semibold border border-white/20 transition-all active:scale-95"
          >
            <ArrowLeft size={18} /> Acknowledge & Return to Chat
          </button>
        </div>
      </div>
    </div>
  );
};

export default EmergencyOverlay;