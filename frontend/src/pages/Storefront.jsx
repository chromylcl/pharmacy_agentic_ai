import { useState, useEffect } from 'react';
import ProductGrid from '../components/Store/ProductGrid';
import { Search, SlidersHorizontal, Sparkles, Filter } from 'lucide-react';
import { pharmacyService } from '../services/api';

const glassBase = "bg-white/30 backdrop-blur-[32px] saturate-[180%] border border-white/60 shadow-[0_24px_48px_-12px_rgba(0,0,0,0.1)]";

export default function Storefront() {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const categories = ['All', 'OTC', 'Antibiotics', 'Supplements', 'Allergy', 'Diagnostics'];

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await pharmacyService.getProducts();
        setProducts(response.data);
      } catch (err) {
        console.error("Failed to load products", err);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  return (
    <div className="w-full max-w-7xl mx-auto p-6 md:p-12 h-full overflow-y-auto scrollbar-hide space-y-12 animate-in fade-in duration-1000">
      
      {/* SEARCH HEADER */}
      <div className="flex flex-col gap-10">
        <div className="flex justify-between items-end">
          <div>
             <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 mb-4">
              <Sparkles size={12} className="text-blue-600" />
              <span className="text-[9px] font-black uppercase tracking-widest text-blue-700">Digital Dispensary v1.0</span>
            </div>
            <h1 className="text-5xl font-black text-slate-900 tracking-tighter leading-none">Inventory</h1>
          </div>
          <p className="text-slate-400 font-bold uppercase tracking-widest text-[10px] mb-2 hidden md:block">Authorized Access Only</p>
        </div>

        <div className="flex flex-col md:flex-row gap-5">
          <div className={`flex-1 flex items-center gap-4 px-8 py-5 rounded-[2.5rem] ${glassBase} focus-within:ring-8 ring-blue-500/5 transition-all group`}>
            <Search size={22} className="text-slate-400 group-focus-within:text-blue-600 transition-colors" strokeWidth={3} />
            <input 
              type="text" 
              placeholder="Search medications, symptoms, or active ingredients..."
              className="bg-transparent border-none outline-none flex-1 text-slate-900 font-bold placeholder:text-slate-400 text-lg"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <button className={`px-10 py-5 rounded-[2.5rem] flex items-center gap-3 font-black text-slate-700 hover:bg-white/60 transition-all ${glassBase} shadow-inner active:scale-95`}>
            <Filter size={20} strokeWidth={3} /> Filters
          </button>
        </div>

        {/* CATEGORY NAV */}
        <div className="flex items-center gap-4 overflow-x-auto pb-6 scrollbar-hide border-b border-white/40">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-8 py-3 rounded-full text-xs font-black uppercase tracking-widest transition-all duration-500 whitespace-nowrap ${
                activeCategory === cat 
                ? 'bg-slate-900 text-white shadow-2xl scale-110 translate-y-[-2px]' 
                : 'bg-white/20 text-slate-400 hover:bg-white/60 border border-white/40'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* PRODUCTS GRID */}
      {loading ? (
        <div className="flex justify-center items-center h-48">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <ProductGrid searchQuery={searchQuery} activeCategory={activeCategory} products={products} />
      )}
    </div>
  );
}