import { X, Trash2, CreditCard, ShoppingCart } from 'lucide-react';
import { usePharmacy } from '../../context/PharmacyContext';

const CartDrawer = ({ isOpen, onClose }) => {
  const { cart, setCart } = usePharmacy();

  // Calculate the grand total
  const grandTotal = cart.reduce((sum, item) => sum + item.price, 0);

  const handleRemove = (indexToRemove) => {
    setCart(cart.filter((_, idx) => idx !== indexToRemove));
  };

  const handleCheckout = () => {
    alert("This will trigger the AI Checkout Prompt and PayPal generation!");
    // We will wire this to the backend Billing Agent later!
  };

  return (
    <>
      {/* Dark blurred overlay behind the drawer */}
      <div 
        className={`fixed inset-0 bg-black/20 backdrop-blur-sm z-[60] transition-opacity duration-500 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={onClose}
      ></div>

      {/* The Glass Drawer sliding from the right */}
      <div className={`fixed top-0 right-0 h-full w-full max-w-md glass-panel !rounded-none !rounded-l-[40px] z-[70] flex flex-col transform transition-transform duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        
        {/* Drawer Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/40">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-100 text-emerald-600 rounded-xl">
              <ShoppingCart size={24} />
            </div>
            <h2 className="text-2xl font-extrabold text-slate-800 tracking-tight">Your Cart</h2>
          </div>
          <button 
            onClick={onClose}
            className="p-2 bg-white/50 hover:bg-white border border-white/60 rounded-full text-slate-500 hover:text-slate-800 transition-all active:scale-95 shadow-sm"
          >
            <X size={20} />
          </button>
        </div>

        {/* Cart Items Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {cart.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-4 opacity-70">
              <ShoppingCart size={48} strokeWidth={1} />
              <p className="font-medium text-lg">Your cart is empty.</p>
            </div>
          ) : (
            cart.map((item, idx) => (
              <div key={idx} className="bg-white/60 backdrop-blur-md border border-white/80 p-4 rounded-3xl shadow-sm flex items-center justify-between group hover:bg-white/80 transition-colors">
                <div>
                  <h4 className="font-bold text-slate-800">{item.name}</h4>
                  <p className="text-xs font-semibold text-slate-500 mt-0.5 uppercase tracking-wider">{item.category}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className="font-extrabold text-slate-800">${item.price.toFixed(2)}</span>
                  <button 
                    onClick={() => handleRemove(idx)}
                    className="p-2 text-rose-400 hover:text-rose-600 hover:bg-rose-50 rounded-full transition-colors opacity-0 group-hover:opacity-100"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Sticky Checkout Footer */}
        {cart.length > 0 && (
          <div className="p-6 bg-white/40 backdrop-blur-xl border-t border-white/50">
            <div className="flex justify-between items-center mb-6">
              <span className="text-slate-500 font-semibold uppercase tracking-wider text-sm">Grand Total</span>
              <span className="text-3xl font-black text-slate-800">${grandTotal.toFixed(2)}</span>
            </div>
            
            <button 
              onClick={handleCheckout}
              className="w-full py-4 bg-slate-800 hover:bg-slate-700 text-white rounded-2xl font-bold text-lg shadow-xl shadow-slate-800/20 flex items-center justify-center gap-2 active:scale-[0.98] transition-all"
            >
              <CreditCard size={20} /> Checkout Securely
            </button>
          </div>
        )}
      </div>
    </>
  );
};

export default CartDrawer;