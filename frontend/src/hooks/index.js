/**
 * Custom React hooks for the Finance Agent application
 */
import { useState, useEffect, useCallback, useRef } from "react";
import { chatAPI, getWorkflowStatusAPI } from "@api/finance";

// Hook for managing chat functionality
export const useChat = (userId = null) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = useCallback(
    async (query) => {
      if (!query.trim()) return;

      setIsLoading(true);
      setError(null);

      // Add user message to chat
      const userMessage = {
        id: Date.now(),
        type: "user",
        content: query,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      try {
        const response = await chatAPI({ message: query, user_id: userId });

        // Add AI response to chat
        const aiMessage = {
          id: Date.now() + 1,
          type: "assistant",
          content: response.response,
          intent: response.intent,
          stage: response.stage,
          tools_used: response.tools_used,
          analysis_results: response.analysis_results,
          suggestions: response.suggestions,
          visualizations: response.visualizations,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMessage]);

        return response;
      } catch (err) {
        setError(err.message);

        // Add error message to chat
        const errorMessage = {
          id: Date.now() + 1,
          type: "error",
          content: `Sorry, I encountered an error: ${err.message}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [userId, messages]
  );

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
  };
};

// Hook for managing workflow status
export const useWorkflowStatus = (userId) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStatus = useCallback(async () => {
    if (!userId) return;

    setLoading(true);
    setError(null);

    try {
      const statusData = await getWorkflowStatusAPI(userId);
      setStatus(statusData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  return {
    status,
    loading,
    error,
    refetch: fetchStatus,
  };
};

// Hook for API loading states
export const useAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (apiCall) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiCall();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    execute,
    clearError: () => setError(null),
  };
};

// Hook for local storage management
export const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback(
    (value) => {
      try {
        const valueToStore =
          value instanceof Function ? value(storedValue) : value;
        setStoredValue(valueToStore);
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      } catch (error) {
        console.error(`Error setting localStorage key "${key}":`, error);
      }
    },
    [key, storedValue]
  );

  const removeValue = useCallback(() => {
    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue];
};

// Hook for debounced input
export const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Hook for intersection observer (for animations)
export const useIntersectionObserver = (options = {}) => {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [hasIntersected, setHasIntersected] = useState(false);
  const elementRef = useRef();

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      setIsIntersecting(entry.isIntersecting);
      if (entry.isIntersecting && !hasIntersected) {
        setHasIntersected(true);
      }
    }, options);

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [options, hasIntersected]);

  return [elementRef, isIntersecting, hasIntersected];
};

// Hook for window size
export const useWindowSize = () => {
  const [windowSize, setWindowSize] = useState({
    width: undefined,
    height: undefined,
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener("resize", handleResize);
    handleResize(); // Call handler right away so state gets updated with initial window size

    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return windowSize;
};
