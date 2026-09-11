import axios from 'axios';
import { TraceResult } from '../types/trace.types';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 60000,
});

export const apiClient = {
  getTrace: async (walletAddress: string): Promise<TraceResult> => {
    const response = await api.get(`/trace/${walletAddress}`);
    return response.data;
  },
};
