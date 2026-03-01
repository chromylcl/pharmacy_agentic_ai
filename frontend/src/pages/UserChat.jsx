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
  Volume2,
  VolumeX,
  ChevronDown,
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
  const { patient, setPatient, messages, setMessages, setAgentStatus, setCart, setIsBillingOpen, setActiveTab } = usePharmacy();

  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [emergencyWord, setEmergencyWord] = useState(null);
  const [isThinking, setIsThinking] = useState(false);
  const [pendingMedicine, setPendingMedicine] = useState(null);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);

  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  // Handle Speech Recognition Setup
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition && !recognitionRef.current) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = false;

      recognition.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          setInput(prev => (prev + " " + finalTranscript).trim());
        }
      };

      recognition.onerror = (e) => {
        console.error("Speech Recognition Error:", e);
        setIsRecording(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  useEffect(() => {
    if (recognitionRef.current) {
      if (isRecording) {
        try { recognitionRef.current.start(); } catch (e) { }
      } else {
        try { recognitionRef.current.stop(); } catch (e) { }
      }
    }
  }, [isRecording]);

  const speakText = (text) => {
    if (!isAudioEnabled || !text) return;
    window.speechSynthesis.cancel(); // stop previous
    let cleanText = String(text).replace(/Option [A|B|C|D|E|F|G|H]:/g, "").replace(/\*\*/g, "").replace(/🚨/g, "").replace(/\[.*?\]/g, "");
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  };

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

        if (backend.type === "order_success" || backend.type === "checkout") {
          aiMsg.type = "checkout";
          aiMsg.medicine = backend.data?.product;
          aiMsg.quantity = backend.data?.quantity;
          aiMsg.price = backend.data?.total_price || 0;
          setPendingMedicine(null);
        }

        aiMsg.trace = backend.trace || [];
        setMessages((prev) => [...prev, aiMsg]);
        setIsThinking(false);
        speakText(aiMsg.content);
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
        recommendations: backend.recommendations || [],
        trace: backend.trace || []
      };

      if (backend.recommendations && backend.recommendations.length > 0) {
        setPatient(prev => ({ ...prev, symptom: textToSend }));
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

      if (backend.type === "order_success" || backend.type === "checkout") {
        aiMsg.type = "checkout";
        aiMsg.medicine = backend.data?.product || "Medicine";
        aiMsg.quantity = backend.data?.quantity || 1;
        aiMsg.price = backend.data?.total_price || "0.00";
      }

      setMessages((prev) => [...prev, aiMsg]);
      speakText(aiMsg.content);
    } catch (error) {
      console.error("Backend error:", error);
      setMessages((prev) => [...prev, {
        id: Date.now(),
        role: "ai",
        type: "error",
        content: "Oops! We encountered a system error connecting to the AI brain.",
      }]);
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
      content: `✅ Successfully added ${msg.quantity}x ${msg.medicine} to your cart.`
    }]);
    speakText(`Successfully added to your cart!`);
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

            <QuickActions onAction={(p) => {
              if (p === 'TRIGGER_RX_UPLOAD') {
                setIsUploadOpen(true);
              } else if (p === 'TRIGGER_GO_TO_STORE') {
                setActiveTab('store');
              } else {
                handleSend(p);
              }
            }} />
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"
              }`}
          >
            <div className="max-w-[85%] md:max-w-[65%] lg:max-w-[50%]">
              {/* NORMAL TEXT */}
              {(msg.type === "text" || msg.type === "ask_quantity" || msg.type === "error" || msg.type === "checkout_prompt") && (
                <div
                  className={`p-6 rounded-[2.5rem] text-[16px] shadow-xl ${msg.role === "user"
                    ? "bg-blue-600/15 border-blue-400/30 backdrop-blur-3xl rounded-tr-none"
                    : "bg-white/50 border-white/80 backdrop-blur-3xl rounded-tl-none"
                    }`}
                >
                  {/* MULTI-AGENT THINKING TRACE */}
                  {msg.trace && msg.trace.length > 0 && (
                    <details className="mb-5 overflow-hidden rounded-2xl border border-white/60 bg-white/40 backdrop-blur-[40px] saturate-[200%] shadow-[0_8px_32px_-8px_rgba(0,0,0,0.1)] group transition-all duration-500">
                      <summary className="p-3 bg-white/50 border-b border-white/40 flex items-center justify-between cursor-pointer list-none appearance-none hover:bg-white/60 transition-colors [&::-webkit-details-marker]:hidden outline-none">
                        <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-slate-600">
                          <Activity size={12} className="text-purple-500 group-open:animate-pulse" /> Orchestrator Reasoning Pathway
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-[9px] font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">{msg.trace.length} Steps</span>
                          <ChevronDown size={14} className="text-slate-400 group-open:rotate-180 transition-transform duration-300" />
                        </div>
                      </summary>
                      <div className="p-4 space-y-2.5 bg-gradient-to-b from-white/30 to-white/10 max-h-56 overflow-y-auto animate-in slide-in-from-top-2 duration-300">
                        {msg.trace.map((step, i) => (
                          <div key={i} className="flex items-start gap-3 text-[11.5px] text-slate-700 font-mono leading-relaxed">
                            <span className="text-purple-500 font-black select-none mt-0.5 opacity-80">[{i + 1}]</span>
                            {(() => {
                              const match = step.match(/^\[(.*?)\] (.*)$/);
                              if (match) {
                                const [, agent, text] = match;
                                let badgeColor = "bg-slate-200 text-slate-700";
                                if (agent === "Orchestrator") badgeColor = "bg-blue-100 text-blue-700 border-blue-200";
                                else if (agent === "Intent Agent") badgeColor = "bg-emerald-100 text-emerald-700 border-emerald-200";
                                else if (agent === "Master Agent") badgeColor = "bg-purple-100 text-purple-700 border-purple-200";
                                else if (agent === "Action Agent") badgeColor = "bg-amber-100 text-amber-700 border-amber-200";
                                else if (agent === "Semantic Matcher" || agent.includes("Database")) badgeColor = "bg-slate-100 text-slate-600 border-slate-200";

                                return (
                                  <span className="flex-1">
                                    <span className={`inline-block border px-1.5 py-0.5 rounded-md text-[9px] font-bold uppercase tracking-wider mr-2 shadow-sm ${badgeColor}`}>
                                      {agent}
                                    </span>
                                    <span>{text}</span>
                                  </span>
                                );
                              }
                              return <span className="flex-1">{step}</span>;
                            })()}
                          </div>
                        ))}
                      </div>
                    </details>
                  )}

                  <p className="whitespace-pre-wrap">{msg.content}</p>

                  {/* CHECKOUT PROMPT ACTIONS */}
                  {msg.type === "checkout_prompt" && msg.role === "ai" && (
                    <div className="mt-6 flex">
                      <button
                        onClick={() => setIsBillingOpen(true)}
                        className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white font-black py-4 px-6 rounded-2xl transition-all shadow-xl shadow-emerald-500/30 active:scale-95 flex items-center justify-center gap-2"
                      >
                        <CreditCard size={18} />
                        Confirm Purchase & Secure Billing
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
                              onClick={() => handleAddToCart({
                                medicine: med.name,
                                quantity: 1,
                                price: med.price || 0
                              })}
                              className="mt-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold py-1.5 px-4 rounded-full transition-colors flex items-center gap-1"
                            >
                              <ShoppingCart size={12} />
                              Add to Cart
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
                  {(msg.content || "").includes("Partially") || (msg.content || "").includes("Partial") ? (
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
              onClick={() => setIsAudioEnabled(!isAudioEnabled)}
              className={`p-4 transition-colors ${isAudioEnabled ? 'text-blue-600' : 'text-slate-400'}`}
              title="Toggle AI Voice"
            >
              {isAudioEnabled ? <Volume2 size={22} /> : <VolumeX size={22} />}
            </button>

            <button
              onClick={() => setIsUploadOpen(true)}
              className="p-4 text-slate-500 hover:text-blue-600"
            >
              <Paperclip size={22} />
            </button>

            <button
              onClick={() => setIsRecording(!isRecording)}
              className={`p-4 transition-colors ${isRecording ? 'text-rose-500 animate-pulse' : 'text-slate-500 hover:text-blue-600'}`}
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
          setPatient(prev => ({ ...prev, prescription: filename }));
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
