import React from 'react';
import { format } from 'date-fns';
import type { ActivityLog } from '../types';

interface ActivityFeedProps {
  activities: ActivityLog[];
}

export const ActivityFeed: React.FC<ActivityFeedProps> = ({ activities }) => {
  const getLevelColor = (level: string) => {
    switch (level) {
      case 'SUCCESS':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'WARNING':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'ERROR':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'SUCCESS':
        return '✅';
      case 'WARNING':
        return '⚠️';
      case 'ERROR':
        return '❌';
      default:
        return 'ℹ️';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Activity Feed</h2>
        <p className="text-sm text-gray-500">Real-time Grok AI activity stream</p>
      </div>
      <div className="h-96 overflow-y-auto p-4 space-y-3">
        {activities.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No activity yet. Start trading to see updates.
          </div>
        ) : (
          activities.slice().reverse().map((activity, index) => (
            <div
              key={index}
              className={`p-3 rounded border ${getLevelColor(activity.level)}`}
            >
              <div className="flex items-start gap-2">
                <span className="text-lg">{getLevelIcon(activity.level)}</span>
                <div className="flex-1">
                  <p className="text-sm font-medium">{activity.message}</p>
                  <p className="text-xs mt-1 opacity-75">
                    {format(new Date(activity.timestamp), 'HH:mm:ss')}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
