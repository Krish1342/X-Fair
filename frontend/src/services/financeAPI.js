/**
 * API Service for Dynamic Personal Finance Agent
 * Handles all communication with the backend API using Axios
 */

import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

class FinanceAPIService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Set up request interceptor for auth token
    this.client.interceptors.request.use((config) => {
      const token =
        typeof window !== "undefined" &&
        window.localStorage?.getItem("finance_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Set up response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => {
        console.error(`API call failed:`, error.response || error);
        if (error.response?.data) {
          throw new Error(
            error.response.data.detail ||
              error.response.data.message ||
              `HTTP ${error.response.status}`
          );
        }
        throw error;
      }
    );
  }

  // Set authentication token
  setAuthToken(token) {
    if (token) {
      this.client.defaults.headers.Authorization = `Bearer ${token}`;
    } else {
      delete this.client.defaults.headers.Authorization;
    }
  }

  // Authentication endpoints
  async login(credentials) {
    // Backend expects email & password
    const loginData = {
      email: credentials.email || credentials.username,
      password: credentials.password,
      name: credentials.name,
    };

    return this.client.post("/auth/login", loginData);
  }

  async register(userData) {
    const registerData = {
      email: userData.email,
      password: userData.password,
      name: userData.name,
    };

    return this.client.post("/auth/register", registerData);
  }

  async logout() {
    return this.client.post("/auth/logout");
  }

  // Token verification
  async verifyToken(token) {
    this.setAuthToken(token);
    // The backend exposes /api/v1/auth/verify
    const resp = await this.client.get("/auth/verify");
    return {
      user: resp.user,
      userProfile: resp.userProfile || null,
      workflowStage: resp.workflow_stage || resp.workflowStage,
    };
  }

  // Chat and workflow endpoints
  async sendChatMessage(
    query,
    userId = null,
    conversationHistory = null,
    workflow_stage = "Started"
  ) {
    // Backend chat expects: { message, context?, user_id, workflow_stage }
    const res = await this.client.post("/chat", {
      message: query,
      user_id: userId || "default",
      workflow_stage,
      context: conversationHistory
        ? { conversation_history: conversationHistory }
        : undefined,
    });
    return {
      ...res,
      stage: res.workflow_stage || res.stage,
      suggestions: res.suggestions || [],
      visualizations: res.visualizations || [],
    };
  }

  // Backward-compat method used by some components
  async chat(payload) {
    // normalize payload to backend format
    const { message, context, user_id, workflow_stage } = payload || {};
    const res = await this.client.post("/chat", {
      message,
      context,
      user_id: user_id || "default",
      workflow_stage: workflow_stage || "Started",
    });
    return {
      ...res,
      stage: res.workflow_stage || res.stage,
      suggestions: res.suggestions || [],
      visualizations: res.visualizations || [],
      workflowUpdate: res.workflowUpdate || null,
    };
  }

  // Simple HTML-compatible chat
  async chatHTML(payload) {
    const { message, user_id, workflow_stage, context } = payload || {};
    const res = await this.client.post("/chat/html", {
      message,
      user_id: user_id || "default",
      workflow_stage: workflow_stage || "Started",
      context,
    });
    // Always returns { response: string }
    return res;
  }

  // Execute suggested action from AIPage
  async executeAction(payload) {
    return this.client.post("/chat/execute", payload);
  }

  async completeOnboarding(onboardingData) {
    // Backend expects { user_data: {...} }
    return this.client.post("/onboarding", { user_data: onboardingData });
  }

  async getWorkflowStatus(userId) {
    return this.client.get(`/workflow/status/${userId}`);
  }

  async getWorkflowVisualization() {
    return this.client.get("/workflow/visualization");
  }

  // Tool and feature endpoints
  async getAvailableTools() {
    return this.client.get("/tools");
  }

  async getExampleQueries() {
    return this.client.get("/examples");
  }

  // Health check
  async healthCheck() {
    return this.client.get("/health");
  }

  // User profile
  async getUserProfile(userId) {
    // The backend currently doesn't expose a profile route in main.py.
    // Keep function for future use; return a mock aligned with verify endpoint.
    return {
      user: { id: userId, name: "Demo User", email: "demo@example.com" },
    };
  }

  // Dashboard data
  async getDashboard(params = {}) {
    return this.client.get("/dashboard", { params });
  }

  // User-specific data
  async getTransactions(userId) {
    return this.client.get(`/transactions/${userId}`);
  }

  async addTransaction(userId, tx) {
    return this.client.post(`/transactions/${userId}`, tx);
  }

  async getTransaction(userId, id) {
    return this.client.get(`/transactions/${userId}/${id}`);
  }

  async updateTransaction(userId, id, tx) {
    return this.client.put(`/transactions/${userId}/${id}`, tx);
  }

  async deleteTransaction(userId, id) {
    return this.client.delete(`/transactions/${userId}/${id}`);
  }

  async getGoals(userId) {
    return this.client.get(`/goals/${userId}`);
  }

  async addGoal(userId, goal) {
    return this.client.post(`/goals/${userId}`, goal);
  }

  async getGoal(userId, id) {
    return this.client.get(`/goals/${userId}/${id}`);
  }

  async updateGoal(userId, id, goal) {
    return this.client.put(`/goals/${userId}/${id}`, goal);
  }

  async deleteGoal(userId, id) {
    return this.client.delete(`/goals/${userId}/${id}`);
  }

  async getBudgets(userId) {
    return this.client.get(`/budgets/${userId}`);
  }

  async addBudget(userId, budget) {
    return this.client.post(`/budgets/${userId}`, budget);
  }

  async getBudget(userId, id) {
    return this.client.get(`/budgets/${userId}/${id}`);
  }

  async updateBudget(userId, id, budget) {
    return this.client.put(`/budgets/${userId}/${id}`, budget);
  }

  async deleteBudget(userId, id) {
    return this.client.delete(`/budgets/${userId}/${id}`);
  }

  // Recurring transactions
  async listRecurring(userId) {
    return this.client.get(`/recurring/${userId}`);
  }

  async createRecurring(userId, item) {
    return this.client.post(`/recurring/${userId}`, item);
  }

  async updateRecurring(userId, id, item) {
    return this.client.put(`/recurring/${userId}/${id}`, item);
  }

  async deleteRecurring(userId, id) {
    return this.client.delete(`/recurring/${userId}/${id}`);
  }

  async previewRecurring(userId, periods = 3) {
    return this.client.get(`/recurring/${userId}/preview`, {
      params: { periods },
    });
  }

  async generateRecurring(userId, upTo = null) {
    return this.client.post(`/recurring/${userId}/generate`, null, {
      params: upTo ? { up_to: upTo } : {},
    });
  }
}

// Create and export a singleton instance
const financeAPI = new FinanceAPIService();
export default financeAPI;
export { financeAPI };
