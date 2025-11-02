/**
 * Login Modal Component
 */
import React, { useState } from "react";
import { useApp } from "@store/AppContext";
import { loginAPI, registerAPI } from "@api/finance";
import Modal from "@ui/Modal";
import Button from "@ui/Button";
import Input from "@ui/Input";
import Toast from "@ui/Toast";
import { cn } from "@utils";

const LoginModal = ({ isOpen, onClose }) => {
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

    if (!isLogin && formData.password.length < 6) {
      showToast("Password must be at least 6 characters long", "error");
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsLoading(true);

    try {
      let response;

      if (isLogin) {
        response = await loginAPI({
          email: formData.email,
          password: formData.password,
        });
      } else {
        response = await registerAPI({
          name: formData.name,
          email: formData.email,
          password: formData.password,
        });
      }

      // Store auth data
      dispatch({
        type: "SET_USER",
        payload: {
          id: response.user.id,
          email: response.user.email,
          name: response.user.name,
        },
      });

      // Store token
      localStorage.setItem("finance_token", response.token);

      showToast(`${isLogin ? "Login" : "Registration"} successful!`, "success");

      // Close modal after short delay
      setTimeout(() => {
        onClose();
        setFormData({
          email: "",
          password: "",
          confirmPassword: "",
          name: "",
        });
      }, 1500);
    } catch (error) {
      showToast(
        error.message ||
          `${isLogin ? "Login" : "Registration"} failed. Please try again.`,
        "error"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setIsLoading(true);
    try {
      // Demo credentials
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
        onClose();
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

  const handleGoogleLogin = async () => {
    try {
      // Placeholder for Google OAuth integration
      showToast("Google login coming soon!", "info");
    } catch (error) {
      showToast("Google login failed", "error");
    }
  };

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        title={isLogin ? "Sign In" : "Create Account"}
      >
        <div className="space-y-6">
          {/* Auth Method Toggle */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setIsLogin(true)}
              className={cn(
                "flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors",
                isLogin
                  ? "bg-white text-blue-600 shadow-sm"
                  : "text-gray-600 hover:text-blue-600"
              )}
            >
              Sign In
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={cn(
                "flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors",
                !isLogin
                  ? "bg-white text-blue-600 shadow-sm"
                  : "text-gray-600 hover:text-blue-600"
              )}
            >
              Sign Up
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <Input
                label="Full Name"
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Enter your full name"
                required={!isLogin}
              />
            )}

            <Input
              label="Email Address"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="Enter your email"
              required
            />

            <Input
              label="Password"
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="Enter your password"
              required
            />

            {!isLogin && (
              <Input
                label="Confirm Password"
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                placeholder="Confirm your password"
                required={!isLogin}
              />
            )}

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              className="w-full"
            >
              {isLogin ? "Sign In" : "Create Account"}
            </Button>
          </form>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">
                Or continue with
              </span>
            </div>
          </div>

          {/* Social Login */}
          <div className="space-y-3">
            <Button
              onClick={handleGoogleLogin}
              variant="outline"
              size="lg"
              className="w-full"
            >
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Continue with Google
            </Button>

            {/* Demo Login - More Prominent */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-blue-200" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-3 bg-white text-blue-600 font-medium">
                  Try the Demo
                </span>
              </div>
            </div>

            <Button
              onClick={handleDemoLogin}
              variant="primary"
              size="lg"
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
              isLoading={isLoading}
            >
              🚀 Try Demo Account
            </Button>

            <p className="text-xs text-center text-gray-500 mt-2">
              Explore all features with pre-loaded demo data
            </p>
          </div>

          {/* Footer */}
          <div className="text-center text-sm text-gray-600">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              onClick={toggleMode}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              {isLogin ? "Sign up" : "Sign in"}
            </button>
          </div>

          {isLogin && (
            <div className="text-center">
              <button className="text-sm text-blue-600 hover:text-blue-700">
                Forgot your password?
              </button>
            </div>
          )}
        </div>
      </Modal>

      {toast && (
        <Toast message={toast.message} type={toast.type} onClose={hideToast} />
      )}
    </>
  );
};

export default LoginModal;
