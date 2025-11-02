/**
 * Global state management using React Context
 * Simplified state management for the Finance Agent application
 */
import React, {
  createContext,
  useContext,
  useReducer,
  useCallback,
} from "react";
import { storage } from "@utils";

// Initial state
const initialState = {
  // User state
  user: null,
  isAuthenticated: false,

  // App state
  currentView: "home",
  workflowStage: "started",
  availableFeatures: [],

  // Chat state
  chatHistory: [],
  isLoading: false,

  // UI state
  showChatBot: false,
  showLogin: false,
  sidebarOpen: false,

  // Data state
  financialData: null,
  analysisResults: {},

  // Settings
  preferences: {
    theme: "light",
    currency: "USD",
    notifications: true,
  },

  // Error handling
  error: null,
  toast: null,
};

// Action types
const ActionTypes = {
  // User actions
  SET_USER: "SET_USER",
  LOGOUT: "LOGOUT",

  // App actions
  SET_CURRENT_VIEW: "SET_CURRENT_VIEW",
  SET_WORKFLOW_STAGE: "SET_WORKFLOW_STAGE",
  SET_AVAILABLE_FEATURES: "SET_AVAILABLE_FEATURES",

  // Chat actions
  ADD_CHAT_MESSAGE: "ADD_CHAT_MESSAGE",
  CLEAR_CHAT_HISTORY: "CLEAR_CHAT_HISTORY",
  SET_LOADING: "SET_LOADING",

  // UI actions
  TOGGLE_CHAT_BOT: "TOGGLE_CHAT_BOT",
  TOGGLE_LOGIN: "TOGGLE_LOGIN",
  TOGGLE_SIDEBAR: "TOGGLE_SIDEBAR",

  // Data actions
  SET_FINANCIAL_DATA: "SET_FINANCIAL_DATA",
  SET_ANALYSIS_RESULTS: "SET_ANALYSIS_RESULTS",

  // Settings actions
  SET_PREFERENCES: "SET_PREFERENCES",

  // Error handling
  SET_ERROR: "SET_ERROR",
  CLEAR_ERROR: "CLEAR_ERROR",
  SET_TOAST: "SET_TOAST",
  CLEAR_TOAST: "CLEAR_TOAST",
};

// Reducer function
const appReducer = (state, action) => {
  switch (action.type) {
    case ActionTypes.SET_USER:
      return {
        ...state,
        user: action.payload,
        isAuthenticated: !!action.payload,
      };

    case ActionTypes.LOGOUT:
      storage.remove("user");
      storage.remove("authToken");
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        chatHistory: [],
        financialData: null,
        analysisResults: {},
      };

    case ActionTypes.SET_CURRENT_VIEW:
      return {
        ...state,
        currentView: action.payload,
      };

    case ActionTypes.SET_WORKFLOW_STAGE:
      return {
        ...state,
        workflowStage: action.payload,
      };

    case ActionTypes.SET_AVAILABLE_FEATURES:
      return {
        ...state,
        availableFeatures: action.payload,
      };

    case ActionTypes.ADD_CHAT_MESSAGE:
      const newChatHistory = [...state.chatHistory, action.payload];
      return {
        ...state,
        chatHistory: newChatHistory,
      };

    case ActionTypes.CLEAR_CHAT_HISTORY:
      return {
        ...state,
        chatHistory: [],
      };

    case ActionTypes.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload,
      };

    case ActionTypes.TOGGLE_CHAT_BOT:
      return {
        ...state,
        showChatBot:
          action.payload !== undefined ? action.payload : !state.showChatBot,
      };

    case ActionTypes.TOGGLE_LOGIN:
      return {
        ...state,
        showLogin:
          action.payload !== undefined ? action.payload : !state.showLogin,
      };

    case ActionTypes.TOGGLE_SIDEBAR:
      return {
        ...state,
        sidebarOpen:
          action.payload !== undefined ? action.payload : !state.sidebarOpen,
      };

    case ActionTypes.SET_FINANCIAL_DATA:
      return {
        ...state,
        financialData: action.payload,
      };

    case ActionTypes.SET_ANALYSIS_RESULTS:
      return {
        ...state,
        analysisResults: { ...state.analysisResults, ...action.payload },
      };

    case ActionTypes.SET_PREFERENCES:
      const newPreferences = { ...state.preferences, ...action.payload };
      storage.set("preferences", newPreferences);
      return {
        ...state,
        preferences: newPreferences,
      };

    case ActionTypes.SET_ERROR:
      return {
        ...state,
        error: action.payload,
      };

    case ActionTypes.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    case ActionTypes.SET_TOAST:
      return {
        ...state,
        toast: action.payload,
      };

    case ActionTypes.CLEAR_TOAST:
      return {
        ...state,
        toast: null,
      };

    default:
      return state;
  }
};

// Create contexts
const AppStateContext = createContext();
const AppDispatchContext = createContext();

// Provider component
export const AppProvider = ({ children }) => {
  // Load initial state from localStorage
  const loadInitialState = () => {
    const savedUser = storage.get("user");
    const savedPreferences = storage.get("preferences");

    return {
      ...initialState,
      user: savedUser,
      isAuthenticated: !!savedUser,
      preferences: { ...initialState.preferences, ...savedPreferences },
    };
  };

  const [state, dispatch] = useReducer(appReducer, loadInitialState());

  return (
    <AppStateContext.Provider value={state}>
      <AppDispatchContext.Provider value={dispatch}>
        {children}
      </AppDispatchContext.Provider>
    </AppStateContext.Provider>
  );
};

// Custom hooks for accessing state and dispatch
export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error("useAppState must be used within an AppProvider");
  }
  return context;
};

export const useAppDispatch = () => {
  const context = useContext(AppDispatchContext);
  if (!context) {
    throw new Error("useAppDispatch must be used within an AppProvider");
  }
  return context;
};

// Action creators
export const useAppActions = () => {
  const dispatch = useAppDispatch();

  return {
    // User actions
    setUser: useCallback(
      (user) => {
        storage.set("user", user);
        dispatch({ type: ActionTypes.SET_USER, payload: user });
      },
      [dispatch]
    ),

    logout: useCallback(() => {
      dispatch({ type: ActionTypes.LOGOUT });
    }, [dispatch]),

    // App actions
    setCurrentView: useCallback(
      (view) => {
        dispatch({ type: ActionTypes.SET_CURRENT_VIEW, payload: view });
      },
      [dispatch]
    ),

    setWorkflowStage: useCallback(
      (stage) => {
        dispatch({ type: ActionTypes.SET_WORKFLOW_STAGE, payload: stage });
      },
      [dispatch]
    ),

    setAvailableFeatures: useCallback(
      (features) => {
        dispatch({
          type: ActionTypes.SET_AVAILABLE_FEATURES,
          payload: features,
        });
      },
      [dispatch]
    ),

    // Chat actions
    addChatMessage: useCallback(
      (message) => {
        dispatch({ type: ActionTypes.ADD_CHAT_MESSAGE, payload: message });
      },
      [dispatch]
    ),

    clearChatHistory: useCallback(() => {
      dispatch({ type: ActionTypes.CLEAR_CHAT_HISTORY });
    }, [dispatch]),

    setLoading: useCallback(
      (loading) => {
        dispatch({ type: ActionTypes.SET_LOADING, payload: loading });
      },
      [dispatch]
    ),

    // UI actions
    toggleChatBot: useCallback(
      (show) => {
        dispatch({ type: ActionTypes.TOGGLE_CHAT_BOT, payload: show });
      },
      [dispatch]
    ),

    toggleLogin: useCallback(
      (show) => {
        dispatch({ type: ActionTypes.TOGGLE_LOGIN, payload: show });
      },
      [dispatch]
    ),

    toggleSidebar: useCallback(
      (open) => {
        dispatch({ type: ActionTypes.TOGGLE_SIDEBAR, payload: open });
      },
      [dispatch]
    ),

    // Data actions
    setFinancialData: useCallback(
      (data) => {
        dispatch({ type: ActionTypes.SET_FINANCIAL_DATA, payload: data });
      },
      [dispatch]
    ),

    setAnalysisResults: useCallback(
      (results) => {
        dispatch({ type: ActionTypes.SET_ANALYSIS_RESULTS, payload: results });
      },
      [dispatch]
    ),

    // Settings actions
    setPreferences: useCallback(
      (preferences) => {
        dispatch({ type: ActionTypes.SET_PREFERENCES, payload: preferences });
      },
      [dispatch]
    ),

    // Error handling
    setError: useCallback(
      (error) => {
        dispatch({ type: ActionTypes.SET_ERROR, payload: error });
      },
      [dispatch]
    ),

    clearError: useCallback(() => {
      dispatch({ type: ActionTypes.CLEAR_ERROR });
    }, [dispatch]),

    setToast: useCallback(
      (toast) => {
        dispatch({ type: ActionTypes.SET_TOAST, payload: toast });
        // Auto-clear toast after 5 seconds
        setTimeout(() => {
          dispatch({ type: ActionTypes.CLEAR_TOAST });
        }, 5000);
      },
      [dispatch]
    ),

    clearToast: useCallback(() => {
      dispatch({ type: ActionTypes.CLEAR_TOAST });
    }, [dispatch]),
  };
};

// Combined hook for convenience
export const useApp = () => {
  const state = useAppState();
  const dispatch = useAppDispatch();
  const actions = useAppActions();

  return {
    state,
    dispatch,
    ...actions,
  };
};
