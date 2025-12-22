import React, { useEffect, useState } from 'react';
import { tradingAPI } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import { StatsCard } from './StatsCard';
import { ActivityFeed } from './ActivityFeed';
import { PortfolioChart } from './PortfolioChart';
import { TradesTable } from './TradesTable';
import type { Portfolio, Statistics, Trade, PortfolioSnapshot } from '../types';

export const Dashboard: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [stats, setStats] = useState<Statistics | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [history, setHistory] = useState<PortfolioSnapshot[]>([]);
  const { activities: wsActivities, isConnected } = useWebSocket();
  const [apiActivities, setApiActivities] = useState<any[]>([]);

  // Use WebSocket activities if available, otherwise use API activities
  const activities = wsActivities.length > 0 ? wsActivities : apiActivities;

  const fetchData = async () => {
    try {
      const [statusRes, portfolioRes, statsRes, tradesRes, historyRes, activitiesRes] =
        await Promise.all([
          tradingAPI.getTradingStatus(),
          tradingAPI.getCurrentPortfolio(),
          tradingAPI.getStatistics(),
          tradingAPI.getTrades(20),
          tradingAPI.getPortfolioHistory(50),
          tradingAPI.getActivities(50),
        ]);

      console.log('[Dashboard] Trading status:', statusRes.data);
      console.log('[Dashboard] Activities count:', activitiesRes.data.activities.length);

      setIsRunning(statusRes.data.is_running);
      setPortfolio(portfolioRes.data);
      setStats(statsRes.data);
      setTrades(tradesRes.data);
      setHistory(historyRes.data);
      setApiActivities(activitiesRes.data.activities);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const handleStartStop = async () => {
    try {
      if (isRunning) {
        await tradingAPI.stopTrading();
      } else {
        await tradingAPI.startTrading();
      }
      await fetchData();
    } catch (error) {
      console.error('Error toggling trading:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Trading IA Auto-Apprenant
              </h1>
              <p className="text-sm text-gray-500">
                Autonomous AI Trading with Self-Learning
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div
                  className={`h-3 w-3 rounded-full ${
                    isConnected ? 'bg-green-500' : 'bg-red-500'
                  }`}
                />
                <span className="text-sm text-gray-600">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <button
                onClick={handleStartStop}
                className={`px-6 py-2 rounded-lg font-semibold text-white ${
                  isRunning
                    ? 'bg-red-600 hover:bg-red-700'
                    : 'bg-green-600 hover:bg-green-700'
                }`}
              >
                {isRunning ? 'Stop Trading' : 'Start Trading'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Portfolio Value"
            value={portfolio ? `$${portfolio.total_value.toFixed(2)}` : '-'}
            valueColor={
              portfolio && portfolio.total_pnl >= 0
                ? 'text-green-600'
                : 'text-red-600'
            }
          />
          <StatsCard
            title="Total P&L"
            value={portfolio ? `$${portfolio.total_pnl.toFixed(2)}` : '-'}
            valueColor={
              portfolio && portfolio.total_pnl >= 0
                ? 'text-green-600'
                : 'text-red-600'
            }
            trend={
              portfolio
                ? {
                    value: Number(portfolio.total_pnl_pct.toFixed(2)),
                    isPositive: portfolio.total_pnl >= 0,
                  }
                : undefined
            }
          />
          <StatsCard
            title="Win Rate"
            value={stats ? `${stats.win_rate.toFixed(1)}%` : '-'}
            valueColor="text-blue-600"
          />
          <StatsCard
            title="Total Trades"
            value={stats ? stats.total_trades : 0}
            valueColor="text-gray-900"
          />
        </div>

        {/* Chart and Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <PortfolioChart data={history} />
          </div>
          <div>
            <ActivityFeed activities={activities} />
          </div>
        </div>

        {/* Trades Table */}
        <div className="mb-8">
          <TradesTable trades={trades} />
        </div>

        {/* Positions */}
        {portfolio && portfolio.positions.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Open Positions
            </h2>
            <div className="space-y-3">
              {portfolio.positions.map((position, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded"
                >
                  <div>
                    <div className="font-semibold text-gray-900">
                      {position.symbol}
                    </div>
                    <div className="text-sm text-gray-500">
                      Qty: {position.quantity.toFixed(4)} @ $
                      {position.avg_price.toFixed(2)}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900">
                      ${position.current_value.toFixed(2)}
                    </div>
                    <div
                      className={`text-sm ${
                        position.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {position.pnl >= 0 ? '+' : ''}${position.pnl.toFixed(2)} (
                      {position.pnl_pct.toFixed(2)}%)
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
