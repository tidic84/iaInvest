import { useEffect, useRef, useState } from 'react';
import type { ActivityLog } from '../types';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

export const useWebSocket = () => {
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const isCleaningUpRef = useRef(false);

  useEffect(() => {
    isCleaningUpRef.current = false;

    const connect = () => {
      // Don't reconnect if component is unmounting
      if (isCleaningUpRef.current) return;

      // Close existing connection if any
      if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
        console.log('WebSocket already connected or connecting');
        return;
      }

      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        console.log('[WebSocket] Connected successfully');
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('[WebSocket] Message received:', message.type);

          if (message.type === 'activity') {
            console.log('[WebSocket] New activity:', message.data);
            setActivities((prev) => [...prev, message.data].slice(-100)); // Keep last 100
          } else if (message.type === 'status' && message.data.activity_log) {
            console.log('[WebSocket] Initial activities:', message.data.activity_log.length);
            setActivities(message.data.activity_log);
          }
        } catch (error) {
          console.error('[WebSocket] Error parsing message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);

        // Reconnect after 3 seconds only if not cleaning up
        if (!isCleaningUpRef.current) {
          reconnectTimeoutRef.current = window.setTimeout(connect, 3000);
        }
      };

      wsRef.current = ws;
    };

    connect();

    return () => {
      isCleaningUpRef.current = true;

      // Cancel any pending reconnection
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      // Close WebSocket connection
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, []);

  return { activities, isConnected };
};
