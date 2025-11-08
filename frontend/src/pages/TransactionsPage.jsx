import React, { useEffect, useState } from "react";
import { useApp } from "@store/AppContext";
import { listTransactionsAPI, deleteTransactionAPI } from "@api/finance";
import LoadingSpinner from "@components/ui/LoadingSpinner";
import Button from "@components/ui/Button";
import BulkUpload from "@components/features/BulkUpload";
import UPIIntegration from "@components/features/UPIIntegration";

const TransactionsPage = () => {
  const { state } = useApp();
  const userId = state.user?.id;
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showBulkUpload, setShowBulkUpload] = useState(false);
  const [showUPIUpload, setShowUPIUpload] = useState(false);

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

  // Listen for data updates
  useEffect(() => {
    const handleUpdate = (event) => {
      if (event.detail?.entity === "transactions") {
        load();
      }
    };
    window.addEventListener("finance:data-updated", handleUpdate);
    return () =>
      window.removeEventListener("finance:data-updated", handleUpdate);
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
        <div className="flex gap-3">
          <Button
            onClick={() => setShowUPIUpload(true)}
            variant="secondary"
            className="flex items-center gap-2"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
            Connect UPI
          </Button>
          <Button
            onClick={() => setShowBulkUpload(true)}
            variant="primary"
            className="flex items-center gap-2"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            Bulk Upload
          </Button>
        </div>
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

      {/* Modals */}
      <BulkUpload
        isOpen={showBulkUpload}
        onClose={() => setShowBulkUpload(false)}
        userId={userId}
        onSuccess={() => {
          load();
        }}
      />
      <UPIIntegration
        isOpen={showUPIUpload}
        onClose={() => setShowUPIUpload(false)}
        userId={userId}
        onSuccess={() => {
          load();
        }}
      />
    </div>
  );
};

export default TransactionsPage;
