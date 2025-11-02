/**
 * Login Page Component
 * Standalone login page with proper form handling
 */
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useApp } from "@store/AppContext";
import { loginAPI, registerAPI } from "@api/finance";
import Button from "@ui/Button";
import Input from "@ui/Input";
import Toast from "@ui/Toast";
import { cn } from "@utils";

const LoginPage = () => {
  const navigate = useNavigate();
  const { dispatch } = useApp();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    name: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (message, type = "info") => {
    setToast({ message, type });
  };

  const hideToast = () => {
    setToast(null);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const validateForm = () => {
    if (!formData.email || !formData.password) {
      showToast("Please fill in all required fields", "error");
      return false;
    }

    if (!isLogin && formData.password !== formData.confirmPassword) {
      showToast("Passwords do not match", "error");
      return false;
    }

    if (!isLogin && (!formData.name || formData.name.length < 2)) {
      showToast("Please enter a valid name", "error");
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsLoading(true);
    hideToast();

    try {
      let response;

      if (isLogin) {
        response = await loginAPI({
          email: formData.email,
          password: formData.password,
        });
      } else {
        response = await registerAPI({
          email: formData.email,
          password: formData.password,
          name: formData.name,
        });
      }

      // Handle successful auth
      dispatch({
        type: "SET_USER",
        payload: {
          id: response.user.id,
          email: response.user.email,
          name: response.user.name,
        },
      });

      localStorage.setItem("finance_token", response.token);

      showToast(
        isLogin
          ? "Login successful! Welcome back!"
          : "Registration successful! Welcome to Finance Agent!",
        "success"
      );

      // Redirect to dashboard after short delay
      setTimeout(() => {
        navigate("/dashboard");
      }, 1500);
    } catch (error) {
      showToast(
        error.message ||
          (isLogin
            ? "Login failed. Please check your credentials."
            : "Registration failed. Please try again."),
        "error"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setIsLoading(true);
    hideToast();

    try {
      const response = await loginAPI({
        email: "demo@example.com",
        password: "demo123",
      });

      dispatch({
        type: "SET_USER",
        payload: {
          id: response.user.id,
          email: response.user.email,
          name: response.user.name,
        },
      });

      localStorage.setItem("finance_token", response.token);
      showToast("Demo login successful! Welcome to the demo!", "success");

      setTimeout(() => {
        navigate("/dashboard");
      }, 1500);
    } catch (error) {
      showToast("Demo login failed. Please try again.", "error");
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setFormData({
      email: "",
      password: "",
      confirmPassword: "",
      name: "",
    });
    hideToast();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Logo and Header */}
        <Link
          to="/"
          className="flex items-center justify-center space-x-3 mb-8 group"
        >
          <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
            <svg
              className="w-7 h-7 text-white"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4zM18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" />
            </svg>
          </div>
          <span className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            Finance Agent
          </span>
        </Link>

        <div className="text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-3">
            {isLogin ? "Welcome back!" : "Join Finance Agent"}
          </h2>
          <p className="text-lg text-gray-600">
            {isLogin
              ? "Sign in to continue your financial journey"
              : "Start taking control of your finances today"}
          </p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-10 px-6 shadow-2xl sm:rounded-2xl sm:px-12 border border-gray-100 backdrop-blur-sm">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* Name field for registration */}
            {!isLogin && (
              <div className="space-y-2">
                <label
                  htmlFor="name"
                  className="block text-sm font-semibold text-gray-700"
                >
                  Full Name
                </label>
                <div className="relative">
                  <Input
                    id="name"
                    name="name"
                    type="text"
                    autoComplete="name"
                    required={!isLogin}
                    value={formData.name}
                    onChange={handleInputChange}
                    className="appearance-none block w-full px-4 py-3 border border-gray-300 rounded-xl placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-all bg-gray-50 focus:bg-white"
                    placeholder="Enter your full name"
                  />
                </div>
              </div>
            )}

            {/* Email field */}
            <div className="space-y-2">
              <label
                htmlFor="email"
                className="block text-sm font-semibold text-gray-700"
              >
                Email address
              </label>
              <div className="relative">
                <Input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={handleInputChange}
                  className="appearance-none block w-full px-4 py-3 border border-gray-300 rounded-xl placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-all bg-gray-50 focus:bg-white"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            {/* Password field */}
            <div className="space-y-2">
              <label
                htmlFor="password"
                className="block text-sm font-semibold text-gray-700"
              >
                Password
              </label>
              <div className="relative">
                <Input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete={isLogin ? "current-password" : "new-password"}
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  className="appearance-none block w-full px-4 py-3 border border-gray-300 rounded-xl placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-all bg-gray-50 focus:bg-white"
                  placeholder="Enter your password"
                />
              </div>
            </div>

            {/* Confirm Password field for registration */}
            {!isLogin && (
              <div className="space-y-2">
                <label
                  htmlFor="confirmPassword"
                  className="block text-sm font-semibold text-gray-700"
                >
                  Confirm Password
                </label>
                <div className="relative">
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    autoComplete="new-password"
                    required={!isLogin}
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    className="appearance-none block w-full px-4 py-3 border border-gray-300 rounded-xl placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-all bg-gray-50 focus:bg-white"
                    placeholder="Confirm your password"
                  />
                </div>
              </div>
            )}

            {/* Submit Button */}
            <div className="pt-2">
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-4 px-6 border border-transparent rounded-xl shadow-lg text-base font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
              >
                {isLoading ? (
                  <>
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    {isLogin ? "Signing in..." : "Creating account..."}
                  </>
                ) : isLogin ? (
                  "Sign In"
                ) : (
                  "Create Account"
                )}
              </Button>
            </div>

            {/* Demo Login Button */}
            {isLogin && (
              <div>
                <Button
                  type="button"
                  onClick={handleDemoLogin}
                  disabled={isLoading}
                  className="w-full flex justify-center py-3 px-4 border-2 border-gray-300 rounded-xl shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  Try Demo Login
                </Button>
              </div>
            )}
          </form>

          {/* Toggle between login/register */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">
                  {isLogin
                    ? "New to Finance Agent?"
                    : "Already have an account?"}
                </span>
              </div>
            </div>

            <div className="mt-6">
              <button
                type="button"
                onClick={toggleMode}
                className="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium text-blue-600 hover:text-blue-500 focus:outline-none focus:underline transition-colors"
              >
                {isLogin
                  ? "Create a new account"
                  : "Sign in to existing account"}
              </button>
            </div>
          </div>

          {/* Back to Home Link */}
          <div className="mt-6 text-center">
            <Link
              to="/"
              className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
            >
              ← Back to home
            </Link>
          </div>
        </div>
      </div>

      {/* Toast Notifications */}
      {toast && (
        <Toast message={toast.message} type={toast.type} onClose={hideToast} />
      )}
    </div>
  );
};

export default LoginPage;
