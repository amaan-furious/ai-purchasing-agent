import axios from 'axios';
import type {
  Product,
  InventoryItem,
  Supplier,
  PurchaseOrder,
  DemandForecast,
  Budget,
  StorageCapacity,
  Scenario,
  AgentDecision,
} from './types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// Products & Inventory
export const getProducts = () => api.get<Product[]>('/products').then(r => r.data);
export const getProduct = (id: string) => api.get<Product>(`/products/${id}`).then(r => r.data);
export const getInventory = (nodeId: string) => api.get<InventoryItem[]>(`/inventory/${nodeId}`).then(r => r.data);
export const getNodes = () => api.get('/nodes').then(r => r.data);

// Suppliers
export const getSuppliers = () => api.get<Supplier[]>('/suppliers').then(r => r.data);
export const getSupplier = (id: string) => api.get<Supplier>(`/suppliers/${id}`).then(r => r.data);
export const getSuppliersForProduct = (productId: string) => api.get(`/suppliers/for-product/${productId}`).then(r => r.data);

// Purchase Orders
export const getOrders = () => api.get<PurchaseOrder[]>('/orders').then(r => r.data);
export const getOrder = (id: string) => api.get<PurchaseOrder>(`/orders/${id}`).then(r => r.data);

// Forecasts, Budget, Storage
export const getForecasts = (nodeId: string) => api.get<DemandForecast[]>(`/forecasts/${nodeId}`).then(r => r.data);
export const getBudget = (nodeId: string) => api.get<Budget>(`/budget/${nodeId}`).then(r => r.data);
export const getStorage = (nodeId: string) => api.get<StorageCapacity>(`/storage/${nodeId}`).then(r => r.data);

// Scenarios
export const getScenarios = () => api.get<Scenario[]>('/scenarios').then(r => r.data);
export const getScenario = (id: string) => api.get<Scenario>(`/scenarios/${id}`).then(r => r.data);

// Run scenario — returns EventSource for SSE streaming
export const runScenario = (scenarioId: string, _config: any): EventSource => {
  const eventSource = new EventSource(`/api/scenarios/${scenarioId}/run`);
  return eventSource;
};

// Reset scenario
export const resetScenario = async (scenarioId: string) => {
  return api.post(`/scenarios/${scenarioId}/reset`).then(r => r.data);
};

// Agent decisions
export const getAgentDecisions = () => api.get<AgentDecision[]>('/agent/decisions').then(r => r.data);
export const getAgentDecision = (id: number) => api.get<AgentDecision>(`/agent/decisions/${id}`).then(r => r.data);
