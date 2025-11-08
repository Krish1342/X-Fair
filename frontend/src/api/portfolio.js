import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const getAuthHeaders = () => {
  const token = window.localStorage?.getItem("finance_token");
  return {
    Authorization: token ? `Bearer ${token}` : "",
  };
};

// Stocks API
export const getStocks = async (userId, refresh = false) => {
  const response = await axios.get(
    `${API_BASE}/api/v1/portfolio/stocks/${userId}?refresh=${refresh}`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

export const createStock = async (userId, stockData) => {
  const response = await axios.post(
    `${API_BASE}/api/v1/portfolio/stocks/${userId}`,
    stockData,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

export const updateStock = async (userId, stockId, stockData) => {
  const response = await axios.put(
    `${API_BASE}/api/v1/portfolio/stocks/${userId}/${stockId}`,
    stockData,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

export const deleteStock = async (userId, stockId) => {
  const response = await axios.delete(
    `${API_BASE}/api/v1/portfolio/stocks/${userId}/${stockId}`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

// Mutual Funds API
export const getMutualFunds = async (userId) => {
  const response = await axios.get(
    `${API_BASE}/api/v1/portfolio/mutual-funds/${userId}`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

export const createMutualFund = async (userId, mfData) => {
  const response = await axios.post(
    `${API_BASE}/api/v1/portfolio/mutual-funds/${userId}`,
    mfData,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

export const updateMutualFund = async (userId, mfId, mfData) => {
  const response = await axios.put(
    `${API_BASE}/api/v1/portfolio/mutual-funds/${userId}/${mfId}`,
    mfData,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

export const deleteMutualFund = async (userId, mfId) => {
  const response = await axios.delete(
    `${API_BASE}/api/v1/portfolio/mutual-funds/${userId}/${mfId}`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

// Portfolio Summary
export const getPortfolioSummary = async (userId) => {
  const response = await axios.get(
    `${API_BASE}/api/v1/portfolio/summary/${userId}`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

// Refresh all prices
export const refreshAllPrices = async (userId) => {
  const response = await axios.post(
    `${API_BASE}/api/v1/portfolio/refresh-prices/${userId}`,
    {},
    { headers: getAuthHeaders() }
  );
  return response.data;
};
