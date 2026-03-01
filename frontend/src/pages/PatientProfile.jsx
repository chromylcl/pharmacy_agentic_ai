import React, { useState, useEffect } from "react";
import { usePharmacy } from "../context/PharmacyContext";
import { History, Bell, PackageCheck, AlertCircle, ShoppingCart } from "lucide-react";
import axios from "axios";

const glassBase = "backdrop-blur-[32px] saturate-[200%] bg-white/60 border border-white/60 shadow-xl";

export default function PatientProfile() {
    const { patient, setCart, setIsBillingOpen } = usePharmacy();
    const [orders, setOrders] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const orderRes = await axios.get(`http://localhost:8000/user/orders/${patient.id}`);
                setOrders(orderRes.data);

                // Fetch refill alerts (admin endpoint, but we filter for user)
                const alertRes = await axios.get(`http://localhost:8000/admin/refill-alerts`);
                const userAlerts = alertRes.data.filter(a => a.patient_id === patient.id);
                setAlerts(userAlerts);

            } catch (error) {
                console.error("Failed to fetch profile data:", error);
            } finally {
                setLoading(false);
            }
        };

        if (patient?.id) {
            fetchData();
        }
    }, [patient.id]);

    const handleReorder = (productName) => {
        // We add to cart with a default quantity and price 0 (price updates usually from DB, here we mock it)
        setCart(prev => [...prev, {
            id: Date.now(),
            name: productName,
            quantity: 1,
            price: 0 // In a generic reorder, the real app would fetch current price.
        }]);
        setIsBillingOpen(true);
    };

    if (loading) {
        return (
            <div className="flex-1 overflow-y-auto px-4 py-8 flex items-center justify-center h-full">
                <div className="animate-pulse flex flex-col items-center gap-4">
                    <div className="h-12 w-12 bg-blue-100 rounded-full"></div>
                    <div className="text-slate-500 font-bold">Loading secure records...</div>
                </div>
            </div>
        );
    }

    return (
        <div className="flex-1 overflow-y-auto px-4 md:px-24 py-8 space-y-8 scrollbar-hide animate-in fade-in duration-500">
            <div className="flex items-center gap-4 mb-4">
                <div className="h-16 w-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30 text-white font-black text-2xl">
                    {patient?.name?.charAt(0)}
                </div>
                <div>
                    <h2 className="text-3xl font-black text-slate-800">{patient?.name}</h2>
                    <p className="text-slate-500 font-medium">{patient?.email}</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

                {/* REFILL ALERTS SECTION */}
                <div className="space-y-4">
                    <div className="flex items-center gap-2 mb-2">
                        <Bell className="text-amber-500" size={24} />
                        <h3 className="text-xl font-black text-slate-800">Refill Alerts</h3>
                    </div>

                    {alerts.length === 0 ? (
                        <div className={`p-8 rounded-3xl ${glassBase} text-center flex flex-col items-center gap-3`}>
                            <div className="p-4 bg-slate-100 rounded-full">
                                <PackageCheck size={24} className="text-slate-400" />
                            </div>
                            <p className="text-slate-500 font-medium">You have no active refill alerts.</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {alerts.map((alert, i) => (
                                <div key={i} className={`p-5 rounded-2xl ${glassBase} flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-l-4 border-l-amber-500 hover:shadow-2xl transition-all`}>
                                    <div className="flex items-start gap-3">
                                        <AlertCircle className="text-amber-500 mt-1" size={18} />
                                        <div>
                                            <h4 className="font-bold text-slate-800">{alert.medicine}</h4>
                                            <p className="text-sm text-slate-500">Running out by: {alert.expected_run_out}</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => handleReorder(alert.medicine)}
                                        className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-xl transition-all shadow-md active:scale-95 flex items-center gap-2 text-sm"
                                    >
                                        <ShoppingCart size={16} /> Reorder
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* ORDER HISTORY SECTION */}
                <div className="space-y-4">
                    <div className="flex items-center gap-2 mb-2">
                        <History className="text-blue-500" size={24} />
                        <h3 className="text-xl font-black text-slate-800">Order History</h3>
                    </div>

                    {orders.length === 0 ? (
                        <div className={`p-8 rounded-3xl ${glassBase} text-center flex flex-col items-center gap-3`}>
                            <div className="p-4 bg-slate-100 rounded-full">
                                <History size={24} className="text-slate-400" />
                            </div>
                            <p className="text-slate-500 font-medium">No previous orders found.</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {orders.map((order, i) => (
                                <div key={i} className={`p-5 rounded-2xl ${glassBase} flex justify-between items-center group hover:border-blue-200 transition-colors`}>
                                    <div>
                                        <h4 className="font-bold text-slate-800">{order.product}</h4>
                                        <p className="text-xs text-slate-400 font-mono mt-1">Purchased: {new Date(order.purchase_date).toLocaleDateString()}</p>
                                    </div>
                                    <div className="text-right">
                                        <span className="block font-black text-slate-700">Qty: {order.quantity}</span>
                                        <button
                                            onClick={() => handleReorder(order.product)}
                                            className="text-xs mt-1 text-blue-600 font-bold hover:underline opacity-0 group-hover:opacity-100 transition-opacity"
                                        >
                                            Buy Again
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}
