import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { AlertTriangle, Package, CheckCircle } from 'lucide-react';

const AdminDashboard = () => {
  const [inventory, setInventory] = useState([]);

  useEffect(() => {
    // This calls the FastAPI backend you set up earlier
    axios.get('http://127.0.0.1:8000/inventory')
      .then(res => setInventory(res.data))
      .catch(err => console.error("Backend not reachable:", err));
  }, []);

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Package className="text-emerald-400" size={32} /> 
          Inventory Status
        </h1>
        <div className="bg-slate-800 border border-slate-700 px-4 py-2 rounded-lg text-sm">
          Total Items: <span className="text-emerald-400 font-mono">{inventory.length}</span>
        </div>
      </div>
      
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-2xl">
        <table className="w-full text-left border-collapse">
          <thead className="bg-slate-700/50 text-slate-400 text-xs uppercase tracking-wider">
            <tr>
              <th className="px-6 py-4">Medicine</th>
              <th className="px-6 py-4">Stock</th>
              <th className="px-6 py-4">Rx Required</th>
              <th className="px-6 py-4">Alerts</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {inventory.map((item, idx) => (
              <tr key={idx} className="hover:bg-slate-700/30 transition-colors">
                <td className="px-6 py-4 font-semibold text-slate-200">{item.name}</td>
                <td className="px-6 py-4">
                  <span className="font-mono">{item.stock}</span> 
                  <span className="text-slate-500 text-sm ml-1">{item.unit}</span>
                </td>
                <td className="px-6 py-4">
                  {item.prescription_required ? (
                    <span className="bg-red-500/10 text-red-400 px-2 py-1 rounded text-xs border border-red-500/20">Required</span>
                  ) : (
                    <span className="bg-slate-700 text-slate-400 px-2 py-1 rounded text-xs">OTC</span>
                  )}
                </td>
                <td className="px-6 py-4">
                  {item.stock < 15 ? (
                    <span className="text-amber-400 flex items-center gap-1 text-sm">
                      <AlertTriangle size={14} /> Low Stock
                    </span>
                  ) : (
                    <span className="text-emerald-500 flex items-center gap-1 text-sm">
                      <CheckCircle size={14} /> OK
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminDashboard;