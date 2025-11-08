import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Upload transactions from CSV or Excel file
 * @param {File} file - The file to upload
 * @param {number} userId - The user ID
 * @returns {Promise} Upload result with summary
 */
export const uploadTransactionsFile = async (file, userId) => {
  const formData = new FormData();
  formData.append("file", file);

  const token = window.localStorage?.getItem("finance_token");

  const response = await axios.post(
    `${API_BASE}/upload/transactions/${userId}`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: token ? `Bearer ${token}` : "",
      },
    }
  );

  return response.data;
};

/**
 * Parse UPI transaction message
 * @param {string} message - The UPI SMS message
 * @param {number} userId - The user ID
 * @returns {Promise} Parsed transaction data
 */
export const parseUPIMessage = async (message, userId) => {
  const token = window.localStorage?.getItem("finance_token");

  const formData = new FormData();
  formData.append("message", message);

  const response = await axios.post(
    `${API_BASE}/upload/upi-message/${userId}`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: token ? `Bearer ${token}` : "",
      },
    }
  );

  return response.data;
};
