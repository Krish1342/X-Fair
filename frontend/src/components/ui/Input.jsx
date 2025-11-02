import React, { forwardRef, useState } from "react";
import { cn } from "@utils";

/**
 * Modern Input Component with Beautiful Design
 * Enhanced UX with proper validation, states, and accessibility
 */
const Input = forwardRef(
  (
    {
      type = "text",
      placeholder = "",
      value,
      onChange,
      onBlur,
      onFocus,
      disabled = false,
      error = false,
      className = "",
      label,
      helperText,
      required = false,
      icon: Icon,
      iconPosition = "left",
      ...props
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = useState(false);

    const handleFocus = (e) => {
      setIsFocused(true);
      onFocus?.(e);
    };

    const handleBlur = (e) => {
      setIsFocused(false);
      onBlur?.(e);
    };

    const inputClasses = cn(
      "input-field",
      error && "input-error",
      Icon && iconPosition === "left" && "pl-10",
      Icon && iconPosition === "right" && "pr-10",
      disabled && "opacity-50 cursor-not-allowed",
      className
    );

    return (
      <div className="space-y-2">
        {/* Label */}
        {label && (
          <label className="block text-sm font-medium text-slate-700">
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}

        {/* Input container */}
        <div className="relative">
          {/* Left icon */}
          {Icon && iconPosition === "left" && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Icon
                className={cn(
                  "h-5 w-5",
                  error
                    ? "text-red-400"
                    : isFocused
                    ? "text-blue-500"
                    : "text-slate-400"
                )}
              />
            </div>
          )}

          {/* Input field */}
          <input
            ref={ref}
            type={type}
            placeholder={placeholder}
            value={value}
            onChange={onChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            disabled={disabled}
            className={inputClasses}
            required={required}
            {...props}
          />

          {/* Right icon */}
          {Icon && iconPosition === "right" && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <Icon
                className={cn(
                  "h-5 w-5",
                  error
                    ? "text-red-400"
                    : isFocused
                    ? "text-blue-500"
                    : "text-slate-400"
                )}
              />
            </div>
          )}
        </div>

        {/* Helper text */}
        {helperText && (
          <p
            className={cn("text-sm", error ? "text-red-600" : "text-slate-500")}
          >
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
