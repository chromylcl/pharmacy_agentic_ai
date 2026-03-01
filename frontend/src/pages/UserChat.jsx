import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Mic,
  CreditCard,
  CheckCircle,
  Activity,
  Paperclip,
  Sparkles,
  Loader2,
  AlertCircle,
  ShoppingCart,
} from "lucide-react";

import { usePharmacy } from "../context/PharmacyContext";
import { pharmacyService } from "../services/api";
import AgentExpander from "../components/Chat/AgentExpander";
import QuickActions from "../components/Chat/QuickActions";
import PrescriptionUpload from "../components/Chat/PrescriptionUpload";
import EmergencyOverlay from "../components/Chat/EmergencyOverlay";

const glassBase =
  "backdrop-blur-[32px] saturate-[200%] border border-white/60 shadow-[0_24px_48px_-12px_rgba(0,0,0,0.12)]";

export default function UserChat() {
  const { patient, setPatient, messages, setMessages, setAgentStatus, setCart, setIsBillingOpen } = usePharmacy();

  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [emergencyWord, setEmergencyWord] = useState(null);
  const [isThinking, setIsThinking] = useState(false);
  const [pendingMedicine, setPendingMedicine] = useState(null);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  const handleSend = async (textOverride = null) => {
    const textToSend = textOverride || input;
    if (!textToSend.trim()) return;

    const newMsg = {
      id: Date.now(),
      role: "user",
      content: textToSend,
      type: "text",
    };

    setMessages((prev) => [...prev, newMsg]);
    setInput("");
    setIsThinking(true);

    try {
      // 🔁 QUANTITY FLOW
      if (pendingMedicine && !isNaN(textToSend)) {
        const response = await pharmacyService.sendQuantity(
          patient.name,
          pendingMedicine,
          parseInt(textToSend),
        );

        const backend = response.data;

        let aiMsg = {
          id: Date.now(),
          role: "ai",
          type: "text",
          content: backend.message || backend.reply,
        };
        if (backend.type === "stock_error") {
          aiMsg.type = "text";
        }
        if (backend.type === "prescription_required") {
          aiMsg.type = "text";
          setIsUploadOpen(true);
        }

        if (backend.type === "safety_block") {
          aiMsg.type = "text";
        }
        if (backend.type === "order_success") {
          aiMsg.type = "checkout";
          aiMsg.medicine = backend.data?.product;
          aiMsg.quantity = backend.data?.quantity;
          aiMsg.price = backend.data?.total_price;
          setPendingMedicine(null);
        }

        setMessages((prev) => [...prev, aiMsg]);
        setIsThinking(false);
        return;
      }

      // 🔵 NORMAL CHAT
      const response = await pharmacyService.sendChatMessage(
        textToSend,
        patient,
      );

      const backend = response.data;

      if (backend.agents) setAgentStatus(backend.agents);

      let aiMsg = {
        id: Date.now(),
        role: "ai",
        type: backend.type || "text",
        content: backend.message,
        recommendations: backend.recommendations || []
      };

      if (backend.recommendations && backend.recommendations.length > 0) {
        setPatient(prev => ({...prev, symptom: textToSend}));
      }

      if (backend.type === "ask_quantity") {
        setPendingMedicine(backend.medicine);
      }

      if (backend.type === "stock_error") {
        aiMsg.type = "text";
      }

      if (backend.type === "prescription_required") {
        aiMsg.type = "text";
        if (backend.medicine) {
            setPendingMedicine(backend.medicine);
        }
        setIsUploadOpen(true);
      }

      if (backend.type === "safety_block") {
        aiMsg.type = "text";
      }

      if (backend.type === "order_success") {
        aiMsg.type = "checkout";
        aiMsg.medicine = backend.data?.product || "Medicine";
        aiMsg.quantity = backend.data?.quantity || 1;
        aiMsg.price = backend.data?.total_price || "0.00";
      }

      setMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      console.error("Backend error:", error);
    }

    setIsThinking(false);
  };

  const handleAddToCart = (msg) => {
    const newItem = {
      id: Date.now(),
      name: msg.medicine,
      quantity: msg.quantity,
      price: msg.price
    };
    setCart(prev => [...prev, newItem]);
    
    setMessages(prev => [...prev, {
      id: Date.now() + 1,
      role: "ai",
      type: "text",
      content: `Successfully added ${msg.quantity}x ${msg.medicine} to your cart! Is there anything else you need today?`
    }]);
  };

  return (
    <div className="flex flex-col h-full w-full bg-transparent overflow-hidden">
      {/* CHAT AREA */}
      <div className="flex-1 overflow-y-auto px-4 md:px-24 py-8 space-y-8 scrollbar-hide">
        {messages.length === 0 && (
          <div className="text-center mb-12 animate-in fade-in slide-in-from-top-8 duration-700">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 mb-4">
              <Sparkles size={14} className="text-blue-600" />
              <span className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-700">
                AI Medical Intelligence
              </span>
            </div>

            <h2 className="text-5xl font-black text-slate-800">
              Welcome back,{" "}
              <span className="text-blue-600">
                {patient?.name?.split(" ")[0]}
              </span>
            </h2>

            <QuickActions onAction={(p) => handleSend(p)} />
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div className="max-w-[85%] md:max-w-[65%] lg:max-w-[50%]">
              {/* NORMAL TEXT */}
              {(msg.type === "text" || msg.type === "ask_quantity" || msg.type === "error" || msg.type === "checkout_prompt") && (
                <div
                  className={`p-6 rounded-[2.5rem] text-[16px] shadow-xl ${
                    msg.role === "user"
                      ? "bg-blue-600/15 border-blue-400/30 backdrop-blur-3xl rounded-tr-none"
                      : "bg-white/50 border-white/80 backdrop-blur-3xl rounded-tl-none"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>

                  {/* CHECKOUT PROMPT ACTIONS */}
                  {msg.type === "checkout_prompt" && msg.role === "ai" && (
                    <div className="mt-6 flex">
                      <button
                        onClick={() => setIsBillingOpen(true)}
                        className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 px-4 rounded-2xl transition-all shadow-md active:scale-95 flex items-center justify-center gap-2"
                      >
                        <CreditCard size={18} />
                        Confirm Purchase & Billing
                      </button>
                    </div>
                  )}

                  {/* CONFIRMATION ACTIONS */}
                  {msg.content?.includes("Option A") && msg.role === "ai" && (
                    <div className="mt-6 flex flex-col sm:flex-row gap-3">
                      <button
                        onClick={() => handleSend("Option A")}
                        className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 px-4 rounded-2xl transition-all shadow-md active:scale-95"
                      >
                        Proceed To Checkout
                      </button>
                      <button
                        onClick={() => handleSend("Option B")}
                        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-2xl transition-all shadow-md active:scale-95"
                      >
                        Modify Order
                      </button>
                      <button
                        onClick={() => handleSend("Option C")}
                        className="flex-1 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold py-3 px-4 rounded-2xl transition-all shadow-md active:scale-95"
                      >
                        Cancel
                      </button>
                    </div>
                  )}
                  
                  {/* RECOMMENDATIONS CARDS */}
                  {msg.recommendations && msg.recommendations.length > 0 && (
                    <div className="mt-4 flex flex-col gap-3">
                      {msg.recommendations.map(med => (
                        <div key={med.id} className="bg-white/80 p-4 rounded-2xl flex justify-between items-center shadow-sm hover:shadow-md transition-shadow">
                          <div className="flex-1">
                            <h5 className="font-bold text-slate-800">{med.name}</h5>
                            <p className="text-xs text-slate-500 mt-1 max-w-[200px] leading-tight">{med.reason}</p>
                          </div>
                          <div className="text-right ml-4 flex flex-col items-end justify-between gap-2 h-full">
                            <div>
                                <span className="font-black text-blue-600 block">${(med.price || 0).toFixed(2)}</span>
                                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${med.stock > 0 ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                                  {med.stock > 0 ? 'In Stock' : 'Out'}
                                </span>
                            </div>
                            <button
                              onClick={() => handleSend(`I want to buy ${med.name}`)}
                              className="mt-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold py-1.5 px-4 rounded-full transition-colors flex items-center gap-1"
                            >
                              <ShoppingCart size={12} />
                              Order
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* CHECKOUT CARD */}
              {msg.type === "checkout" && (
                <div className="p-8 rounded-[3rem] rounded-tl-none space-y-6 bg-white/60 border-white/80 backdrop-blur-3xl shadow-xl">
                  {msg.content.includes("Partially Approved") ? (
                    <div className="flex flex-col gap-2">
                       <div className="flex items-center gap-3">
                         <AlertCircle size={20} className="text-amber-500" />
                         <span className="text-sm font-bold text-amber-600">
                           Partial Approval
                         </span>
                       </div>
                       <p className="text-sm text-slate-600 mb-2">{msg.content}</p>
                    </div>
                  ) : (
                    <div className="flex flex-col gap-2">
                      <div className="flex items-center gap-3">
                        <CheckCircle size={20} className="text-emerald-500" />
                        <span className="text-sm font-bold text-slate-500">
                          Product Approved
                        </span>
                      </div>
                      <p className="text-sm text-slate-600 mb-2">{msg.content}</p>
                    </div>
                  )}

                  <div className="flex justify-between items-center p-4 bg-white/50 rounded-2xl border border-slate-100 mb-4">
                    <div>
                      <h4 className="font-black text-xl text-slate-800">{msg.medicine}</h4>
                      <p className="text-sm font-bold text-slate-500">
                        Qty Approved: {msg.quantity}
                      </p>
                    </div>
                    <div className="text-2xl font-black text-blue-600">€{msg.price}</div>
                  </div>

                  {/* CART ACTIONS */}
                  <div className="flex gap-4">
                    <button 
                      onClick={() => handleAddToCart(msg)}
                      className="flex-1 py-4 px-6 bg-blue-50 text-blue-600 font-bold rounded-2xl hover:bg-blue-100 transition-colors"
                    >
                      Add to Cart
                    </button>
                    <button 
                      onClick={() => {
                        handleAddToCart(msg);
                        setIsBillingOpen(true);
                      }}
                      className="flex-1 py-4 px-6 bg-slate-900 text-white font-bold rounded-2xl hover:bg-slate-800 transition-colors shadow-lg"
                    >
                      Buy Now
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Typing Indicator */}
        {isThinking && (
          <div className="flex justify-start">
            <div className="glass-panel px-5 py-3 rounded-3xl rounded-tl-none inline-flex items-center gap-3 ml-4">
              <Loader2 size={18} className="animate-spin text-blue-600" />
              <span className="text-sm font-bold text-slate-500">
                Processing...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* INPUT */}
      <div className="px-4 md:px-24 pb-12 pt-4 bg-gradient-to-t from-white/20 to-transparent">
        <div className="max-w-4xl mx-auto">
          <div
            className={`p-3 rounded-[3rem] bg-white/40 border-white/60 ${glassBase} flex items-center gap-2`}
          >
            <button
              onClick={() => setIsUploadOpen(true)}
              className="p-4 text-slate-500 hover:text-blue-600"
            >
              <Paperclip size={22} />
            </button>

            <button
              onClick={() => setIsRecording(!isRecording)}
              className="p-4 text-slate-500 hover:text-blue-600"
            >
              {isRecording ? <Activity size={22} /> : <Mic size={22} />}
            </button>

            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) =>
                e.key === "Enter" && !isThinking && handleSend()
              }
              disabled={isThinking}
              placeholder="Ask PharmaAgent anything..."
              className="flex-1 bg-transparent outline-none px-4 text-xl font-bold"
            />

            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || isThinking}
              className="p-4 bg-slate-900 text-white rounded-full hover:bg-slate-800 transition-all"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>

      <PrescriptionUpload
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        medicineName={pendingMedicine}
        userId={patient?.name || "test_user"}
        onUploadComplete={(filename) => {
          setIsUploadOpen(false);
          setPatient(prev => ({...prev, prescription: filename}));
          setPendingMedicine(null);
          handleSend(`[Prescription Uploaded]: I have provided my prescription.`);
        }}
      />
      <EmergencyOverlay
        isOpen={!!emergencyWord}
        triggerWord={emergencyWord}
        onClose={() => setEmergencyWord(null)}
      />
    </div>
  );
}
