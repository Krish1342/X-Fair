import { useState, useEffect } from "react";
import { useApp } from "@store/AppContext";
import Button from "@components/ui/Button";
import {
  getStocks,
  getMutualFunds,
  getPortfolioSummary,
  refreshAllPrices,
  createStock,
  createMutualFund,
  deleteStock,
  deleteMutualFund,
} from "@api/portfolio";
import {
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Plus,
  Trash2,
  DollarSign,
  PieChart,
} from "lucide-react";

export default function PortfolioPage() {
  const { state, setToast } = useApp();
  const userId = state.user?.id;

  const [stocks, setStocks] = useState([]);
  const [mutualFunds, setMutualFunds] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [showAddStock, setShowAddStock] = useState(false);
  const [showAddMF, setShowAddMF] = useState(false);

  useEffect(() => {
    if (userId) {
      loadPortfolioData();
    }
  }, [userId]);

  const loadPortfolioData = async () => {
    try {
      setLoading(true);
      const [stocksRes, mfRes, summaryRes] = await Promise.all([
        getStocks(userId),
        getMutualFunds(userId),
        getPortfolioSummary(userId),
      ]);

      if (stocksRes.success) setStocks(stocksRes.stocks || []);
      if (mfRes.success) setMutualFunds(mfRes.mutual_funds || []);
      if (summaryRes.success) setSummary(summaryRes.summary);
    } catch (error) {
      console.error("Error loading portfolio:", error);
      setToast({ message: "Failed to load portfolio data", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshPrices = async () => {
    try {
      setRefreshing(true);
      const response = await refreshAllPrices(userId);
      if (response.success) {
        setToast({
          message: `Updated ${response.updated} stock prices`,
          type: "success",
        });
        await loadPortfolioData();
      }
    } catch (error) {
      setToast({ message: "Failed to refresh prices", type: "error" });
    } finally {
      setRefreshing(false);
    }
  };

  const handleDeleteStock = async (stockId) => {
    if (!confirm("Are you sure you want to delete this stock?")) return;
    try {
      await deleteStock(userId, stockId);
      setToast({ message: "Stock deleted successfully", type: "success" });
      await loadPortfolioData();
    } catch (error) {
      setToast({ message: "Failed to delete stock", type: "error" });
    }
  };

  const handleDeleteMF = async (mfId) => {
    if (!confirm("Are you sure you want to delete this mutual fund?")) return;
    try {
      await deleteMutualFund(userId, mfId);
      setToast({
        message: "Mutual fund deleted successfully",
        type: "success",
      });
      await loadPortfolioData();
    } catch (error) {
      setToast({ message: "Failed to delete mutual fund", type: "error" });
    }
  };

  const formatCurrency = (amount, currency = "USD") => {
    const symbol = currency === "INR" ? "₹" : "$";
    return `${symbol}${Math.abs(amount).toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatPercent = (percent) => {
    const sign = percent >= 0 ? "+" : "";
    return `${sign}${percent.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading portfolio...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Investment Portfolio
            </h1>
            <p className="text-gray-600 mt-1">
              Track your stocks and mutual funds
            </p>
          </div>
          <Button
            onClick={handleRefreshPrices}
            disabled={refreshing}
            className="flex items-center gap-2"
          >
            <RefreshCw
              className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`}
            />
            {refreshing ? "Refreshing..." : "Refresh Prices"}
          </Button>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">Total Investment</p>
                <DollarSign className="w-5 h-5 text-gray-400" />
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(summary.total_investment, "INR")}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">Current Value</p>
                <PieChart className="w-5 h-5 text-gray-400" />
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(summary.current_value, "INR")}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">Total P&L</p>
                {summary.profit_loss >= 0 ? (
                  <TrendingUp className="w-5 h-5 text-green-500" />
                ) : (
                  <TrendingDown className="w-5 h-5 text-red-500" />
                )}
              </div>
              <p
                className={`text-2xl font-bold ${
                  summary.profit_loss >= 0 ? "text-green-600" : "text-red-600"
                }`}
              >
                {formatCurrency(summary.profit_loss, "INR")}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">Returns</p>
                {summary.profit_loss_percent >= 0 ? (
                  <TrendingUp className="w-5 h-5 text-green-500" />
                ) : (
                  <TrendingDown className="w-5 h-5 text-red-500" />
                )}
              </div>
              <p
                className={`text-2xl font-bold ${
                  summary.profit_loss_percent >= 0
                    ? "text-green-600"
                    : "text-red-600"
                }`}
              >
                {formatPercent(summary.profit_loss_percent)}
              </p>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
              {["overview", "stocks", "mutual-funds"].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`${
                    activeTab === tab
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm capitalize`}
                >
                  {tab.replace("-", " ")}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Content based on active tab */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Stocks Overview */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-900">Stocks</h2>
                <span className="text-sm text-gray-600">
                  {stocks.length} holdings
                </span>
              </div>
              {summary?.stocks && (
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Investment:</span>
                    <span className="font-medium">
                      {formatCurrency(summary.stocks.investment, "INR")}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Current Value:</span>
                    <span className="font-medium">
                      {formatCurrency(summary.stocks.current_value, "INR")}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">P&L:</span>
                    <span
                      className={`font-medium ${
                        summary.stocks.profit_loss >= 0
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      {formatCurrency(summary.stocks.profit_loss, "INR")}
                    </span>
                  </div>
                </div>
              )}
              <Button
                onClick={() => setActiveTab("stocks")}
                variant="outline"
                className="w-full mt-4"
              >
                View All Stocks
              </Button>
            </div>

            {/* Mutual Funds Overview */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  Mutual Funds
                </h2>
                <span className="text-sm text-gray-600">
                  {mutualFunds.length} holdings
                </span>
              </div>
              {summary?.mutual_funds && (
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Investment:</span>
                    <span className="font-medium">
                      {formatCurrency(summary.mutual_funds.investment, "INR")}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Current Value:</span>
                    <span className="font-medium">
                      {formatCurrency(
                        summary.mutual_funds.current_value,
                        "INR"
                      )}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">P&L:</span>
                    <span
                      className={`font-medium ${
                        summary.mutual_funds.profit_loss >= 0
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      {formatCurrency(summary.mutual_funds.profit_loss, "INR")}
                    </span>
                  </div>
                </div>
              )}
              <Button
                onClick={() => setActiveTab("mutual-funds")}
                variant="outline"
                className="w-full mt-4"
              >
                View All Mutual Funds
              </Button>
            </div>
          </div>
        )}

        {activeTab === "stocks" && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-gray-900">
                  Stock Holdings
                </h2>
                <Button
                  onClick={() => setShowAddStock(true)}
                  className="flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Add Stock
                </Button>
              </div>
            </div>

            {stocks.length === 0 ? (
              <div className="p-12 text-center">
                <p className="text-gray-500">No stocks in your portfolio</p>
                <Button onClick={() => setShowAddStock(true)} className="mt-4">
                  Add Your First Stock
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Symbol
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Name
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Qty
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Avg Price
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Current Price
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Investment
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Current Value
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        P&L
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {stocks.map((stock) => (
                      <tr key={stock.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-medium text-gray-900">
                            {stock.symbol}
                          </div>
                          <div className="text-xs text-gray-500">
                            {stock.exchange}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">
                            {stock.name}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {stock.quantity}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {formatCurrency(stock.avg_buy_price, stock.currency)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {stock.current_price
                            ? formatCurrency(
                                stock.current_price,
                                stock.currency
                              )
                            : "-"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {formatCurrency(
                            stock.total_investment,
                            stock.currency
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {formatCurrency(stock.current_value, stock.currency)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                          <div
                            className={`font-medium ${
                              stock.profit_loss >= 0
                                ? "text-green-600"
                                : "text-red-600"
                            }`}
                          >
                            {formatCurrency(stock.profit_loss, stock.currency)}
                          </div>
                          <div
                            className={`text-xs ${
                              stock.profit_loss_percent >= 0
                                ? "text-green-600"
                                : "text-red-600"
                            }`}
                          >
                            {formatPercent(stock.profit_loss_percent)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                          <button
                            onClick={() => handleDeleteStock(stock.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === "mutual-funds" && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-gray-900">
                  Mutual Fund Holdings
                </h2>
                <Button
                  onClick={() => setShowAddMF(true)}
                  className="flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Add Mutual Fund
                </Button>
              </div>
            </div>

            {mutualFunds.length === 0 ? (
              <div className="p-12 text-center">
                <p className="text-gray-500">
                  No mutual funds in your portfolio
                </p>
                <Button onClick={() => setShowAddMF(true)} className="mt-4">
                  Add Your First Mutual Fund
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Scheme Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Fund House
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Units
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Avg NAV
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Current NAV
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Investment
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Current Value
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        P&L
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {mutualFunds.map((mf) => (
                      <tr key={mf.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900">
                            {mf.scheme_name}
                          </div>
                          <div className="text-xs text-gray-500">
                            {mf.scheme_type}
                          </div>
                          {mf.sip_amount && (
                            <div className="text-xs text-blue-600 mt-1">
                              SIP: {formatCurrency(mf.sip_amount, "INR")}/month
                              on {mf.sip_date}th
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          {mf.fund_house}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {mf.units.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {formatCurrency(mf.avg_nav, "INR")}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {formatCurrency(mf.current_nav, "INR")}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {formatCurrency(mf.total_investment, "INR")}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {formatCurrency(mf.current_value, "INR")}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                          <div
                            className={`font-medium ${
                              mf.profit_loss >= 0
                                ? "text-green-600"
                                : "text-red-600"
                            }`}
                          >
                            {formatCurrency(mf.profit_loss, "INR")}
                          </div>
                          <div
                            className={`text-xs ${
                              mf.profit_loss_percent >= 0
                                ? "text-green-600"
                                : "text-red-600"
                            }`}
                          >
                            {formatPercent(mf.profit_loss_percent)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                          <button
                            onClick={() => handleDeleteMF(mf.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Add modals can be implemented here - keeping it simple for now */}
      {showAddStock && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Add Stock</h3>
            <p className="text-gray-600 mb-4">
              Use the API documentation or backend to add stocks
              programmatically.
            </p>
            <Button onClick={() => setShowAddStock(false)}>Close</Button>
          </div>
        </div>
      )}

      {showAddMF && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Add Mutual Fund</h3>
            <p className="text-gray-600 mb-4">
              Use the API documentation or backend to add mutual funds
              programmatically.
            </p>
            <Button onClick={() => setShowAddMF(false)}>Close</Button>
          </div>
        </div>
      )}
    </div>
  );
}
