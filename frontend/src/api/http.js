import axios from "axios";

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Attach token from localStorage if present
http.interceptors.request.use((config) => {
  const token =
    typeof window !== "undefined" &&
    window.localStorage?.getItem("finance_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Normalize response and errors
http.interceptors.response.use(
  (res) => res,
  (error) => {
    const data = error?.response?.data;
    const msg =
      data?.detail || data?.message || error.message || "Request failed";
    return Promise.reject(new Error(msg));
  }
);

export default http;
