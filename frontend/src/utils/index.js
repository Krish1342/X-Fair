/**
 * Utility functions for the Finance Agent application
 */

// Format currency values
export const formatCurrency = (amount, currency = "USD", locale = "en-US") => {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return "$0.00";
  }

  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

// Format percentages
export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined || isNaN(value)) {
    return "0%";
  }

  return `${value.toFixed(decimals)}%`;
};

// Format large numbers with abbreviations
export const formatNumber = (num, decimals = 1) => {
  if (num === null || num === undefined || isNaN(num)) {
    return "0";
  }

  const absNum = Math.abs(num);

  if (absNum >= 1e9) {
    return (num / 1e9).toFixed(decimals) + "B";
  }
  if (absNum >= 1e6) {
    return (num / 1e6).toFixed(decimals) + "M";
  }
  if (absNum >= 1e3) {
    return (num / 1e3).toFixed(decimals) + "K";
  }

  return num.toFixed(decimals);
};

// Format dates
export const formatDate = (date, options = {}) => {
  if (!date) return "";

  const defaultOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
  };

  return new Intl.DateTimeFormat("en-US", {
    ...defaultOptions,
    ...options,
  }).format(new Date(date));
};

// Format relative time (e.g., "2 hours ago")
export const formatRelativeTime = (date) => {
  if (!date) return "";

  const now = new Date();
  const past = new Date(date);
  const diffInSeconds = Math.floor((now - past) / 1000);

  const units = [
    { name: "year", seconds: 31536000 },
    { name: "month", seconds: 2592000 },
    { name: "week", seconds: 604800 },
    { name: "day", seconds: 86400 },
    { name: "hour", seconds: 3600 },
    { name: "minute", seconds: 60 },
  ];

  for (const unit of units) {
    const interval = Math.floor(diffInSeconds / unit.seconds);
    if (interval >= 1) {
      return `${interval} ${unit.name}${interval > 1 ? "s" : ""} ago`;
    }
  }

  return "Just now";
};

// Validate email
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Validate password strength
export const validatePassword = (password) => {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  const errors = [];

  if (password.length < minLength) {
    errors.push(`Password must be at least ${minLength} characters long`);
  }
  if (!hasUpperCase) {
    errors.push("Password must contain at least one uppercase letter");
  }
  if (!hasLowerCase) {
    errors.push("Password must contain at least one lowercase letter");
  }
  if (!hasNumbers) {
    errors.push("Password must contain at least one number");
  }
  if (!hasSpecialChar) {
    errors.push("Password must contain at least one special character");
  }

  return {
    isValid: errors.length === 0,
    errors,
    strength:
      errors.length === 0 ? "strong" : errors.length <= 2 ? "medium" : "weak",
  };
};

// Deep clone object
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== "object") return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map((item) => deepClone(item));
  if (typeof obj === "object") {
    const copy = {};
    Object.keys(obj).forEach((key) => {
      copy[key] = deepClone(obj[key]);
    });
    return copy;
  }
};

// Debounce function
export const debounce = (func, wait, immediate = false) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func(...args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func(...args);
  };
};

// Throttle function
export const throttle = (func, limit) => {
  let inThrottle;
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

// Generate random ID
export const generateId = (prefix = "") => {
  const timestamp = Date.now().toString(36);
  const randomPart = Math.random().toString(36).substr(2, 9);
  return `${prefix}${timestamp}_${randomPart}`;
};

// Calculate financial metrics
export const calculateCompoundInterest = (
  principal,
  rate,
  time,
  compound = 12
) => {
  return principal * Math.pow(1 + rate / compound, compound * time);
};

export const calculateMonthlyPayment = (principal, rate, years) => {
  const monthlyRate = rate / 12;
  const numPayments = years * 12;

  if (rate === 0) return principal / numPayments;

  return (
    (principal * monthlyRate * Math.pow(1 + monthlyRate, numPayments)) /
    (Math.pow(1 + monthlyRate, numPayments) - 1)
  );
};

export const calculateROI = (initialValue, finalValue) => {
  if (initialValue === 0) return 0;
  return ((finalValue - initialValue) / initialValue) * 100;
};

// Color utilities for charts and UI
export const getColorByValue = (
  value,
  thresholds = { low: 30, medium: 70 }
) => {
  if (value <= thresholds.low) return "#ef4444"; // red
  if (value <= thresholds.medium) return "#f59e0b"; // yellow
  return "#22c55e"; // green
};

export const generateChartColors = (count) => {
  const colors = [
    "#3b82f6",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#8b5cf6",
    "#06b6d4",
    "#84cc16",
    "#f97316",
    "#ec4899",
    "#6366f1",
  ];

  if (count <= colors.length) {
    return colors.slice(0, count);
  }

  // Generate additional colors if needed
  const additionalColors = [];
  for (let i = colors.length; i < count; i++) {
    const hue = (i * 137.508) % 360; // Golden angle approximation
    additionalColors.push(`hsl(${hue}, 70%, 50%)`);
  }

  return [...colors, ...additionalColors];
};

// URL and query string utilities
export const getQueryParams = (url = window.location.search) => {
  const params = new URLSearchParams(url);
  const result = {};
  for (const [key, value] of params) {
    result[key] = value;
  }
  return result;
};

export const buildQueryString = (params) => {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      searchParams.append(key, value);
    }
  });
  return searchParams.toString();
};

// Local storage utilities with error handling
export const storage = {
  get: (key, defaultValue = null) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error("Error reading from localStorage:", error);
      return defaultValue;
    }
  },

  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error("Error writing to localStorage:", error);
      return false;
    }
  },

  remove: (key) => {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error("Error removing from localStorage:", error);
      return false;
    }
  },

  clear: () => {
    try {
      localStorage.clear();
      return true;
    } catch (error) {
      console.error("Error clearing localStorage:", error);
      return false;
    }
  },
};

// CSS class utilities
export const cn = (...classes) => {
  return classes.filter(Boolean).join(" ");
};

// Animation utilities
export const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { duration: 0.3 },
};

export const slideUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3 },
};

export const slideIn = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
  transition: { duration: 0.3 },
};
