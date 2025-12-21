import axios from 'axios';
import type {
  Trade,
  Reflection,
  LearnedRule,
  Portfolio,
  PortfolioSnapshot,
  Statistics,
  ActivityLog,
  TradingStatus,
} from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const tradingAPI = {
  // Health
  health: () => api.get('/api/health'),

  // Trading Control
  startTrading: () => api.post<{ status: string }>('/api/trading/start'),
  stopTrading: () => api.post<{ status: string }>('/api/trading/stop'),
  getTradingStatus: () => api.get<TradingStatus>('/api/trading/status'),

  // Trades
  getTrades: (limit: number = 50) => api.get<Trade[]>('/api/trades', { params: { limit } }),

  // Reflections
  getReflections: (limit: number = 10) => api.get<Reflection[]>('/api/reflections', { params: { limit } }),

  // Rules
  getRules: (activeOnly: boolean = true) => api.get<LearnedRule[]>('/api/rules', { params: { active_only: activeOnly } }),

  // Portfolio
  getCurrentPortfolio: () => api.get<Portfolio>('/api/portfolio/current'),
  getPortfolioHistory: (limit: number = 100) => api.get<PortfolioSnapshot[]>('/api/portfolio/history', { params: { limit } }),

  // Statistics
  getStatistics: () => api.get<Statistics>('/api/stats'),

  // Activity
  getActivity: (limit: number = 100) => api.get<ActivityLog[]>('/api/activity', { params: { limit } }),
};
