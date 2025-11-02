/**
 * Main Layout Component
 * Provides the overall structure for the application
 */
import React from "react";
import { useLocation } from "react-router-dom";
import { useAppState, useAppActions } from "@store/AppContext";
import Header from "./Header";
import Footer from "./Footer";
import ChatBot from "@features/ChatBot";
import LoginModal from "@components/features/LoginModal";
import Toast from "@components/ui/Toast";
import LoadingSpinner from "@components/ui/LoadingSpinner";

const Layout = ({ children }) => {
  const { showLogin, isLoading, toast, error } = useAppState();
  const { clearError, clearToast } = useAppActions();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="flex-1 relative">
        {children}

        {/* Global Loading Overlay */}
        {isLoading && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <LoadingSpinner size="lg" />
          </div>
        )}
      </main>

      {/* Footer */}
      <Footer />

      {/* Simple ChatBot */}
      <ChatBot />

      {/* Login Modal */}
      {showLogin && <LoginModal />}

      {/* Toast Notifications */}
      {toast && (
        <Toast message={toast.message} type={toast.type} onClose={clearToast} />
      )}

      {/* Error Toast */}
      {error && <Toast message={error} type="error" onClose={clearError} />}
    </div>
  );
};

export default Layout;
