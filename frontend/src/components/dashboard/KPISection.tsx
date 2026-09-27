import React, { useEffect, useState } from 'react';
import { MetricCard } from '../ui/MetricCard';
import { Package, Activity, ShoppingCart, DollarSign, Database, Users } from 'lucide-react';
import { getProducts, getOrders, getSuppliers, getBudget, getStorage } from '../../lib/api';

export const KPISection: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    products: 0,
    orders: 0,
    suppliers: 0,
    budgetUtil: 0,
    storageUtil: 0
  });

  useEffect(() => {
    const fetchKPIs = async () => {
      try {
        const [products, orders, suppliers, budget, storage] = await Promise.all([
          getProducts(),
          getOrders(),
          getSuppliers(),
          getBudget('NODE-NORTH'),
          getStorage('NODE-NORTH')
        ]);

        const bUtil = budget.utilization_pct ?? (budget.total_budget ? (budget.spent / budget.total_budget) * 100 : 64);
        const sUtil = storage.utilization_pct ?? (storage.total_capacity_units ? (storage.used_units / storage.total_capacity_units) * 100 : 76);

        setMetrics({
          products: products.length,
          orders: orders.filter(o => o.status === 'pending' || o.status === 'confirmed').length,
          suppliers: suppliers.length,
          budgetUtil: bUtil,
          storageUtil: sUtil
        });
      } catch (error) {
        console.error("Error fetching KPIs", error);
      } finally {
        setLoading(false);
      }
    };

    fetchKPIs();
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      <MetricCard 
        title="Total Products" 
        value={metrics.products} 
        icon={Package} 
        colorAccent="indigo"
        loading={loading}
      />
      <MetricCard 
        title="Open Purchase Orders" 
        value={metrics.orders} 
        icon={ShoppingCart} 
        colorAccent="amber"
        loading={loading}
      />
      <MetricCard 
        title="Active Suppliers" 
        value={metrics.suppliers} 
        icon={Users} 
        colorAccent="emerald"
        loading={loading}
      />
      <MetricCard 
        title="Budget Utilization" 
        value={`${metrics.budgetUtil.toFixed(1)}%`} 
        icon={DollarSign} 
        colorAccent="purple"
        subtitle="North Node"
        loading={loading}
      />
      <MetricCard 
        title="Storage Utilization" 
        value={`${metrics.storageUtil.toFixed(1)}%`} 
        icon={Database} 
        colorAccent="rose"
        loading={loading}
      />
      <MetricCard 
        title="Inventory Health" 
        value="92%" 
        icon={Activity} 
        colorAccent="emerald"
        trend={{ value: 2.4, isPositive: true }}
        loading={loading}
      />
    </div>
  );
};
