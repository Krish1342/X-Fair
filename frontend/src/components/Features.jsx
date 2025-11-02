import React from "react";

const Features = () => {
  const features = [
    {
      title: "Transaction Analysis",
      description:
        "AI-powered analysis of spending patterns, categorization, and merchant insights with LangGraph workflow.",
      icon: (
        <svg
          className="w-8 h-8"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
      ),
      color: "bg-blue-500",
      tools: ["TransactionAnalyzerTool"],
    },
    {
      title: "Budget Management",
      description:
        "Smart budget tracking with overspending alerts and category-wise analysis for better financial control.",
      icon: (
        <svg
          className="w-8 h-8"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
          />
        </svg>
      ),
      color: "bg-green-500",
      tools: ["BudgetManagerTool"],
    },
    {
      title: "Investment Analysis",
      description:
        "Portfolio performance tracking, gains/losses analysis, and asset allocation insights.",
      icon: (
        <svg
          className="w-8 h-8"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
          />
        </svg>
      ),
      color: "bg-purple-500",
      tools: ["InvestmentAnalyzerTool"],
    },
    {
      title: "Goal Tracking",
      description:
        "Progress monitoring for financial goals with timeline analysis and recommendation engine.",
      icon: (
        <svg
          className="w-8 h-8"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
          />
        </svg>
      ),
      color: "bg-orange-500",
      tools: ["GoalTrackerTool"],
    },
    {
      title: "Financial Insights",
      description:
        "Comprehensive financial health scoring with trend analysis and personalized recommendations.",
      icon: (
        <svg
          className="w-8 h-8"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
      ),
      color: "bg-red-500",
      tools: ["FinancialInsightsTool"],
    },
    {
      title: "LangGraph AI Agent",
      description:
        "Advanced conversational AI powered by LangGraph workflow for intelligent financial assistance.",
      icon: (
        <svg
          className="w-8 h-8"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
      ),
      color: "bg-indigo-500",
      tools: ["IntentClassifierNode", "ResponseSynthesizerNode"],
    },
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Powerful Features for Modern Finance
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Our AI-powered platform provides everything you need to take control
            of your financial future
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="card hover:shadow-xl transition-shadow duration-300"
            >
              <div className="flex items-center mb-4">
                <div
                  className={`w-12 h-12 ${feature.color} rounded-lg flex items-center justify-center text-white mr-4`}
                >
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900">
                  {feature.title}
                </h3>
              </div>
              <p className="text-gray-600 leading-relaxed mb-3">
                {feature.description}
              </p>
              {feature.tools && (
                <div className="flex flex-wrap gap-1">
                  {feature.tools.map((tool, toolIndex) => (
                    <span
                      key={toolIndex}
                      className="inline-block bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full"
                    >
                      {tool}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Stats Section */}
        <div className="mt-20 bg-gray-50 rounded-2xl p-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-sky-600 mb-2">10K+</div>
              <div className="text-gray-600">Active Users</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-sky-600 mb-2">$2.5M+</div>
              <div className="text-gray-600">Money Managed</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-sky-600 mb-2">95%</div>
              <div className="text-gray-600">Accuracy Rate</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-sky-600 mb-2">24/7</div>
              <div className="text-gray-600">AI Support</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Features;
