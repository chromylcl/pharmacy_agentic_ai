import React, { useRef, useState } from 'react';
import { usePharmacy } from '../../context/PharmacyContext';
import { Download, CreditCard, X, CheckCircle, FileText, AlertTriangle } from 'lucide-react';
import axios from 'axios';

export default function BillingModal({ isOpen, onClose }) {
  const { cart, patient, setCart, setMessages, setRefreshTrigger } = usePharmacy();
  const [isSuccess, setIsSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const printRef = useRef(null);

  if (!isOpen) return null;

  const total = cart.reduce((acc, item) => acc + (parseFloat(item.price) * parseInt(item.quantity || 1)), 0);

  const handlePrint = () => {
    window.print();
  };

  const handleConfirm = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const payload = {
        patient_id: patient?.id || "unknown",
        items: cart.map(item => ({
          name: item.name,
          quantity: item.quantity || 1,
          confirmed_overdose: item.confirmed_overdose || false
        }))
      };

      const res = await axios.post('http://localhost:8000/finalize-checkout', payload);

      setIsSuccess(true);
      setTimeout(() => {
        setCart([]);
        setRefreshTrigger(prev => prev + 1);
        setIsSuccess(false);
        onClose();
        setMessages(prev => [...prev, {
          id: Date.now(),
          role: "ai",
          type: "text",
          content: "Your order has been placed successfully! The pharmacy team will prepare it shortly."
        }]);
      }, 7000); // Wait 7s so the success message / printed reciept is fully shown

    } catch (err) {
      setErrorMsg(err.response?.data?.detail || "Checkout blocked by Safety rules or insufficient stock");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex justify-center p-4 sm:p-6 bg-slate-900/40 backdrop-blur-md">
      <div className="w-full max-w-2xl rounded-[2.5rem] shadow-[0_24px_48px_-12px_rgba(0,0,0,0.1)] bg-white/50 backdrop-blur-[40px] saturate-[200%] border border-white/60 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-slate-100 print:hidden">
          <h2 className="text-2xl font-black text-slate-800 flex items-center gap-2">
            <CreditCard className="text-blue-600" /> Secure Medical Checkout
          </h2>
          {!isSuccess && (
            <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors">
              <X className="text-slate-500" />
            </button>
          )}
        </div>

        {errorMsg && (
          <div className="mx-6 mt-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl font-medium animate-pulse">
            🚨 {errorMsg}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 sm:p-8 relative">
          {isSuccess ? (
            <div className="absolute inset-0 bg-white/60 backdrop-blur-[40px] z-10 flex flex-col items-center justify-center p-8 text-center animate-in fade-in duration-500">
              <div className="w-24 h-24 bg-emerald-100 rounded-full flex items-center justify-center mb-6 shadow-[0_0_40px_rgba(16,185,129,0.3)]">
                <CheckCircle size={48} className="text-emerald-500" />
              </div>
              <h2 className="text-3xl font-black text-slate-800 mb-2">Checkout & Medical Clearance Successful!</h2>
              <p className="text-slate-600 font-medium">Your total of ${total.toFixed(2)} has been charged and audit trails are logged. Check your printed invoice for dosage guides.</p>
              <button onClick={() => { setCart([]); setIsSuccess(false); onClose(); }} className="mt-8 px-10 py-4 bg-emerald-500 text-white font-black rounded-2xl shadow-xl shadow-emerald-500/30 hover:bg-emerald-600 transition-all active:scale-95">Complete Transaction</button>
            </div>
          ) : (
            <div ref={printRef} className="print-section max-w-full bg-white/40 p-6 rounded-3xl border border-white/60 shadow-sm">
              {/* Receipt Header (visible inside print) */}
              <div className="mb-8 pb-8 border-b-2 border-dashed border-slate-200">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-emerald-100 p-2 rounded-xl h-12 w-12 flex items-center justify-center">
                    <img src="/vite.svg" alt="Pharmacy Logo" className="w-8 h-8 opacity-80" style={{ filter: 'hue-rotate(150deg)' }} />
                  </div>
                  <h1 className="text-3xl font-black text-slate-800 tracking-tight">
                    Pharma<span className="text-emerald-600">Agent</span>
                  </h1>
                </div>
                <p className="text-sm text-slate-500 font-medium">Official Medical Invoice</p>
                <div className="mt-6 grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Patient Name</h4>
                    <p className="text-slate-800 font-bold">{patient?.name || "Guest User"}</p>
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Invoice Date</h4>
                    <p className="text-slate-800 font-bold">{new Date().toLocaleDateString()}</p>
                  </div>
                </div>
              </div>

              {/* Order Items */}
              <div className="space-y-4 mb-8">
                <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-4">
                  <FileText size={18} className="text-blue-500" /> Approved Medications & Guidance
                </h3>
                {cart.length === 0 ? (
                  <p className="text-sm text-slate-500 italic">No medicinal items present.</p>
                ) : (
                  cart.map((item, idx) => {
                    const qty = item.quantity || 1;
                    const nextDate = new Date();
                    nextDate.setDate(nextDate.getDate() + qty); // assume frequency 1 per day

                    return (
                      <div key={idx} className="flex flex-col p-4 bg-slate-50 rounded-2xl border border-slate-100 print:bg-transparent print:p-2 print:border-b print:rounded-none mb-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h4 className="font-bold text-slate-800">{item.name}</h4>
                            <p className="text-xs text-slate-500 mt-1">Qty: {qty}</p>
                          </div>
                          <div className="font-black text-slate-800">
                            ${(parseFloat(item.price) * qty).toFixed(2)}
                          </div>
                        </div>
                        <div className="bg-white p-3 rounded-lg border border-slate-100 print:border-none text-xs text-slate-600 space-y-1 mt-2 shadow-sm">
                          <p><strong className="text-slate-800">Dosage Instructions:</strong> {item.prescription_required ? "Strictly as prescribed by physician." : "Take 1 unit with water after meals."}</p>
                          <p><strong className="text-slate-800">Frequency:</strong> Once daily</p>
                          <p><strong className="text-slate-800">Next Recommended Purchase:</strong> {nextDate.toLocaleDateString()}</p>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              {/* Medical Safety Disclaimer */}
              {cart.length > 0 && (
                <div className="mb-8 p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 text-xs flex items-start gap-3 print:border border-amber-300">
                  <AlertTriangle size={24} className="shrink-0 text-amber-500 mt-0.5" />
                  <p className="leading-relaxed"><strong>Mandatory Safety Disclaimer:</strong> This medical invoice serves as a permanent secure record of your purchase. Always strictly follow the prescribed dosage. The recommended next purchase date is an estimate based on standard daily consumption. Do not exceed the maximum safe dosage. Prioritize your health and consult a certified physician if you experience any adverse effects. Non-compliant use is at your own risk.</p>
                </div>
              )}

              {/* Totals */}
              <div className="bg-slate-50 rounded-3xl p-6 border border-slate-100 print:bg-transparent print:border-t-2 print:rounded-none print:border-slate-800 relative overflow-hidden mt-4">
                <div className="absolute -right-8 -top-8 text-emerald-500/10 font-black text-8xl -rotate-12 pointer-events-none print:text-emerald-500/20">
                  PAID
                </div>
                <div className="flex justify-between items-center text-slate-600 mb-2 relative z-10">
                  <span>Subtotal</span>
                  <span className="font-bold">${total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center text-slate-600 mb-4 pb-4 border-b border-slate-200 relative z-10">
                  <span>Audit & Safety Fee</span>
                  <span className="font-bold">$0.00</span>
                </div>
                <div className="flex justify-between items-end relative z-10">
                  <span className="text-lg font-bold text-slate-800">Total Amount</span>
                  <span className="text-4xl font-black text-blue-600">${total.toFixed(2)}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        {!isSuccess && (
          <div className="p-6 bg-white/30 backdrop-blur-md border-t border-white/60 flex gap-4 print:hidden shrink-0">
            <button
              onClick={handlePrint}
              disabled={loading || cart.length === 0}
              className="px-6 py-4 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-2xl transition-colors flex items-center gap-2 group disabled:opacity-50"
            >
              <Download size={18} className="group-hover:-translate-y-1 transition-transform" /> Print Bill
            </button>
            <button
              onClick={handleConfirm}
              disabled={loading || cart.length === 0}
              className="flex-1 px-6 py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-2xl transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50 active:scale-[0.98] flex justify-center items-center"
            >
              {loading ? (
                <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              ) : (
                "Pass Security Audit & Confirm"
              )}
            </button>
          </div>
        )}
      </div>

      <style dangerouslySetInnerHTML={{
        __html: `
        @media print {
          body * { visibility: hidden; }
          .print-section, .print-section * { visibility: visible; }
          .print-section { position: absolute; left: 0; top: 0; width: 100%; padding: 40px; }
        }
      `}} />
    </div>
  );
}
