import { NodeDetails } from '../types/trace.types';

export const getD3Config = (width: number, height: number) => ({
  width,
  height,
  chargeStrength: -300,
  linkDistance: 80,
});

export const getNodeColor = (node: NodeDetails): string => {
  if (node.is_source) return '#fbbf24'; // amber-400
  if (node.is_mixer) return '#ef4444'; // red-500
  if (node.is_exchange) return '#4ade80'; // green-400
  return '#94a3b8'; // slate-400
};

export const getNodeRadius = (node: NodeDetails): number => {
  if (node.is_source) return 12;
  if (node.is_exchange) return 10;
  if (node.is_mixer) return 10;
  return 6;
};
