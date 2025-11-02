import React from "react";
import { cn } from "@utils";

/**
 * Modern Button Component with Beautiful Design
 * Enhanced UX with proper states, animations, and accessibility
 */
const Button = ({
  children,
  variant = "primary",
  size = "md",
  disabled = false,
  isLoading = false,
  onClick,
  type = "button",
  className = "",
  icon: Icon,
  iconPosition = "left",
  fullWidth = false,
  ...props
}) => {
  const baseClasses = "btn";

  const variantClasses = {
    primary: "btn-primary",
    secondary: "btn-secondary",
    outline: "btn-outline",
    ghost: "btn-ghost",
    danger: "btn-danger",
  };

  const sizeClasses = {
    sm: "btn-sm",
    md: "btn-md",
    lg: "btn-lg",
    xl: "btn-xl",
  };

  const isDisabled = disabled || isLoading;

  const buttonClasses = cn(
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    fullWidth && "w-full",
    className
  );

  return (
    <button
      type={type}
      className={buttonClasses}
      disabled={isDisabled}
      onClick={onClick}
      {...props}
    >
      {/* Loading spinner */}
      {isLoading && (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4"
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
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}

      {/* Left icon */}
      {Icon && iconPosition === "left" && !isLoading && (
        <Icon className="w-4 h-4 mr-2" />
      )}

      {/* Button text */}
      <span className={isLoading ? "opacity-70" : ""}>{children}</span>

      {/* Right icon */}
      {Icon && iconPosition === "right" && !isLoading && (
        <Icon className="w-4 h-4 ml-2" />
      )}
    </button>
  );
};

export default Button;
