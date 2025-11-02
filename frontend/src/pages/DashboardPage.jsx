/**
 * Dashboard Page Component - Main dashboard layout
 */
import React from "react";
import { useApp } from "@store/AppContext";
import Dashboard from "@features/Dashboard";

const DashboardPage = () => {
  const { state } = useApp();

  // Redirect to login if not authenticated
  if (!state.user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Please log in to continue
          </h2>
          <p className="text-gray-600">
            You need to be logged in to access the dashboard.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <Dashboard />
      </div>
    </div>
  );
};

export default DashboardPage;
