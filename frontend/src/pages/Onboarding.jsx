import { useState } from 'react';
import { usePharmacy } from '../context/PharmacyContext';
import { ShieldCheck, User, Calendar, Baby, HeartPulse, CheckCircle2 } from 'lucide-react';

const Onboarding = () => {
  const { setPatient, setIsAuth } = usePharmacy();
  const [formData, setFormData] = useState({ firstName: '', lastName: '', age: '', terms: false });

  // Dynamic calculations for the safety banners
  const ageNum = parseInt(formData.age);
  const isPediatric = ageNum > 0 && ageNum < 18;
  const isSenior = ageNum >= 65;
  const isReady = formData.firstName && formData.lastName && formData.age && formData.terms;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isReady) {
      const mode = isPediatric ? 'pediatric' : isSenior ? 'senior' : 'standard';
      
      // Save patient to the global context
      setPatient({ 
        name: `${formData.firstName.trim()} ${formData.lastName.trim()}`, 
        age: ageNum, 
        mode 
      });
      // Unlock the app
      setIsAuth(true);
    }
  };

  return (
    <div className="glass-panel max-w-lg w-full p-8 md:p-10 shadow-2xl animate-in fade-in zoom-in-95 duration-500">
      <div className="flex flex-col items-center text-center mb-8">
        <div className="h-16 w-16 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-2xl flex items-center justify-center shadow-lg shadow-emerald-200 mb-6 transition-transform hover:scale-105">
          <ShieldCheck size={32} className="text-white" />
        </div>
        <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">Patient Intake</h1>
        <p className="text-slate-500 mt-2 font-medium">Secure AI Pharmacy Registration</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid grid-cols-2 gap-4">
          <div className="relative group">
            <User size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
            <input 
              type="text" required placeholder="First Name" 
              className="w-full bg-white/60 border border-white/50 pl-11 pr-4 py-3 rounded-xl text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 ring-emerald-400/50 shadow-sm transition-all"
              onChange={(e) => setFormData({...formData, firstName: e.target.value})}
            />
          </div>
          <div className="relative group">
            <input 
              type="text" required placeholder="Last Name" 
              className="w-full bg-white/60 border border-white/50 px-4 py-3 rounded-xl text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 ring-emerald-400/50 shadow-sm transition-all"
              onChange={(e) => setFormData({...formData, lastName: e.target.value})}
            />
          </div>
        </div>

        <div className="relative group">
          <Calendar size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
          <input 
            type="number" required placeholder="Age" min="1" max="120"
            className="w-full bg-white/60 border border-white/50 pl-11 pr-4 py-3 rounded-xl text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 ring-emerald-400/50 shadow-sm transition-all"
            onChange={(e) => setFormData({...formData, age: e.target.value})}
          />
        </div>

        {/* Dynamic Safety Banners */}
        <div className="min-h-[50px] transition-all duration-300">
          {isPediatric && (
            <div className="flex items-center gap-3 p-3 bg-blue-50/80 backdrop-blur-sm border border-blue-200 text-blue-700 rounded-xl text-sm font-semibold animate-in slide-in-from-top-2">
              <Baby size={20} className="text-blue-500" /> Pediatric Mode: Guardian supervision verified.
            </div>
          )}
          {isSenior && (
            <div className="flex items-center gap-3 p-3 bg-amber-50/80 backdrop-blur-sm border border-amber-200 text-amber-700 rounded-xl text-sm font-semibold animate-in slide-in-from-top-2">
              <HeartPulse size={20} className="text-amber-500" /> Senior Mode: Contraindication alerts boosted.
            </div>
          )}
        </div>

        <label className="flex items-start gap-3 cursor-pointer p-2 rounded-lg hover:bg-white/40 transition-colors">
          <div className="relative flex items-center mt-0.5">
            <input 
              type="checkbox" required
              className="peer w-5 h-5 appearance-none border-2 border-slate-300 rounded bg-white/50 checked:bg-emerald-500 checked:border-emerald-500 transition-all cursor-pointer"
              onChange={(e) => setFormData({...formData, terms: e.target.checked})} 
            />
            <CheckCircle2 size={16} className="absolute inset-0 m-auto text-white opacity-0 peer-checked:opacity-100 pointer-events-none transition-opacity" strokeWidth={3} />
          </div>
          <span className="text-sm text-slate-600 leading-snug font-medium">
            I acknowledge the <span className="text-emerald-600 hover:underline">Terms of Service</span> and consent to AI-assisted medical triage.
          </span>
        </label>

        <button 
          type="submit" 
          disabled={!isReady}
          className="w-full mt-4 bg-emerald-500 hover:bg-emerald-600 text-white p-4 rounded-xl font-bold text-lg shadow-xl shadow-emerald-500/20 transition-all disabled:opacity-50 disabled:hover:bg-emerald-500 disabled:cursor-not-allowed active:scale-[0.98]"
        >
          Initialize Session
        </button>
      </form>
    </div>
  );
};

export default Onboarding;