import { ShoppingCart, AlertCircle, FileText } from 'lucide-react';
import { usePharmacy } from '../../context/PharmacyContext';

const ProductGrid = ({ searchQuery, activeCategory, products = [] }) => {
  const { cart, setCart } = usePharmacy();

  const handleAddToCart = (product) => {
    // We'll wire up the proper cart drawer later, for now just log it
    console.log("Added to cart:", product.name);
    setCart([...cart, product]);
  };

  const filteredProducts = products.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = activeCategory === 'All'; // Simplify category filter since the backend doesn't have categories right now.
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-5 w-full pb-20">
      {filteredProducts.map((product) => {
        const isOutOfStock = product.stock === 0;

        return (
          <div 
            key={product.id} 
            className={`glass-panel p-5 relative overflow-hidden transition-all duration-300 ${
              isOutOfStock ? 'opacity-60 grayscale-[0.5]' : 'hover:-translate-y-1 hover:shadow-xl hover:bg-white/60'
            }`}
          >
            <div className="flex justify-between items-start mb-3">
              <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider ${
                product.prescription_required ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'
              }`}>
                {product.prescription_required ? 'Rx Required' : 'OTC'}
              </span>
              
              <span className={`text-xs font-semibold ${isOutOfStock ? 'text-red-500' : 'text-slate-500'}`}>
                {isOutOfStock ? 'Out of Stock' : `${product.stock} in stock`}
              </span>
            </div>

            <h3 className="text-lg font-bold text-slate-800 tracking-tight">{product.name}</h3>
            <p className="text-sm text-slate-500 mt-1 mb-4 line-clamp-2">{product.desc || 'No description available.'}</p>

            <div className="flex items-center justify-between mt-auto pt-3 border-t border-slate-200/50">
              <span className="text-xl font-extrabold text-slate-800">${(product.price || 0).toFixed(2)}</span>
              
              {product.prescription_required ? (
                <button className="flex items-center gap-1.5 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold rounded-full shadow-sm transition-colors active:scale-95">
                  <FileText size={16} /> Upload Rx
                </button>
              ) : (
                <button 
                  disabled={isOutOfStock}
                  onClick={() => handleAddToCart(product)}
                  className={`flex items-center gap-1.5 px-4 py-2 text-sm font-semibold rounded-full shadow-sm transition-all active:scale-95 ${
                    isOutOfStock 
                    ? 'bg-slate-200 text-slate-400 cursor-not-allowed' 
                    : 'bg-slate-800 hover:bg-slate-700 text-white'
                  }`}
                >
                  <ShoppingCart size={16} /> {isOutOfStock ? 'Unavailable' : 'Add to Cart'}
                </button>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default ProductGrid;