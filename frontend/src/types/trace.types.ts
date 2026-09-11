export interface NodeDetails {
  id: string;
  is_source: boolean;
  is_exchange: boolean;
  vasp_name?: string;
  confidence_score: number;
  shap_features?: Record<string, number>;
  is_mixer?: boolean;
}

export interface EdgeDetails {
  source: string;
  target: string;
  value: number;
}

export interface LeaderboardEntry {
  address: string;
  vasp_name: string;
  confidence: number;
  hop: number;
  shap_features?: Record<string, number>;
}

export interface TraceResult {
  nodes: NodeDetails[];
  links: EdgeDetails[];
  leaderboard: LeaderboardEntry[];
}
