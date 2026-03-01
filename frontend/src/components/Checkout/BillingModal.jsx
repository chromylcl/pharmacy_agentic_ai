import React, { useRef } from 'react';
import { usePharmacy } from '../../context/PharmacyContext';
import { Download, CreditCard, X, CheckCircle, FileText } from 'lucide-react';

export default function BillingModal({ isOpen, onClose }) {
  const { cart, patient, setCart, setMessages } = usePharmacy();
  const [isSuccess, setIsSuccess] = React.useState(false);
  const printRef = useRef(null);

  if (!isOpen) return null;

  const total = cart.reduce((acc, item) => acc + (parseFloat(item.price) * parseInt(item.quantity || 1)), 0);

  const handlePrint = () => {
    window.print();
  };

  const handleConfirm = () => {
    setIsSuccess(true);
    setTimeout(() => {
      setCart([]);
      setIsSuccess(false);
      onClose();
      setMessages(prev => [...prev, {
        id: Date.now(),
        role: "ai",
        type: "text",
        content: "Your order has been placed successfully! The pharmacy team will prepare it shortly."
      }]);
    }, 3000);
  };

  return (
    <div className="fixed inset-0 z-[100] flex justify-center p-4 sm:p-6 bg-slate-900/40 backdrop-blur-md">
      <div className="w-full max-w-2xl bg-white rounded-[2rem] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-slate-100 print:hidden">
          <h2 className="text-2xl font-black text-slate-800 flex items-center gap-2">
            <CreditCard className="text-blue-600" /> Secure Checkout
          </h2>
          {!isSuccess && (
            <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors">
              <X className="text-slate-500" />
            </button>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 sm:p-8 relative">
          {isSuccess ? (
            <div className="absolute inset-0 bg-white z-10 flex flex-col items-center justify-center p-8 text-center animate-in fade-in duration-500">
              <div className="w-24 h-24 bg-emerald-100 rounded-full flex items-center justify-center mb-6">
                <CheckCircle size={48} className="text-emerald-500" />
              </div>
              <h2 className="text-3xl font-black text-slate-800 mb-2">Order Successful!</h2>
              <p className="text-slate-500">Your total of ${total.toFixed(2)} has been charged. Check your printed invoice.</p>
            </div>
          ) : (
            <div ref={printRef} className="print-section max-w-full">
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
                  {patient?.symptom && (
                    <div className="col-span-2 mt-2">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Diagnosed Symptom</h4>
                      <p className="text-slate-800 font-bold bg-amber-50 text-amber-800 p-2 rounded-lg border border-amber-100 inline-block">{patient.symptom}</p>
                    </div>
                  )}
                  {patient?.prescription && (
                    <div className="col-span-2 mt-2">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Attached Medical Record</h4>
                      <p className="text-slate-800 font-bold bg-blue-50 text-blue-800 p-2 rounded-lg border border-blue-100 inline-flex items-center gap-2">
                        📄 {patient.prescription}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Order Items */}
              <div className="space-y-4 mb-8">
                <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-4">
                  <FileText size={18} className="text-blue-500" /> Approved Medications
                </h3>
                {cart.length === 0 ? (
                  <p className="text-sm text-slate-500 italic">No medicinal items present.</p>
                ) : (
                  cart.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center p-4 bg-slate-50 rounded-2xl border border-slate-100 print:bg-transparent print:p-2 print:border-b print:rounded-none">
                      <div>
                        <h4 className="font-bold text-slate-800">{item.name}</h4>
                        <p className="text-xs text-slate-500 mt-1">Qty: {item.quantity || 1}</p>
                      </div>
                      <div className="font-black text-slate-800">
                        ${(parseFloat(item.price) * parseInt(item.quantity || 1)).toFixed(2)}
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Totals */}
              <div className="bg-slate-50 rounded-3xl p-6 border border-slate-100 print:bg-transparent print:border-t-2 print:rounded-none print:border-slate-800 relative overflow-hidden">
                {/* WATERMARK */}
                <div className="absolute -right-8 -top-8 text-emerald-500/10 font-black text-8xl -rotate-12 pointer-events-none print:text-emerald-500/20">
                  PAID
                </div>

                <div className="flex justify-between items-center text-slate-600 mb-2 relative z-10">
                  <span>Subtotal</span>
                  <span className="font-bold">${total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center text-slate-600 mb-4 pb-4 border-b border-slate-200 relative z-10">
                  <span>Tax (0%)</span>
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
          <div className="p-6 bg-white border-t border-slate-100 flex gap-4 print:hidden">
            <button 
              onClick={handlePrint}
              className="px-6 py-4 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-2xl transition-colors flex items-center gap-2"
            >
              <Download size={18} /> Download Bill
            </button>
            <button 
              onClick={handleConfirm}
              disabled={cart.length === 0}
              className="flex-1 px-6 py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-2xl transition-colors shadow-lg shadow-blue-600/20 disabled:opacity-50"
            >
              Confirm Checkout
            </button>
          </div>
        )}
      </div>

      <style dangerouslySetInnerHTML={{__html: `
        @media print {
          body * {
            visibility: hidden;
          }
          .print-section, .print-section * {
            visibility: visible;
          }
          .print-section {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            padding: 40px;
          }
        }
      `}} />
    </div>
  );
}
