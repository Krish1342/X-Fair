/**
 * Main App Component with Routing
 */
import React, { useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { AppProvider, useApp } from "@store/AppContext.jsx";
import Layout from "@layout/Layout";
import HomePage from "@pages/HomePage";
import LoginPage from "@pages/LoginPage";
import DashboardPage from "@pages/DashboardPage";
import OnboardingPage from "@pages/OnboardingPage";
import NotFoundPage from "@pages/NotFoundPage";
import WorkflowPage from "@pages/WorkflowPage";
import { verifyTokenAPI } from "@api/finance";
import AIPage from "@pages/AIPage";
import TransactionsPage from "@pages/TransactionsPage";

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { state } = useApp();

  if (!state.user) {
    return <Navigate to="/" replace />;
  }

  return children;
};

// App Content Component (inside AppProvider)
const AppContent = () => {
  const { state, dispatch } = useApp();

  // Initialize app on mount
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Check for existing auth token
        const token = localStorage.getItem("finance_token");
        if (token) {
          // Verify token and get user data
          const userData = await verifyTokenAPI();
          dispatch({
            type: "SET_USER",
            payload: userData.user,
          });

          if (userData.userProfile) {
            dispatch({
              type: "SET_USER_PROFILE",
              payload: userData.userProfile,
            });
          }

          if (userData.workflowStage) {
            dispatch({
              type: "SET_WORKFLOW_STAGE",
              payload: userData.workflowStage,
            });
          }
        }
      } catch (error) {
        // Token invalid, clear it
        localStorage.removeItem("finance_token");
        console.log("Token verification failed:", error);
      } finally {
        dispatch({
          type: "SET_LOADING",
          payload: false,
        });
      }
    };

    initializeApp();
  }, [dispatch]);

  // Show loading screen during initialization
  if (state.isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your finance dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <Router
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <Layout>
        <Routes>
          {/* Public Routes */}
          <Route
            path="/"
            element={
              state.user ? <Navigate to="/dashboard" replace /> : <HomePage />
            }
          />
          <Route
            path="/login"
            element={
              state.user ? <Navigate to="/dashboard" replace /> : <LoginPage />
            }
          />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/ai"
            element={
              <ProtectedRoute>
                <AIPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/workflow"
            element={
              <ProtectedRoute>
                <WorkflowPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/transactions"
            element={
              <ProtectedRoute>
                <TransactionsPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/onboarding"
            element={
              <ProtectedRoute>
                <OnboardingPage />
              </ProtectedRoute>
            }
          />

          {/* Catch all route */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Layout>
    </Router>
  );
};

// Main App Component
const App = () => {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
};

export default App;
