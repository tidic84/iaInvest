export interface Trade {
  id: number;
  trade_number: number;
  timestamp: string;
  action: 'BUY' | 'SELL';
  symbol: string;
  quantity: number;
  entry_price: number;
  exit_price?: number;
  pnl?: number;
  pnl_percentage?: number;
  status: 'OPEN' | 'CLOSED' | 'CANCELLED';
  reasoning?: any;
}

export interface Reflection {
  id: number;
  timestamp: string;
  start_trade_number: number;
  end_trade_number: number;
  mistakes: Mistake[];
  successes: Success[];
  new_rules: NewRule[];
  full_reflection: string;
}

export interface Mistake {
  description: string;
  trades_affected: number[];
  impact: string;
}

export interface Success {
  pattern: string;
  trades_involved: number[];
  why_it_worked: string;
}

export interface NewRule {
  rule: string;
  category: string;
  priority: number;
}

export interface LearnedRule {
  id: number;
  rule: string;
  category: string;
  priority: number;
  is_active: boolean;
  created_at: string;
  times_applied: number;
  success_count: number;
}

export interface Portfolio {
  cash: number;
  total_value: number;
  positions: Position[];
  total_pnl: number;
  total_pnl_pct: number;
  num_positions: number;
}

export interface Position {
  symbol: string;
  quantity: number;
  avg_price: number;
  current_value: number;
  pnl: number;
  pnl_pct: number;
}

export interface PortfolioSnapshot {
  timestamp: string;
  total_value: number;
  cash: number;
  total_pnl: number;
  total_pnl_percentage: number;
  win_rate: number;
  total_trades: number;
}

export interface Statistics {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_pnl: number;
  avg_pnl: number;
}

export interface ActivityLog {
  timestamp: string;
  level: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR';
  message: string;
}

export interface TradingStatus {
  is_running: boolean;
  last_trade_time?: string;
  activity_count: number;
}
