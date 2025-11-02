import http from "./http";

// Auth
export const loginAPI = (payload) =>
  http.post("/auth/login", payload).then((r) => r.data);
export const registerAPI = (payload) =>
  http.post("/auth/register", payload).then((r) => r.data);
export const logoutAPI = () => http.post("/auth/logout").then((r) => r.data);
export const verifyTokenAPI = () =>
  http.get("/auth/verify").then((r) => r.data);

// Dashboard and workflow
export const getDashboardAPI = (params) =>
  http.get("/dashboard", { params }).then((r) => r.data);
export const getWorkflowStatusAPI = (userId) =>
  http.get(`/workflow/status/${userId}`).then((r) => r.data);
export const getWorkflowVisualizationAPI = () =>
  http.get("/workflow/visualization").then((r) => r.data);

// Chat
export const chatAPI = (payload) =>
  http.post("/chat", payload).then((r) => r.data);
export const chatHTMLAPI = (payload) =>
  http.post("/chat/html", payload).then((r) => r.data);
export const executeActionAPI = (payload) =>
  http.post("/chat/execute", payload).then((r) => r.data);

// Transactions
export const listTransactionsAPI = (userId) =>
  http.get(`/transactions/${userId}`).then((r) => r.data);
export const getTransactionAPI = (userId, id) =>
  http.get(`/transactions/${userId}/${id}`).then((r) => r.data);
export const addTransactionAPI = (userId, payload) =>
  http.post(`/transactions/${userId}`, payload).then((r) => r.data);
export const updateTransactionAPI = (userId, id, payload) =>
  http.put(`/transactions/${userId}/${id}`, payload).then((r) => r.data);
export const deleteTransactionAPI = (userId, id) =>
  http.delete(`/transactions/${userId}/${id}`).then((r) => r.data);

// Goals
export const listGoalsAPI = (userId) =>
  http.get(`/goals/${userId}`).then((r) => r.data);
export const addGoalAPI = (userId, payload) =>
  http.post(`/goals/${userId}`, payload).then((r) => r.data);
export const getGoalAPI = (userId, id) =>
  http.get(`/goals/${userId}/${id}`).then((r) => r.data);
export const updateGoalAPI = (userId, id, payload) =>
  http.put(`/goals/${userId}/${id}`, payload).then((r) => r.data);
export const deleteGoalAPI = (userId, id) =>
  http.delete(`/goals/${userId}/${id}`).then((r) => r.data);

// Budgets
export const listBudgetsAPI = (userId) =>
  http.get(`/budgets/${userId}`).then((r) => r.data);
export const getBudgetAPI = (userId, id) =>
  http.get(`/budgets/${userId}/${id}`).then((r) => r.data);
export const addBudgetAPI = (userId, payload) =>
  http.post(`/budgets/${userId}`, payload).then((r) => r.data);
export const updateBudgetAPI = (userId, id, payload) =>
  http.put(`/budgets/${userId}/${id}`, payload).then((r) => r.data);
export const deleteBudgetAPI = (userId, id) =>
  http.delete(`/budgets/${userId}/${id}`).then((r) => r.data);

// Recurring
export const listRecurringAPI = (userId) =>
  http.get(`/recurring/${userId}`).then((r) => r.data);
export const createRecurringAPI = (userId, payload) =>
  http.post(`/recurring/${userId}`, payload).then((r) => r.data);
export const updateRecurringAPI = (userId, id, payload) =>
  http.put(`/recurring/${userId}/${id}`, payload).then((r) => r.data);
export const deleteRecurringAPI = (userId, id) =>
  http.delete(`/recurring/${userId}/${id}`).then((r) => r.data);
export const previewRecurringAPI = (userId, periods = 3) =>
  http
    .get(`/recurring/${userId}/preview`, { params: { periods } })
    .then((r) => r.data);
export const generateRecurringAPI = (userId, up_to) =>
  http
    .post(`/recurring/${userId}/generate`, null, {
      params: up_to ? { up_to } : {},
    })
    .then((r) => r.data);
