import axios from 'axios';
import { TreeNode } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface OrgChartResponse {
  tree: TreeNode;
  metadata?: Record<string, any>;
}

export const fetchOrgChart = async (): Promise<OrgChartResponse> => {
  const response = await api.get<OrgChartResponse>('/api/v1/org-chart');
  return response.data;
};

export const fetchEmployees = async () => {
  const response = await api.get('/api/v1/employees');
  return response.data;
};

export const fetchPositions = async () => {
  const response = await api.get('/api/v1/positions');
  return response.data;
};

export const fetchOrgUnits = async () => {
  const response = await api.get('/api/v1/org-units');
  return response.data;
};

export default api;
