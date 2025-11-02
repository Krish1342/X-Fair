import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Dummy users for basic authentication
  const dummyUsers = [
    {
      id: 1,
      username: "john_doe",
      email: "john@example.com",
      password: "password123",
      name: "John Doe",
    },
    {
      id: 2,
      username: "jane_smith",
      email: "jane@example.com",
      password: "password123",
      name: "Jane Smith",
    },
    {
      id: 3,
      username: "demo",
      email: "demo@example.com",
      password: "demo",
      name: "Demo User",
    },
  ];

  useEffect(() => {
    // Check if user is already logged in (from localStorage)
    const savedUser = localStorage.getItem("finance_user");
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        localStorage.removeItem("finance_user");
      }
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      // Find user in dummy data
      const foundUser = dummyUsers.find(
        (user) =>
          (user.username === username || user.email === username) &&
          user.password === password
      );

      if (foundUser) {
        const userData = {
          id: foundUser.id,
          username: foundUser.username,
          email: foundUser.email,
          name: foundUser.name,
        };

        setUser(userData);
        setIsAuthenticated(true);
        localStorage.setItem("finance_user", JSON.stringify(userData));
        return { success: true, user: userData };
      } else {
        return { success: false, message: "Invalid username or password" };
      }
    } catch (error) {
      return { success: false, message: "Login failed. Please try again." };
    }
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem("finance_user");
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    dummyUsers: dummyUsers.map((user) => ({
      username: user.username,
      email: user.email,
    })),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
