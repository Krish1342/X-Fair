/**
 * Dashboard Component - Main user dashboard with financial overview
 */
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "@store/AppContext";
import {
  getDashboardAPI,
  listTransactionsAPI,
  listGoalsAPI,
  listBudgetsAPI,
  listRecurringAPI,
  deleteRecurringAPI,
  deleteTransactionAPI,
  deleteGoalAPI,
  deleteBudgetAPI,
  generateRecurringAPI,
} from "@api/finance";
import DataEntryModal from "@components/DataEntryModal";
import LoadingSpinner from "@ui/LoadingSpinner";
import Button from "@ui/Button";
import { cn } from "@utils";

const Dashboard = () => {
  const { state, dispatch, setToast } = useApp();
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState("30d");
  const [transactions, setTransactions] = useState([]);
  const [goalsList, setGoalsList] = useState([]);
  const [budgets, setBudgets] = useState([]);
  const [recurring, setRecurring] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalType, setModalType] = useState("transaction");
  const [modalMode, setModalMode] = useState("create");
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    loadDashboardData();
    if (state.user?.id) {
      loadUserLists(state.user.id);
    }
  }, [selectedTimeframe, state.user?.id]);

  // Listen for global data update events (e.g., from AIPage or other components)
  useEffect(() => {
    const handler = () => {
      if (state.user?.id) {
        loadUserLists(state.user.id);
        loadDashboardData(true); // silent refresh for top metrics/insights
      }
    };
    window.addEventListener("finance:data-updated", handler);
    return () => window.removeEventListener("finance:data-updated", handler);
  }, [state.user?.id]);

  const loadDashboardData = async (silent = false) => {
    try {
      if (!silent) setIsLoading(true);
      const params = { timeframe: selectedTimeframe };
      const data = state.user?.id
        ? await getDashboardAPI({ ...params, user_id: state.user.id })
        : await getDashboardAPI(params);
      setDashboardData(data);
      setError(null);
    } catch (err) {
      console.error("Dashboard loading error:", err);
      if (!silent) {
        // Use fallback demo data for better UX only on full load
        setDashboardData({
          accountBalance: 15750.5,
          monthlyIncome: 5200.0,
          monthlyExpenses: 3450.0,
          savingsRate: 33.7,
          budgetCategories: [
            { name: "Housing", spent: 1200, budget: 1300, percentage: 92 },
            { name: "Food", spent: 450, budget: 500, percentage: 90 },
            { name: "Transportation", spent: 280, budget: 350, percentage: 80 },
            { name: "Entertainment", spent: 180, budget: 200, percentage: 90 },
          ],
          recentTransactions: [
            {
              id: 1,
              description: "Grocery Store",
              amount: -85.43,
              date: "2025-10-12",
              category: "Food",
            },
            {
              id: 2,
              description: "Salary Deposit",
              amount: 2600.0,
              date: "2025-10-11",
              category: "Income",
            },
            {
              id: 3,
              description: "Gas Station",
              amount: -42.18,
              date: "2025-10-10",
              category: "Transportation",
            },
          ],
          goals: [
            {
              name: "Emergency Fund",
              current: 8500,
              target: 15000,
              percentage: 57,
            },
            { name: "Vacation", current: 2100, target: 3500, percentage: 60 },
            { name: "New Car", current: 5200, target: 20000, percentage: 26 },
          ],
          insights: [
            "Your spending on dining out increased by 15% this month",
            "You're on track to meet your emergency fund goal by March 2026",
            "Consider increasing your investment contributions",
          ],
        });
        setError(null);
      }
    } finally {
      if (!silent) setIsLoading(false);
    }
  };

  const loadUserLists = async (userId) => {
    try {
      const [tx, gl, bd, rc] = await Promise.all([
        listTransactionsAPI(userId),
        listGoalsAPI(userId),
        listBudgetsAPI(userId),
        listRecurringAPI(userId),
      ]);
      setTransactions(tx || []);
      setGoalsList(gl || []);
      setBudgets(bd || []);
      setRecurring(rc || []);
    } catch (e) {
      console.error("Failed loading user lists", e);
    }
  };

  const handleWorkflowStageChange = (newStage) => {
    dispatch({
      type: "SET_WORKFLOW_STAGE",
      payload: newStage,
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-96 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-8 bg-white rounded-lg shadow-md">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.314 18.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Failed to load dashboard data
          </h3>
          <p className="text-gray-600 mb-4">
            We're having trouble connecting to the server. Please check your
            connection and try again.
          </p>
          <Button onClick={loadDashboardData} variant="primary">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  const {
    accountBalance = 0,
    monthlyIncome = 0,
    monthlyExpenses = 0,
    savingsRate = 0,
    budgetCategories = [],
    recentTransactions = [],
    goals = [],
    insights = [],
  } = dashboardData || {};

  const netIncome = monthlyIncome - monthlyExpenses;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        
      </div>
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Financial Dashboard
          </h1>
        </div>

        <div className="flex space-x-2">
          {["7d", "30d", "90d", "1y"].map((timeframe) => (
            <button
              key={timeframe}
              onClick={() => setSelectedTimeframe(timeframe)}
              className={cn(
                "px-3 py-1 rounded-md text-sm font-medium transition-colors",
                selectedTimeframe === timeframe
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              )}
            >
              {timeframe}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Account Balance"
          value={`$${accountBalance.toLocaleString()}`}
          change={accountBalance > 0 ? "+5.2%" : "0%"}
          isPositive={accountBalance > 0}
          icon="💰"
        />
        <MetricCard
          title="Monthly Income"
          value={`$${monthlyIncome.toLocaleString()}`}
          change="+2.1%"
          isPositive={true}
          icon="📈"
        />
        <MetricCard
          title="Monthly Expenses"
          value={`$${monthlyExpenses.toLocaleString()}`}
          change="-1.3%"
          isPositive={true}
          icon="💳"
        />
        <MetricCard
          title="Savings Rate"
          value={`${savingsRate}%`}
          change="+0.8%"
          isPositive={true}
          icon="🎯"
        />
      </div>

      {/* Workflow Progress moved to AI page */}

      {/* Main Content */}
      <div className="grid grid-cols-1 gap-6">
        {/* Budget Overview (only when not logged in) */}
        {!state.user && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Budget Categories</h2>
            </div>
            <div className="space-y-3">
              {budgetCategories.map((category, index) => (
                <BudgetCategoryItem key={index} category={category} />
              ))}
              {budgetCategories.length === 0 && (
                <p className="text-gray-500 text-center py-4">
                  No budget categories set up yet
                </p>
              )}
            </div>
            <div>
              
            </div>
          </div>
        )}

        {/* Recent Transactions - full width */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Recent Transactions</h2>
            {state.user && (
              <div className="flex gap-2">
                <button
                  className="text-sm px-3 py-1 rounded-md bg-blue-600 text-white"
                  onClick={() => {
                    setModalType("transaction");
                    setModalMode("create");
                    setSelectedItem(null);
                    setModalOpen(true);
                  }}
                >
                  Add Transaction
                </button>
                <button
                  className="text-sm px-3 py-1 rounded-md bg-purple-600 text-white"
                  onClick={() => {
                    setModalType("recurring");
                    setModalMode("create");
                    setSelectedItem(null);
                    setModalOpen(true);
                  }}
                >
                  Add Recurring
                </button>
              </div>
            )}
          </div>
          <div className="space-y-3">
            {(state.user
              ? [...(transactions || [])]
                  .sort((a, b) => new Date(b.date) - new Date(a.date))
                  .slice(0, 5)
              : (recentTransactions || []).slice(0, 5)
            ).map((transaction, index) => (
              <TransactionItem
                key={index}
                transaction={transaction}
                onEdit={() => {
                  setModalType("transaction");
                  setModalMode("edit");
                  setSelectedItem(transaction);
                  setModalOpen(true);
                }}
                onDelete={async () => {
                  try {
                    if (!state.user?.id || !transaction?.id) return;
                    await deleteTransactionAPI(state.user.id, transaction.id);
                    await loadUserLists(state.user.id);
                    await loadDashboardData(true);
                    window.dispatchEvent(
                      new CustomEvent("finance:data-updated", {
                        detail: { entity: "transaction", action: "delete" },
                      })
                    );
                  } catch (e) {
                    console.error("Delete transaction failed", e);
                  }
                }}
                canManage={!!state.user}
              />
            ))}
            {state.user && (transactions?.length || 0) > 5 && (
              <div className="pt-1">
                <button
                  className="text-sm text-blue-600 hover:underline inline-flex items-center"
                  onClick={() => navigate("/transactions")}
                >
                  See all
                  <span className="ml-1" aria-hidden>
                    →
                  </span>
                </button>
              </div>
            )}
            {state.user && transactions.length === 0 && (
              <p className="text-gray-500 text-center py-4">
                No recent transactions yet. Add your first one.
              </p>
            )}
            {!state.user && recentTransactions.length === 0 && (
              <p className="text-gray-500 text-center py-4">
                No recent transactions
              </p>
            )}
          </div>
        </div>

        {/* Goals + Recurring side-by-side */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Goals */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Financial Goals</h2>
              {state.user && (
                <button
                  className="text-sm px-3 py-1 rounded-md bg-blue-600 text-white"
                  onClick={() => {
                    setModalType("goal");
                    setModalMode("create");
                    setSelectedItem(null);
                    setModalOpen(true);
                  }}
                >
                  Add Goal
                </button>
              )}
            </div>
            <div className="space-y-3">
              {(state.user ? goalsList : goals).map((goal, index) => (
                <GoalItem
                  key={index}
                  goal={goal}
                  canManage={!!state.user}
                  onEdit={() => {
                    setModalType("goal");
                    setModalMode("edit");
                    setSelectedItem(goal);
                    setModalOpen(true);
                  }}
                  onDelete={async () => {
                    try {
                      if (!state.user?.id || !goal?.id) return;
                      await deleteGoalAPI(state.user.id, goal.id);
                      await loadUserLists(state.user.id);
                      await loadDashboardData(true);
                      window.dispatchEvent(
                        new CustomEvent("finance:data-updated", {
                          detail: { entity: "goal", action: "delete" },
                        })
                      );
                    } catch (e) {
                      console.error("Delete goal failed", e);
                    }
                  }}
                />
              ))}
              {state.user && goalsList.length === 0 && (
                <p className="text-gray-500 text-center py-4">
                  No goals set yet. Create your first goal.
                </p>
              )}
              {!state.user && goals.length === 0 && (
                <p className="text-gray-500 text-center py-4">
                  No goals set yet
                </p>
              )}
            </div>
          </div>

          {/* Recurring */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Recurring Transactions</h2>
              {state.user && (
                <div className="flex gap-2">
                  <button
                    className="text-sm px-3 py-1 rounded-md bg-purple-600 text-white"
                    onClick={() => {
                      setModalType("recurring");
                      setModalMode("create");
                      setSelectedItem(null);
                      setModalOpen(true);
                    }}
                  >
                    New Recurring
                  </button>
                  <button
                    className="text-sm px-3 py-1 rounded-md bg-gray-800 text-white"
                    title="Create transactions for any recurring items due up to today"
                    onClick={async () => {
                      try {
                        if (!state.user?.id) return;
                        const today = new Date().toISOString().split("T")[0];
                        const res = await generateRecurringAPI(
                          state.user.id,
                          today
                        );
                        await loadUserLists(state.user.id);
                        await loadDashboardData(true);
                        window.dispatchEvent(
                          new CustomEvent("finance:data-updated", {
                            detail: { entity: "recurring", action: "generate" },
                          })
                        );
                        if (res && typeof res.count === "number") {
                          const msg =
                            res.count > 0
                              ? `${res.count} recurring transaction${
                                  res.count === 1 ? "" : "s"
                                } generated`
                              : "No recurring transactions were due";
                          setToast({
                            message: msg,
                            type: res.count > 0 ? "success" : "info",
                          });
                        }
                      } catch (e) {
                        console.error("Generate recurring failed", e);
                        setToast({
                          message: "Failed to generate transactions",
                          type: "error",
                        });
                      }
                    }}
                  >
                    Generate due transactions
                  </button>
                </div>
              )}
            </div>
            <div className="space-y-3">
              {recurring.map((r) => (
                <div key={r.id} className="p-3 bg-gray-50 rounded-lg border">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium">{r.description}</p>
                      <p className="text-sm text-gray-600">
                        {r.category} • ${r.amount} • {r.frequency}
                        {r.interval && r.interval > 1
                          ? ` x${r.interval}`
                          : ""}{" "}
                        • next: {r.next_date}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        className="text-xs px-2 py-1 rounded border"
                        onClick={() => {
                          setModalType("recurring");
                          setModalMode("edit");
                          setSelectedItem(r);
                          setModalOpen(true);
                        }}
                      >
                        Edit
                      </button>
                      <button
                        className="text-xs px-2 py-1 rounded border text-red-600"
                        onClick={async () => {
                          try {
                            if (!state.user?.id) return;
                            await deleteRecurringAPI(state.user.id, r.id);
                            await loadUserLists(state.user.id);
                            await loadDashboardData(true);
                            window.dispatchEvent(
                              new CustomEvent("finance:data-updated", {
                                detail: {
                                  entity: "recurring",
                                  action: "delete",
                                },
                              })
                            );
                          } catch (e) {
                            console.error("Delete recurring failed", e);
                          }
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
              {recurring.length === 0 && (
                <p className="text-gray-500 text-center py-4">
                  No recurring transactions
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Budgets list (user-specific) */}
      {state.user && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Budgets</h2>
            <button
              className="text-sm px-3 py-1 rounded-md bg-blue-600 text-white"
              onClick={() => {
                setModalType("budget");
                setModalMode("create");
                setSelectedItem(null);
                setModalOpen(true);
              }}
            >
              Add Budget
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {budgets.map((b, i) => (
              <div key={i} className="p-4 rounded-md border">
                <div className="flex justify-between">
                  <span className="font-medium">{b.category}</span>
                  <span className="text-gray-600">{b.month}</span>
                </div>
                <p className="text-sm text-gray-700 mt-1">
                  Budgeted: ${b.budgeted}
                </p>
                <div className="flex gap-2 mt-2">
                  <button
                    className="text-xs px-2 py-1 rounded border"
                    onClick={() => {
                      setModalType("budget");
                      setModalMode("edit");
                      setSelectedItem(b);
                      setModalOpen(true);
                    }}
                  >
                    Edit
                  </button>
                  <button
                    className="text-xs px-2 py-1 rounded border text-red-600"
                    onClick={async () => {
                      try {
                        if (!state.user?.id || !b?.id) return;
                        await deleteBudgetAPI(state.user.id, b.id);
                        await loadUserLists(state.user.id);
                        await loadDashboardData(true);
                        window.dispatchEvent(
                          new CustomEvent("finance:data-updated", {
                            detail: { entity: "budget", action: "delete" },
                          })
                        );
                      } catch (e) {
                        console.error("Delete budget failed", e);
                      }
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
            {budgets.length === 0 && (
              <p className="text-gray-500">No budgets yet.</p>
            )}
          </div>
        </div>
      )}

      <DataEntryModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onDataAdded={() => {
          if (state.user?.id) {
            loadUserLists(state.user.id);
            loadDashboardData(true);
          }
        }}
        type={modalType}
        userId={state.user?.id}
        mode={modalMode}
        initialItem={selectedItem}
      />
    </div>
  );
};

// Metric Card Component
const MetricCard = ({ title, value, change, isPositive, icon }) => (
  <div className="bg-white rounded-lg shadow p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
      <div className="text-2xl">{icon}</div>
    </div>
    <div className="mt-2">
      <span
        className={cn(
          "inline-flex items-center text-sm font-medium",
          isPositive ? "text-green-600" : "text-red-600"
        )}
      >
        {change}
        <span className="ml-1">vs last period</span>
      </span>
    </div>
  </div>
);

// Workflow Progress Component
const WorkflowProgress = ({ currentStage, onStageChange }) => {
  const stages = ["Started", "MVP", "Intermediate", "Advanced"];
  const currentIndex = stages.indexOf(currentStage);

  return (
    <div className="flex items-center space-x-4">
      {stages.map((stage, index) => (
        <div key={stage} className="flex items-center">
          <button
            onClick={() => onStageChange(stage)}
            className={cn(
              "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium",
              index <= currentIndex
                ? "bg-blue-600 text-white"
                : "bg-gray-200 text-gray-600"
            )}
          >
            {index + 1}
          </button>
          <span
            className={cn(
              "ml-2 text-sm font-medium",
              index <= currentIndex ? "text-blue-600" : "text-gray-500"
            )}
          >
            {stage}
          </span>
          {index < stages.length - 1 && (
            <div
              className={cn(
                "w-8 h-0.5 mx-4",
                index < currentIndex ? "bg-blue-600" : "bg-gray-200"
              )}
            />
          )}
        </div>
      ))}
    </div>
  );
};

// Budget Category Item Component
const BudgetCategoryItem = ({ category }) => {
  const { name, budgeted, spent, percentage } = category;
  const isOverBudget = spent > budgeted;

  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <div className="flex-1">
        <div className="flex justify-between items-center mb-1">
          <span className="font-medium">{name}</span>
          <span className="text-sm text-gray-600">
            ${spent} / ${budgeted}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={cn(
              "h-2 rounded-full",
              isOverBudget ? "bg-red-500" : "bg-green-500"
            )}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
};

// Transaction Item Component
const TransactionItem = ({ transaction, onEdit, onDelete, canManage }) => {
  const { description, amount, date, category } = transaction;
  const isExpense = amount < 0;

  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <div className="flex-1">
        <p className="font-medium">{description}</p>
        <p className="text-sm text-gray-600">
          {category} • {date}
        </p>
      </div>
      <span
        className={cn(
          "font-medium",
          isExpense ? "text-red-600" : "text-green-600"
        )}
      >
        {isExpense ? "-" : "+"}${Math.abs(amount)}
      </span>
      {canManage && (
        <div className="flex gap-2 ml-3">
          <button className="text-xs px-2 py-1 rounded border" onClick={onEdit}>
            Edit
          </button>
          <button
            className="text-xs px-2 py-1 rounded border text-red-600"
            onClick={onDelete}
          >
            Delete
          </button>
        </div>
      )}
    </div>
  );
};

// Goal Item Component
const GoalItem = ({ goal, onEdit, onDelete, canManage }) => {
  const { name, target, current, deadline } = goal;
  const percentage = (current / target) * 100;

  return (
    <div className="p-3 bg-gray-50 rounded-lg">
      <div className="flex justify-between items-center mb-2">
        <span className="font-medium">{name}</span>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">{deadline}</span>
          {canManage && (
            <>
              <button
                className="text-xs px-2 py-1 rounded border"
                onClick={onEdit}
              >
                Edit
              </button>
              <button
                className="text-xs px-2 py-1 rounded border text-red-600"
                onClick={onDelete}
              >
                Delete
              </button>
            </>
          )}
        </div>
      </div>
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm">
          ${current} / ${target}
        </span>
        <span className="text-sm font-medium">{percentage.toFixed(1)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="h-2 bg-blue-500 rounded-full"
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  );
};

// Insight Item Component
const InsightItem = ({ insight }) => {
  const { title, description, type, priority } = insight;

  const typeColors = {
    tip: "bg-blue-50 border-blue-200 text-blue-800",
    warning: "bg-yellow-50 border-yellow-200 text-yellow-800",
    success: "bg-green-50 border-green-200 text-green-800",
  };

  return (
    <div
      className={cn(
        "p-3 rounded-lg border",
        typeColors[type] || typeColors.tip
      )}
    >
      <h4 className="font-medium mb-1">{title}</h4>
      <p className="text-sm opacity-90">{description}</p>
    </div>
  );
};

export default Dashboard;
