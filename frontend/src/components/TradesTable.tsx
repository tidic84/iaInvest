import React from 'react';
import { format } from 'date-fns';
import type { Trade } from '../types';

interface TradesTableProps {
  trades: Trade[];
}

export const TradesTable: React.FC<TradesTableProps> = ({ trades }) => {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Recent Trades</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                #
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Time
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Action
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Symbol
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Price
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                P&L
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {trades.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                  No trades yet
                </td>
              </tr>
            ) : (
              trades.map((trade) => (
                <tr key={trade.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {trade.trade_number}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {format(new Date(trade.timestamp), 'HH:mm:ss')}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                        trade.action === 'BUY'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {trade.action}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {trade.symbol}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    ${trade.entry_price.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {trade.pnl !== undefined && trade.pnl !== null ? (
                      <span
                        className={
                          trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                        }
                      >
                        ${trade.pnl.toFixed(2)} ({trade.pnl_percentage?.toFixed(2)}%)
                      </span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                        trade.status === 'OPEN'
                          ? 'bg-blue-100 text-blue-800'
                          : trade.status === 'CLOSED'
                          ? 'bg-gray-100 text-gray-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {trade.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
