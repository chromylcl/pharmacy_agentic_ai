import { useState } from 'react';
import { usePharmacy } from '../../context/PharmacyContext';
import { Pill, ShoppingBag, RotateCcw, ShoppingCart } from 'lucide-react';

const Navbar = ({ activeTab, setActiveTab }) => {
  const { setMessages, setAgentStatus, cart, setIsBillingOpen } = usePharmacy();

  const handleReset = () => {
    setMessages([]);
    setAgentStatus({
      orchestrator: 'idle', pharmacist: 'idle', physician: 'idle',
      regulatory: 'idle', inventory: 'idle', billing: 'idle', refill: 'idle'
    });
  };

  return (
    <>
      <div className="w-full flex justify-center pt-6 px-4 z-50 sticky top-0 animate-in slide-in-from-top-4 duration-700">
        {/* PREMIUM LIQUID GLASS PILL */}
        <nav className="w-full max-w-5xl px-5 py-3 flex items-center justify-between rounded-full bg-white/20 backdrop-blur-[32px] saturate-[150%] border border-white/50 shadow-[inset_0_1px_0_rgba(255,255,255,0.8),0_10px_30px_-10px_rgba(0,0,0,0.1)]">
          
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="bg-emerald-500/15 p-2 rounded-full border border-emerald-500/30 shadow-[inset_0_1px_0_rgba(255,255,255,0.6)]">
              <Pill size={20} className="text-emerald-600" strokeWidth={2.5} />
            </div>
            <span className="text-lg font-bold tracking-tight text-slate-800 drop-shadow-sm">
              Pharma<span className="text-emerald-600">Agent</span>
            </span>
          </div>

          {/* Desktop Tabs */}
          <div className="hidden md:flex items-center gap-2 px-4 py-1.5 bg-white/30 rounded-full border border-white/40 shadow-inner">
            {['chat', 'store', 'admin'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-5 py-1.5 rounded-full text-sm font-bold capitalize transition-all duration-300 ${
                  activeTab === tab 
                  ? 'bg-white text-emerald-600 shadow-sm border border-white/60 scale-105' 
                  : 'text-slate-600 hover:text-slate-900 hover:bg-white/40'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setActiveTab('store')}
              className={`md:hidden p-2 rounded-full transition-all ${activeTab === 'store' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-600 hover:bg-white/40'}`}
            >
              <ShoppingBag size={18} />
            </button>
            
            <div className="h-6 w-px bg-slate-300/50 mx-1"></div>

            {/* Cart Button */}
            <button 
              onClick={() => setIsBillingOpen(true)}
              className="relative p-2 text-slate-600 hover:text-emerald-600 hover:bg-white/40 rounded-full transition-all"
            >
              <ShoppingCart size={20} strokeWidth={2.5} />
              {cart.length > 0 && (
                <span className="absolute top-0 right-0 w-4 h-4 bg-emerald-500 text-white text-[10px] font-bold flex items-center justify-center rounded-full border-2 border-white/80 shadow-sm transform translate-x-1 -translate-y-1">
                  {cart.length}
                </span>
              )}
            </button>
            
            <button 
              onClick={handleReset}
              className="p-2 text-slate-500 hover:text-amber-500 hover:bg-white/40 rounded-full transition-colors"
              title="Reset Session"
            >
              <RotateCcw size={18} strokeWidth={2.5} />
            </button>
          </div>
        </nav>
      </div>
      {/* (Cart Drawer remains the same, assuming it's imported in App.jsx or handled via Context) */}
    </>
  );
};

export default Navbar;