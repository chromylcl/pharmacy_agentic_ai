import { useState } from 'react';
import { ShoppingCart, AlertCircle, FileText, Plus, Minus } from 'lucide-react';
import { usePharmacy } from '../../context/PharmacyContext';
import PrescriptionUpload from '../Chat/PrescriptionUpload';

const ProductGrid = ({ searchQuery, activeCategory, products = [] }) => {
  const { cart, setCart, patient } = usePharmacy();
  const [quantities, setQuantities] = useState({});
  const [warningModal, setWarningModal] = useState(null);
  const [rxModalProduct, setRxModalProduct] = useState(null);

  const handleQtyChange = (productId, delta, maxStock) => {
    setQuantities(prev => {
      const current = prev[productId] || 1;
      const next = current + delta;
      if (next < 1) return prev;
      if (next > maxStock) return prev;
      return { ...prev, [productId]: next };
    });
  };

  const handleAddToCartClick = (product) => {
    const qty = quantities[product.id] || 1;
    const safeLimit = product.max_safe_dosage || 10;

    if (qty > safeLimit) {
      setWarningModal({ product, quantity: qty, safeLimit });
    } else {
      addToCart(product, qty, false);
    }
  };

  const addToCart = (product, qty, confirmed_overdose) => {
    console.log("Added to cart:", product.name, "Qty:", qty);

    // Check if item already in cart
    const existingIdx = cart.findIndex(c => c.id === product.id);
    if (existingIdx >= 0) {
      const newCart = [...cart];
      newCart[existingIdx].quantity += qty;
      newCart[existingIdx].confirmed_overdose = confirmed_overdose || newCart[existingIdx].confirmed_overdose;
      setCart(newCart);
    } else {
      setCart([...cart, { ...product, quantity: qty, confirmed_overdose }]);
    }
    setWarningModal(null);
  };

  const filteredProducts = products.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = activeCategory === 'All';
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="relative">
      {/* OVERDOSAGE WARNING MODAL */}
      {warningModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white rounded-2xl p-6 md:p-8 max-w-md w-full shadow-2xl space-y-4 border border-red-100">
            <div className="flex items-center gap-3 text-red-600 mb-2">
              <AlertCircle size={32} />
              <h2 className="text-xl font-bold">Safety Warning</h2>
            </div>
            <p className="text-slate-600 font-medium">
              You are selecting a high quantity (<strong className="text-red-500">{warningModal.quantity}</strong>) of <strong>{warningModal.product.name}</strong>.
            </p>
            <p className="text-slate-600">
              The suggested safe dosage limit is <strong className="text-slate-900">{warningModal.safeLimit}</strong>. Consuming excessive quantities can cause adverse health effects.
            </p>
            <div className="flex gap-3 justify-end mt-6 pt-4 border-t border-slate-100">
              <button
                onClick={() => setWarningModal(null)}
                className="px-5 py-2.5 rounded-xl font-bold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => addToCart(warningModal.product, warningModal.quantity, true)}
                className="px-5 py-2.5 rounded-xl font-bold bg-red-500 text-white hover:bg-red-600 transition-colors shadow-lg shadow-red-500/30"
              >
                I understand, Proceed
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 w-full pb-20">
        {filteredProducts.map((product) => {
          const isOutOfStock = product.stock === 0;
          const qty = quantities[product.id] || 1;

          return (
            <div
              key={product.id}
              className={`glass-panel p-5 relative overflow-hidden transition-all duration-300 ${isOutOfStock ? 'opacity-60 grayscale-[0.5]' : 'hover:-translate-y-1 hover:shadow-xl hover:bg-white/60'
                }`}
            >
              <div className="flex justify-between items-start mb-3">
                <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider ${product.prescription_required ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'
                  }`}>
                  {product.prescription_required ? 'Rx Required' : 'OTC'}
                </span>

                <span className={`text-xs font-semibold ${isOutOfStock ? 'text-red-500' : 'text-slate-500'}`}>
                  {isOutOfStock ? 'Out of Stock' : `${product.stock} in stock`}
                </span>
              </div>

              <h3 className="text-lg font-bold text-slate-800 tracking-tight">{product.name}</h3>
              <p className="text-sm text-slate-500 mt-1 mb-4 line-clamp-2">{product.description || 'No description available.'}</p>

              <div className="flex items-center justify-between mt-auto pt-3 border-t border-slate-200/50 gap-4">
                <span className="text-xl font-extrabold text-slate-800">${(product.price || 0).toFixed(2)}</span>

                {/* QUANTITY SELECTOR */}
                {!product.prescription_required && !isOutOfStock && (
                  <div className="flex items-center bg-white rounded-full border border-slate-200 shadow-sm mr-auto ml-4">
                    <button onClick={() => handleQtyChange(product.id, -1, product.stock)} className="p-1.5 focus:outline-none hover:bg-slate-50 rounded-l-full text-slate-600 transition-colors">
                      <Minus size={14} strokeWidth={3} />
                    </button>
                    <span className="w-8 text-center font-bold text-sm text-slate-800">{qty}</span>
                    <button onClick={() => handleQtyChange(product.id, 1, product.stock)} className="p-1.5 focus:outline-none hover:bg-slate-50 rounded-r-full text-slate-600 transition-colors">
                      <Plus size={14} strokeWidth={3} />
                    </button>
                  </div>
                )}

                {product.prescription_required ? (
                  <button
                    disabled={isOutOfStock}
                    onClick={() => setRxModalProduct(product)}
                    className={`flex items-center gap-1.5 px-4 py-2 text-sm font-semibold rounded-full shadow-sm transition-colors ml-auto ${isOutOfStock
                      ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                      : 'bg-amber-500 hover:bg-amber-600 text-white active:scale-95'
                      }`}
                  >
                    <FileText size={16} /> {isOutOfStock ? 'Upload Rx' : 'Upload Rx & Add'}
                  </button>
                ) : (
                  <button
                    disabled={isOutOfStock}
                    onClick={() => handleAddToCartClick(product)}
                    className={`flex items-center gap-1.5 px-4 py-2 text-sm font-semibold rounded-full shadow-sm transition-all active:scale-95 ml-auto ${isOutOfStock
                      ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                      : 'bg-slate-800 hover:bg-slate-700 text-white'
                      }`}
                  >
                    <ShoppingCart size={16} /> Add
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <PrescriptionUpload
        isOpen={!!rxModalProduct}
        onClose={() => setRxModalProduct(null)}
        medicineName={rxModalProduct?.name}
        userId={patient?.id || patient?.email || "Unknown"}
        onUploadComplete={(filename) => {
          if (rxModalProduct) {
            handleAddToCartClick(rxModalProduct);
          }
          setRxModalProduct(null);
        }}
      />
    </div>
  );
};

export default ProductGrid;