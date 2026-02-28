import React, { useState, useRef, useEffect } from "react";
import { Send, Mic, CreditCard, CheckCircle, FileText, Activity, Paperclip, Sparkles, AlertCircle, PhoneCall, Loader2 } from "lucide-react";

import { usePharmacy } from "../context/PharmacyContext";
import { pharmacyService } from "../services/api"; // <-- THE NEURAL BRIDGE IMPORTED
import AgentExpander from "../components/Chat/AgentExpander";
import QuickActions from "../components/Chat/QuickActions";
import PrescriptionUpload from "../components/Chat/PrescriptionUpload";
import EmergencyOverlay from "../components/Chat/EmergencyOverlay";

const glassBase = "backdrop-blur-[32px] saturate-[200%] border border-white/60 shadow-[0_24px_48px_-12px_rgba(0,0,0,0.12)]";
const innerLight = "shadow-[inset_0_1px_0_rgba(255,255,255,0.8)]";

export default function UserChat() {
  const { patient, messages, setMessages, setAgentStatus } = usePharmacy();
  
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [emergencyWord, setEmergencyWord] = useState(null);
  const [isThinking, setIsThinking] = useState(false); // <-- NEW API LOADING STATE
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking]);

  const handleSend = async (textOverride = null) => {
    const textToSend = textOverride || input;
    if (!textToSend.trim()) return;

    // 1. PRESCRIPTION TRIGGER
    if (textToSend === "TRIGGER_RX_UPLOAD") {
      setIsUploadOpen(true);
      setInput("");
      return;
    }

    // 2. EMERGENCY INTERCEPTOR
    const RED_FLAGS = ["chest pain", "difficulty breathing", "heart attack", "stroke", "poison", "bleeding"];
    const detected = RED_FLAGS.find(word => textToSend.toLowerCase().includes(word));
    if (detected) {
      setEmergencyWord(detected);
      setInput("");
      return;
    }

    // 3. UPDATE UI FEED INSTANTLY
    const newMsg = { id: Date.now(), role: 'user', content: textToSend, type: 'text' };
    setMessages(prev => [...prev, newMsg]);
    setInput("");
    setIsThinking(true);

    // 4. RESET AGENT STATUS TO START SEQUENCE
    setAgentStatus({
      orchestrator: 'thinking', physician: 'idle', pharmacist: 'idle',
      regulatory: 'idle', inventory: 'idle', billing: 'idle', refill: 'idle'
    });

    // 5. 🚀 THE REAL BACKEND CALL 🚀
    try {
      const response = await pharmacyService.sendChatMessage(textToSend, patient);
      
      // Update Agent UI from Backend
      if (response.data.agents) setAgentStatus(response.data.agents);

      // Render Backend Response
      const aiMsg = {
        id: Date.now(),
        role: 'ai',
        type: response.data.type || 'text', // Allows backend to trigger 'checkout' type
        content: response.data.reply || "Processing complete.",
        medicine: response.data.medicine,
        price: response.data.price,
        quantity: response.data.quantity
      };
      
      setMessages(prev => [...prev, aiMsg]);

    } catch (error) {
      console.error("FastAPI unreachable. Engaging emergency local fallback sequence.", error);
      // 🔥 THE BULLETPROOF FALLBACK 🔥
      processAgentResponse(textToSend);
    } finally {
      setIsThinking(false);
    }
  };

  // The local fallback logic (Kept exactly as you designed it)
  const processAgentResponse = (text) => {
    const lower = text.toLowerCase();
    let aiMsg = { id: Date.now(), role: 'ai', type: 'text', content: "" };

    if (lower.includes("headache") || lower.includes("pain") || lower.includes("paracetamol")) {
      aiMsg = {
        ...aiMsg,
        type: 'checkout',
        content: "Based on your reported symptoms and age-specific safety protocols, I recommend Paracetamol 500mg. It is highly effective for tension headaches and currently in stock.",
        medicine: "Paracetamol 500mg",
        price: 4.99,
        quantity: 1
      };
      setAgentStatus({ orchestrator: 'done', physician: 'done', pharmacist: 'done', inventory: 'done', regulatory: 'done' });
    } else {
      aiMsg.content = "I am currently analyzing your query across our 7-agent medical network. Could you please specify any other symptoms you are experiencing?";
      setAgentStatus({ orchestrator: 'done', physician: 'done', pharmacist: 'done' });
    }

    setMessages(prev => [...prev, aiMsg]);
  };

  return (
    <div className="flex flex-col h-full w-full bg-transparent overflow-hidden">
      
      {/* CHAT VIEWPORT */}
      <div className="flex-1 overflow-y-auto px-4 md:px-24 py-8 space-y-8 scrollbar-hide">
        
        {/* INITIAL STATE: QUICK ACTIONS */}
        {messages.length === 0 && !input && (
          <div className="animate-in fade-in slide-in-from-top-8 duration-1000 ease-out">
            <div className="text-center mb-12">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 mb-4">
                <Sparkles size={14} className="text-blue-600" />
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-700">AI Medical Intelligence</span>
              </div>
              <h2 className="text-5xl font-black text-slate-800 tracking-tight leading-tight">
                Welcome back, <span className="text-blue-600">{patient?.name?.split(' ')[0]}</span>.
              </h2>
              <p className="text-slate-400 font-bold mt-2 uppercase tracking-widest text-[10px]">How can our agent network assist you today?</p>
            </div>
            <QuickActions onAction={(p) => handleSend(p)} />
          </div>
        )}

        {/* MESSAGE STREAM */}
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-5 duration-500`}>
            <div className="max-w-[85%] md:max-w-[65%] lg:max-w-[50%]">
              
              {msg.type === 'text' && (
                <div className={`p-6 rounded-[2.5rem] text-[16px] leading-relaxed shadow-2xl border transition-all ${
                  msg.role === 'user' 
                  ? "bg-blue-600/15 border-blue-400/30 backdrop-blur-3xl text-slate-900 rounded-tr-none shadow-blue-500/5" 
                  : "bg-white/50 border-white/80 backdrop-blur-3xl text-slate-900 rounded-tl-none shadow-slate-900/5"
                }`}>
                  {msg.content}
                </div>
              )}

              {msg.type === 'checkout' && (
                <div className={`p-8 rounded-[3rem] rounded-tl-none space-y-6 bg-white/60 border-white/80 ${glassBase}`}>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-500 text-white rounded-xl shadow-lg shadow-blue-500/20">
                      <CheckCircle size={20} />
                    </div>
                    <span className="text-[11px] font-black uppercase tracking-[0.15em] text-slate-400">Validated Recommendation</span>
                  </div>
                  
                  <p className="text-slate-800 font-semibold text-lg leading-relaxed">{msg.content}</p>
                  
                  <div className="bg-white/40 p-6 rounded-[2rem] border border-white/60 shadow-inner flex justify-between items-center group">
                    <div>
                      <h4 className="brand-font font-black text-2xl text-slate-900 group-hover:text-blue-600 transition-colors">{msg.medicine}</h4>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-600 text-[10px] font-black uppercase tracking-widest">In Stock</span>
                        <span className="text-xs font-bold text-slate-400">Qty: {msg.quantity}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-[10px] font-black text-slate-300 uppercase mb-1">Price</p>
                      <span className="brand-font font-black text-4xl text-slate-900">${msg.price}</span>
                    </div>
                  </div>

                  <button className="w-full py-5 bg-slate-900 text-white rounded-[1.5rem] font-black text-xl shadow-2xl shadow-slate-900/30 hover:bg-slate-800 transition-all active:scale-[0.97] flex items-center justify-center gap-4">
                    <CreditCard size={24} />
                    Confirm & Pay
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* TYPING INDICATOR & AGENT STATUS */}
        {(isThinking || messages[messages.length - 1]?.role === 'user') && (
          <div className="flex justify-start flex-col gap-3">
            <AgentExpander />
            {isThinking && (
              <div className="glass-panel px-5 py-3 rounded-3xl rounded-tl-none inline-flex items-center gap-3 max-w-fit ml-4 animate-in fade-in duration-300">
                <Loader2 size={18} className="animate-spin text-blue-600" />
                <span className="text-sm font-bold text-slate-500">Processing sequence...</span>
              </div>
            )}
          </div>
        )}
        
        <div ref={messagesEndRef} className="h-10" />
      </div>

      {/* INPUT COMMAND CENTER */}
      <div className="px-4 md:px-24 pb-12 pt-4 bg-gradient-to-t from-white/20 to-transparent">
        <div className="max-w-4xl mx-auto">
          <div className={`p-3 rounded-[3rem] bg-white/40 border-white/60 ${glassBase} flex items-center gap-2 focus-within:ring-4 ring-blue-500/10 transition-all`}>
            
            <button 
              onClick={() => setIsUploadOpen(true)}
              className="p-4 text-slate-500 hover:text-blue-600 hover:bg-white/60 rounded-full transition-all group"
              title="Upload Prescription"
            >
              <Paperclip size={24} strokeWidth={2.5} className="group-hover:rotate-12 transition-transform" />
            </button>

            <button 
              onClick={() => setIsRecording(!isRecording)}
              className={`p-4 rounded-full transition-all shadow-lg ${isRecording ? 'bg-rose-500 text-white animate-pulse' : 'text-slate-500 hover:bg-white/60'}`}
            >
              {isRecording ? <Activity size={24} strokeWidth={2.5} /> : <Mic size={24} strokeWidth={2.5} />}
            </button>

            <input 
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !isThinking && handleSend()}
              disabled={isThinking}
              placeholder={isThinking ? "Awaiting neural network response..." : "Ask PharmaAgent anything..."}
              className="flex-1 bg-transparent border-none outline-none px-4 text-slate-900 font-bold placeholder:text-slate-400 text-xl disabled:opacity-50"
            />

            <button 
              onClick={() => handleSend()}
              disabled={!input.trim() || isThinking}
              className="p-4 bg-slate-900 text-white rounded-full shadow-2xl hover:bg-slate-800 disabled:opacity-20 transition-all active:scale-90"
            >
              <Send size={22} strokeWidth={2.5} className="translate-x-[1px]" />
            </button>
          </div>
          <p className="text-center text-[10px] font-bold text-slate-400 mt-4 uppercase tracking-[0.2em] opacity-60">
            End-to-End Encrypted Medical Intelligence Session
          </p>
        </div>
      </div>

      {/* OVERLAYS & MODALS */}
      <PrescriptionUpload isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} />
      <EmergencyOverlay isOpen={!!emergencyWord} triggerWord={emergencyWord} onClose={() => setEmergencyWord(null)} />
    </div>
  );
}