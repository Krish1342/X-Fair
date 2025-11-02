import React, { useState, useEffect } from "react";

const AIInsights = ({ transactions = [], budget = null }) => {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    generateInsights();
  }, [transactions, budget]);

  const generateInsights = async () => {
    if (!transactions || transactions.length === 0) {
      setInsights([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Generate AI-powered insights based on spending patterns
      const generatedInsights = analyzeSpendingPatterns(transactions, budget);
      setInsights(generatedInsights);
    } catch (err) {
      console.error("Error generating insights:", err);
      setError("Failed to generate insights");
    } finally {
      setLoading(false);
    }
  };

  const analyzeSpendingPatterns = (transactions, budget) => {
    const insights = [];

    // Calculate spending by category
    const categorySpending = {};
    const totalSpent = transactions
      .filter((t) => t.amount < 0)
      .reduce((sum, t) => {
        const category = t.category || "Other";
        categorySpending[category] =
          (categorySpending[category] || 0) + Math.abs(t.amount);
        return sum + Math.abs(t.amount);
      }, 0);

    // Top spending category insight
    const topCategory = Object.entries(categorySpending).sort(
      ([, a], [, b]) => b - a
    )[0];

    if (topCategory) {
      const [category, amount] = topCategory;
      const percentage = ((amount / totalSpent) * 100).toFixed(1);
      insights.push({
        id: 1,
        type: "spending",
        icon: "📊",
        title: "Top Spending Category",
        message: `Your highest spending is in ${category}, accounting for ${percentage}% of your total expenses ($${amount.toFixed(
          2
        )}).`,
        severity: percentage > 40 ? "warning" : "info",
      });
    }

    // Frequent merchant insight
    const merchantCount = {};
    transactions.forEach((t) => {
      if (t.merchant && t.amount < 0) {
        merchantCount[t.merchant] = (merchantCount[t.merchant] || 0) + 1;
      }
    });

    const frequentMerchant = Object.entries(merchantCount).sort(
      ([, a], [, b]) => b - a
    )[0];

    if (frequentMerchant && frequentMerchant[1] > 1) {
      const [merchant, count] = frequentMerchant;
      insights.push({
        id: 2,
        type: "behavior",
        icon: "🏪",
        title: "Frequent Merchant",
        message: `You've made ${count} transactions at ${merchant}. Consider reviewing if this aligns with your spending goals.`,
        severity: "info",
      });
    }

    // Budget analysis if available
    if (budget && budget.monthly_budgets) {
      const currentMonth = new Date().toISOString().slice(0, 7);
      const monthlyBudget = budget.monthly_budgets[currentMonth];

      if (monthlyBudget && monthlyBudget.categories) {
        Object.entries(monthlyBudget.categories).forEach(([category, data]) => {
          if (data.percentage_used > 80) {
            insights.push({
              id: insights.length + 3,
              type: "budget",
              icon: "⚠️",
              title: "Budget Alert",
              message: `You've used ${data.percentage_used.toFixed(
                1
              )}% of your ${category} budget. Consider reviewing your spending in this category.`,
              severity: data.percentage_used > 100 ? "error" : "warning",
            });
          }
        });
      }
    }

    // Recent spending trend
    const last3Days = transactions.filter((t) => {
      const transDate = new Date(t.date);
      const threeDaysAgo = new Date();
      threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);
      return transDate >= threeDaysAgo && t.amount < 0;
    });

    if (last3Days.length > 0) {
      const recentSpent = last3Days.reduce(
        (sum, t) => sum + Math.abs(t.amount),
        0
      );
      const dailyAverage = recentSpent / 3;

      insights.push({
        id: insights.length + 4,
        type: "trend",
        icon: "📈",
        title: "Recent Spending Trend",
        message: `You've spent $${recentSpent.toFixed(
          2
        )} in the last 3 days (avg $${dailyAverage.toFixed(2)}/day).`,
        severity: dailyAverage > 50 ? "warning" : "info",
      });
    }

    // Add positive insights if spending is low
    if (totalSpent < 200) {
      insights.push({
        id: insights.length + 5,
        type: "positive",
        icon: "✅",
        title: "Good Spending Control",
        message: `Great job! Your recent spending of $${totalSpent.toFixed(
          2
        )} shows good financial discipline.`,
        severity: "success",
      });
    }

    return insights;
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "error":
        return "bg-red-50 border-red-200 text-red-800";
      case "warning":
        return "bg-yellow-50 border-yellow-200 text-yellow-800";
      case "success":
        return "bg-green-50 border-green-200 text-green-800";
      default:
        return "bg-blue-50 border-blue-200 text-blue-800";
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600"></div>
          <span className="ml-2 text-gray-600">Generating AI insights...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center py-8">
          <div className="text-red-500 text-4xl mb-4">⚠️</div>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (insights.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <span className="text-2xl mr-2">🤖</span>
          AI Financial Insights
        </h3>
        <div className="text-center py-8">
          <div className="text-gray-400 text-4xl mb-4">📊</div>
          <p className="text-gray-600">
            Add some transactions to get personalized AI insights about your
            spending patterns.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <span className="text-2xl mr-2">🤖</span>
        AI Financial Insights
        <span className="ml-2 bg-sky-100 text-sky-800 text-xs px-2 py-1 rounded-full">
          {insights.length} insight{insights.length !== 1 ? "s" : ""}
        </span>
      </h3>

      <div className="space-y-4">
        {insights.map((insight) => (
          <div
            key={insight.id}
            className={`border rounded-lg p-4 ${getSeverityColor(
              insight.severity
            )}`}
          >
            <div className="flex items-start space-x-3">
              <span className="text-2xl">{insight.icon}</span>
              <div className="flex-1">
                <h4 className="font-medium text-sm mb-1">{insight.title}</h4>
                <p className="text-sm opacity-90">{insight.message}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          💡 Insights are generated based on your recent spending patterns and
          budget data
        </p>
      </div>
    </div>
  );
};

export default AIInsights;
