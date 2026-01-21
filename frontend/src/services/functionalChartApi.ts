/**
 * Functional Chart API Service
 * Handles all API calls for functional chart data
 */

const API_BASE_URL = 'http://localhost:8000/api/v1/functional-chart';

export interface FunctionCategory {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  display_order: number;
  functions: Function[];
}

export interface Function {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  display_order: number;
  accountabilities: Accountability[];
}

export interface Accountability {
  id: string;
  accountability_code?: string;
  objective: string;
  display_order: number;
  assignment_count?: number;
}

export interface FunctionalChartResponse {
  categories: FunctionCategory[];
}

// Get full functional chart
export const getFunctionalChart = async (): Promise<FunctionalChartResponse> => {
  const response = await fetch(`${API_BASE_URL}/chart`);
  if (!response.ok) throw new Error('Failed to fetch functional chart');
  return response.json();
};

// Create accountability
export const createAccountability = async (data: {
  function_id: string;
  objective: string;
  accountability_code?: string;
  created_by: string;
}): Promise<Accountability> => {
  const response = await fetch(`${API_BASE_URL}/accountabilities`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error('Failed to create accountability');
  return response.json();
};

// Update accountability
export const updateAccountability = async (
  id: string,
  data: {
    objective?: string;
    accountability_code?: string;
    updated_by: string;
  }
): Promise<Accountability> => {
  const response = await fetch(`${API_BASE_URL}/accountabilities/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error('Failed to update accountability');
  return response.json();
};

// Delete accountability
export const deleteAccountability = async (id: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/accountabilities/${id}`, {
    method: 'DELETE'
  });
  if (!response.ok) throw new Error('Failed to delete accountability');
};

// Create function
export const createFunction = async (data: {
  category_id: string;
  name: string;
  description?: string;
  icon?: string;
  created_by: string;
}): Promise<Function> => {
  const response = await fetch(`${API_BASE_URL}/functions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error('Failed to create function');
  return response.json();
};

// Create category
export const createCategory = async (data: {
  name: string;
  description?: string;
  icon?: string;
  created_by: string;
}): Promise<FunctionCategory> => {
  const response = await fetch(`${API_BASE_URL}/categories`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error('Failed to create category');
  return response.json();
};
