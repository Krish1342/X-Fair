import React, { useEffect, useState } from "react";
import { useApp } from "@store/AppContext";
import { listTransactionsAPI, deleteTransactionAPI } from "@api/finance";
import LoadingSpinner from "@components/ui/LoadingSpinner";
import Button from "@components/ui/Button";

const TransactionsPage = () => {
  const { state } = useApp();
  const userId = state.user?.id;
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    try {
      setIsLoading(true);
      const data = await listTransactionsAPI(userId);
      // Sort by date desc
      const sorted = [...(data || [])].sort(
        (a, b) => new Date(b.date) - new Date(a.date)
      );
      setTransactions(sorted);
      setError(null);
    } catch (e) {
      console.error("Failed to load transactions", e);
      setError("Failed to load transactions");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (userId) {
      load();
    }
  }, [userId]);

  if (!userId) {
    return (
      <div className="min-h-96 flex items-center justify-center">
        <p className="text-gray-600">
          Please log in to view your transactions.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-96 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-96 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-700 mb-3">{error}</p>
          <Button onClick={load} variant="primary">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">All Transactions</h1>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                Date
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                Description
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                Category
              </th>
              <th className="px-4 py-3 text-right text-sm font-medium text-gray-600">
                Amount
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {transactions.map((t) => {
              const isExpense = t.amount < 0;
              return (
                <tr key={t.id}>
                  <td className="px-4 py-3 text-sm text-gray-700">{t.date}</td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {t.description}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {t.category || "-"}
                  </td>
                  <td
                    className={
                      "px-4 py-3 text-sm font-medium text-right " +
                      (isExpense ? "text-red-600" : "text-green-600")
                    }
                  >
                    {isExpense ? "-" : "+"}${Math.abs(t.amount)}
                  </td>
                </tr>
              );
            })}
            {transactions.length === 0 && (
              <tr>
                <td colSpan="4" className="px-4 py-6 text-center text-gray-500">
                  No transactions yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TransactionsPage;
