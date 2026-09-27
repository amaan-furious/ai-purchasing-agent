import React, { useState, useEffect } from 'react';
import { GlassCard } from '../ui/GlassCard';
import { getProducts, getSuppliers, getOrders } from '../../lib/api';
import { Product, Supplier, PurchaseOrder } from '../../lib/types';
import { Package, Users, ShoppingCart } from 'lucide-react';

export const DataExplorer: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'products' | 'suppliers' | 'orders'>('products');
  const [products, setProducts] = useState<Product[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [prodData, suppData, orderData] = await Promise.all([
          getProducts(),
          getSuppliers(),
          getOrders()
        ]);
        setProducts(prodData);
        setSuppliers(suppData);
        setOrders(orderData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const tabs = [
    { id: 'products', label: 'Products', icon: Package },
    { id: 'suppliers', label: 'Suppliers', icon: Users },
    { id: 'orders', label: 'Purchase Orders', icon: ShoppingCart }
  ];

  return (
    <div className="space-y-6">
      <div className="flex space-x-2 p-1 bg-slate-800/50 rounded-xl backdrop-blur-md border border-slate-700/50 w-fit">
        {tabs.map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                isActive 
                  ? 'bg-indigo-500/20 text-indigo-400 shadow-sm border border-indigo-500/30' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/30'
              }`}
            >
              <Icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          );
        })}
      </div>

      <GlassCard>
        {loading ? (
          <div className="h-64 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            {activeTab === 'products' && (
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-700/50 text-slate-400 text-sm">
                    <th className="py-3 px-4 font-medium">ID</th>
                    <th className="py-3 px-4 font-medium">Name</th>
                    <th className="py-3 px-4 font-medium">Category</th>
                    <th className="py-3 px-4 font-medium text-right">Cost</th>
                    <th className="py-3 px-4 font-medium text-right">Price</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map(p => {
                    const price = p.selling_price ?? p.price ?? 0;
                    return (
                      <tr key={p.id} className="border-b border-slate-700/20 hover:bg-slate-800/30">
                        <td className="py-3 px-4 text-sm text-slate-400">{p.id}</td>
                        <td className="py-3 px-4 text-sm font-medium text-white">{p.name}</td>
                        <td className="py-3 px-4 text-sm text-slate-300">
                          <span className="px-2 py-1 rounded bg-slate-800 border border-slate-700">{p.category}</span>
                        </td>
                        <td className="py-3 px-4 text-sm text-right text-slate-400">${p.unit_cost.toFixed(2)}</td>
                        <td className="py-3 px-4 text-sm text-right text-emerald-400">${price.toFixed(2)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}

            {activeTab === 'suppliers' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {suppliers.map(s => {
                  const score = Math.round((s.reliability_score ?? s.reliabilityScore ?? 0.9) * 100);
                  
                  return (
                    <div key={s.id} className="p-4 rounded-xl border border-slate-700/50 bg-slate-800/30">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-semibold text-white">{s.name}</h4>
                        <span className="text-xs text-slate-400">{s.id}</span>
                      </div>
                      <div className="space-y-2 mt-4">
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span className="text-slate-400">Reliability Score</span>
                            <span className="text-indigo-400">{score}%</span>
                          </div>
                          <div className="w-full bg-slate-700 rounded-full h-1.5">
                            <div className="bg-indigo-500 h-1.5 rounded-full" style={{ width: `${score}%` }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {activeTab === 'orders' && (
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-700/50 text-slate-400 text-sm">
                    <th className="py-3 px-4 font-medium">Order ID</th>
                    <th className="py-3 px-4 font-medium">Product ID</th>
                    <th className="py-3 px-4 font-medium">Quantity</th>
                    <th className="py-3 px-4 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map(o => {
                    const pId = o.product_id || o.productId || 'PRD-001';
                    const qty = o.quantity_ordered || o.quantity || 0;
                    
                    return (
                      <tr key={o.id} className="border-b border-slate-700/20 hover:bg-slate-800/30">
                        <td className="py-3 px-4 text-sm text-slate-400">{o.id}</td>
                        <td className="py-3 px-4 text-sm font-medium text-white">{pId}</td>
                        <td className="py-3 px-4 text-sm text-slate-300">{qty}</td>
                        <td className="py-3 px-4 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium uppercase ${
                            o.status === 'pending' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                            o.status === 'confirmed' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                            'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                          }`}>
                            {o.status}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        )}
      </GlassCard>
    </div>
  );
};
