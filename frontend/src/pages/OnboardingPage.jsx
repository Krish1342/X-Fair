/**
 * Onboarding Page Component - User onboarding flow
 */
import React, { useState } from "react";
import { useApp } from "@store/AppContext";
// Note: Onboarding API is not implemented on backend yet.
// We keep local state and set workflow stage on completion.
import Button from "@ui/Button";
import Input from "@ui/Input";
import LoadingSpinner from "@ui/LoadingSpinner";
import { cn } from "@utils";

const OnboardingPage = () => {
  const { state, dispatch } = useApp();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    personalInfo: {
      age: "",
      occupation: "",
      annualIncome: "",
      financialExperience: "beginner",
    },
    financialGoals: {
      primaryGoal: "",
      timeframe: "",
      targetAmount: "",
      secondaryGoals: [],
    },
    preferences: {
      riskTolerance: "moderate",
      investmentInterests: [],
      budgetingStyle: "detailed",
      notifications: true,
    },
  });

  const totalSteps = 3;

  const handleInputChange = (section, field, value) => {
    setFormData((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }));
  };

  const handleArrayInputChange = (section, field, value, isChecked) => {
    setFormData((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: isChecked
          ? [...prev[section][field], value]
          : prev[section][field].filter((item) => item !== value),
      },
    }));
  };

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    setIsLoading(true);
    try {
      // In absence of a backend onboarding endpoint, just set local state
      dispatch({ type: "SET_USER_PROFILE", payload: formData });
      dispatch({ type: "SET_WORKFLOW_STAGE", payload: "MVP" });
      window.location.href = "/dashboard";
    } catch (error) {
      console.error("Onboarding completion error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <PersonalInfoStep
            formData={formData}
            onInputChange={handleInputChange}
          />
        );
      case 2:
        return (
          <FinancialGoalsStep
            formData={formData}
            onInputChange={handleInputChange}
            onArrayInputChange={handleArrayInputChange}
          />
        );
      case 3:
        return (
          <PreferencesStep
            formData={formData}
            onInputChange={handleInputChange}
            onArrayInputChange={handleArrayInputChange}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome to Your Financial Journey
          </h1>
          <p className="text-lg text-gray-600">
            Let's set up your personalized finance assistant
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">
              Step {currentStep} of {totalSteps}
            </span>
            <span className="text-sm text-gray-500">
              {Math.round((currentStep / totalSteps) * 100)}% Complete
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / totalSteps) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-sm p-8 mb-8">
          {renderStepContent()}
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <Button
            onClick={prevStep}
            variant="outline"
            disabled={currentStep === 1}
            className="min-w-24"
          >
            Previous
          </Button>

          {currentStep === totalSteps ? (
            <Button
              onClick={handleComplete}
              isLoading={isLoading}
              className="min-w-24"
            >
              Complete Setup
            </Button>
          ) : (
            <Button onClick={nextStep} className="min-w-24">
              Next
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

// Personal Info Step Component
const PersonalInfoStep = ({ formData, onInputChange }) => {
  const { personalInfo } = formData;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Tell us about yourself
        </h2>
        <p className="text-gray-600 mb-6">
          This information helps us provide personalized financial advice.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Age"
          type="number"
          value={personalInfo.age}
          onChange={(e) => onInputChange("personalInfo", "age", e.target.value)}
          placeholder="Enter your age"
        />

        <Input
          label="Occupation"
          type="text"
          value={personalInfo.occupation}
          onChange={(e) =>
            onInputChange("personalInfo", "occupation", e.target.value)
          }
          placeholder="Your job title"
        />
      </div>

      <Input
        label="Annual Income (USD)"
        type="number"
        value={personalInfo.annualIncome}
        onChange={(e) =>
          onInputChange("personalInfo", "annualIncome", e.target.value)
        }
        placeholder="Enter your annual income"
      />

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Financial Experience Level
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {[
            {
              value: "beginner",
              label: "Beginner",
              desc: "New to personal finance",
            },
            {
              value: "intermediate",
              label: "Intermediate",
              desc: "Some experience managing money",
            },
            {
              value: "advanced",
              label: "Advanced",
              desc: "Experienced with investments",
            },
          ].map((level) => (
            <button
              key={level.value}
              onClick={() =>
                onInputChange(
                  "personalInfo",
                  "financialExperience",
                  level.value
                )
              }
              className={cn(
                "p-3 border rounded-lg text-left transition-colors",
                personalInfo.financialExperience === level.value
                  ? "border-blue-500 bg-blue-50 text-blue-900"
                  : "border-gray-300 hover:border-gray-400"
              )}
            >
              <div className="font-medium">{level.label}</div>
              <div className="text-sm text-gray-600">{level.desc}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

// Financial Goals Step Component
const FinancialGoalsStep = ({
  formData,
  onInputChange,
  onArrayInputChange,
}) => {
  const { financialGoals } = formData;

  const goalOptions = [
    "Emergency Fund",
    "Debt Payoff",
    "Home Purchase",
    "Retirement Savings",
    "Investment Growth",
    "Education Fund",
    "Travel Fund",
    "Business Investment",
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          What are your financial goals?
        </h2>
        <p className="text-gray-600 mb-6">
          Setting clear goals helps us create a personalized plan for you.
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Primary Financial Goal
        </label>
        <select
          value={financialGoals.primaryGoal}
          onChange={(e) =>
            onInputChange("financialGoals", "primaryGoal", e.target.value)
          }
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Select your primary goal</option>
          {goalOptions.map((goal) => (
            <option key={goal} value={goal}>
              {goal}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Amount (USD)
          </label>
          <input
            type="number"
            value={financialGoals.targetAmount}
            onChange={(e) =>
              onInputChange("financialGoals", "targetAmount", e.target.value)
            }
            placeholder="e.g., 10000"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Timeframe
          </label>
          <select
            value={financialGoals.timeframe}
            onChange={(e) =>
              onInputChange("financialGoals", "timeframe", e.target.value)
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select timeframe</option>
            <option value="6months">6 months</option>
            <option value="1year">1 year</option>
            <option value="2years">2 years</option>
            <option value="5years">5 years</option>
            <option value="10years">10+ years</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Secondary Goals (Optional)
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {goalOptions
            .filter((goal) => goal !== financialGoals.primaryGoal)
            .map((goal) => (
              <label key={goal} className="flex items-center">
                <input
                  type="checkbox"
                  checked={financialGoals.secondaryGoals.includes(goal)}
                  onChange={(e) =>
                    onArrayInputChange(
                      "financialGoals",
                      "secondaryGoals",
                      goal,
                      e.target.checked
                    )
                  }
                  className="mr-2 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm">{goal}</span>
              </label>
            ))}
        </div>
      </div>
    </div>
  );
};

// Preferences Step Component
const PreferencesStep = ({ formData, onInputChange, onArrayInputChange }) => {
  const { preferences } = formData;

  const investmentOptions = [
    "Stocks",
    "Bonds",
    "Real Estate",
    "Cryptocurrency",
    "Mutual Funds",
    "ETFs",
    "Commodities",
    "CDs",
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Customize your experience
        </h2>
        <p className="text-gray-600 mb-6">
          Help us tailor our recommendations to your preferences.
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Risk Tolerance
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {[
            {
              value: "conservative",
              label: "Conservative",
              desc: "Prefer stability over growth",
            },
            {
              value: "moderate",
              label: "Moderate",
              desc: "Balanced approach to risk and reward",
            },
            {
              value: "aggressive",
              label: "Aggressive",
              desc: "Willing to take risks for higher returns",
            },
          ].map((risk) => (
            <button
              key={risk.value}
              onClick={() =>
                onInputChange("preferences", "riskTolerance", risk.value)
              }
              className={cn(
                "p-3 border rounded-lg text-left transition-colors",
                preferences.riskTolerance === risk.value
                  ? "border-blue-500 bg-blue-50 text-blue-900"
                  : "border-gray-300 hover:border-gray-400"
              )}
            >
              <div className="font-medium">{risk.label}</div>
              <div className="text-sm text-gray-600">{risk.desc}</div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Investment Interests (Select all that apply)
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {investmentOptions.map((investment) => (
            <label key={investment} className="flex items-center">
              <input
                type="checkbox"
                checked={preferences.investmentInterests.includes(investment)}
                onChange={(e) =>
                  onArrayInputChange(
                    "preferences",
                    "investmentInterests",
                    investment,
                    e.target.checked
                  )
                }
                className="mr-2 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm">{investment}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Budgeting Style
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            {
              value: "simple",
              label: "Simple",
              desc: "Basic income and expense tracking",
            },
            {
              value: "detailed",
              label: "Detailed",
              desc: "Comprehensive category-based budgeting",
            },
          ].map((style) => (
            <button
              key={style.value}
              onClick={() =>
                onInputChange("preferences", "budgetingStyle", style.value)
              }
              className={cn(
                "p-3 border rounded-lg text-left transition-colors",
                preferences.budgetingStyle === style.value
                  ? "border-blue-500 bg-blue-50 text-blue-900"
                  : "border-gray-300 hover:border-gray-400"
              )}
            >
              <div className="font-medium">{style.label}</div>
              <div className="text-sm text-gray-600">{style.desc}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="notifications"
          checked={preferences.notifications}
          onChange={(e) =>
            onInputChange("preferences", "notifications", e.target.checked)
          }
          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
        />
        <label htmlFor="notifications" className="ml-2 text-sm text-gray-700">
          Send me helpful tips and notifications about my financial goals
        </label>
      </div>
    </div>
  );
};

export default OnboardingPage;
