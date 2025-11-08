import { useState } from "react";
import { parseUPIMessage } from "../../api/upload";
import Modal from "../ui/Modal";
import Button from "../ui/Button";

/**
 * UPI Integration Component
 * Allows users to connect their UPI ID to automatically fetch transactions
 */
export default function UPIIntegration({ isOpen, onClose, userId, onSuccess }) {
  const [upiId, setUpiId] = useState("");
  const [step, setStep] = useState(1); // 1: Enter UPI, 2: Verify, 3: Fetch transactions
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [verificationCode, setVerificationCode] = useState("");
  const [fetchedTransactions, setFetchedTransactions] = useState([]);

  const validateUpiId = (id) => {
    // UPI ID format: username@bankname
    const upiRegex = /^[\w.-]+@[\w.-]+$/;
    return upiRegex.test(id);
  };

  const handleConnectUPI = async () => {
    if (!upiId.trim()) {
      setError("Please enter your UPI ID");
      return;
    }

    if (!validateUpiId(upiId)) {
      setError("Invalid UPI ID format. Use format: yourname@bankname");
      return;
    }

    setLoading(true);
    setError("");

    try {
      // Simulate API call to send verification code
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // In real implementation, this would call your backend
      // which would integrate with UPI/bank APIs
      setStep(2);
      setError("");
    } catch (err) {
      setError(err.message || "Failed to connect UPI");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyAndFetch = async () => {
    if (!verificationCode.trim()) {
      setError("Please enter the verification code");
      return;
    }

    setLoading(true);
    setError("");

    try {
      // Simulate verification and transaction fetch
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Generate mock transactions (in real app, this comes from UPI/bank API)
      const mockTransactions = [
        {
          id: 1,
          description: "Payment to Amazon",
          amount: -1250.5,
          date: new Date().toISOString().split("T")[0],
          category: "Shopping",
          merchant: "Amazon",
          upiRef: "UPI" + Math.random().toString().slice(2, 14),
        },
        {
          id: 2,
          description: "Payment to Swiggy",
          amount: -450.0,
          date: new Date(Date.now() - 86400000).toISOString().split("T")[0],
          category: "Food & Dining",
          merchant: "Swiggy",
          upiRef: "UPI" + Math.random().toString().slice(2, 14),
        },
        {
          id: 3,
          description: "Salary Credit",
          amount: 50000.0,
          date: new Date(Date.now() - 86400000 * 2).toISOString().split("T")[0],
          category: "Income",
          merchant: "Employer",
          upiRef: "UPI" + Math.random().toString().slice(2, 14),
        },
        {
          id: 4,
          description: "Payment to Uber",
          amount: -320.0,
          date: new Date(Date.now() - 86400000 * 3).toISOString().split("T")[0],
          category: "Transportation",
          merchant: "Uber",
          upiRef: "UPI" + Math.random().toString().slice(2, 14),
        },
        {
          id: 5,
          description: "Payment to Netflix",
          amount: -649.0,
          date: new Date(Date.now() - 86400000 * 5).toISOString().split("T")[0],
          category: "Entertainment",
          merchant: "Netflix",
          upiRef: "UPI" + Math.random().toString().slice(2, 14),
        },
      ];

      setFetchedTransactions(mockTransactions);
      setStep(3);
      setResult({
        success: true,
        message: `Successfully fetched ${mockTransactions.length} transactions from ${upiId}`,
        count: mockTransactions.length,
      });
    } catch (err) {
      setError(err.message || "Failed to verify and fetch transactions");
    } finally {
      setLoading(false);
    }
  };

  const handleImportTransactions = async () => {
    setLoading(true);
    setError("");

    try {
      // In real implementation, send transactions to backend
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Call success callback
      if (onSuccess) {
        onSuccess();
      }

      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err) {
      setError(err.message || "Failed to import transactions");
      setLoading(false);
    }
  };

  const handleClose = () => {
    setUpiId("");
    setVerificationCode("");
    setError("");
    setResult(null);
    setStep(1);
    setFetchedTransactions([]);
    setLoading(false);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Connect UPI Account"
      size="lg"
    >
      <div className="space-y-4">
        {/* Step Indicator */}
        <div className="flex items-center justify-between mb-6">
          <div
            className={`flex items-center ${
              step >= 1 ? "text-blue-600" : "text-gray-400"
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step >= 1 ? "bg-blue-600 text-white" : "bg-gray-300"
              }`}
            >
              1
            </div>
            <span className="ml-2 text-sm font-medium">Enter UPI ID</span>
          </div>
          <div className="flex-1 h-1 mx-3 bg-gray-300">
            <div
              className={`h-full transition-all ${
                step >= 2 ? "bg-blue-600 w-full" : "w-0"
              }`}
            ></div>
          </div>
          <div
            className={`flex items-center ${
              step >= 2 ? "text-blue-600" : "text-gray-400"
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step >= 2 ? "bg-blue-600 text-white" : "bg-gray-300"
              }`}
            >
              2
            </div>
            <span className="ml-2 text-sm font-medium">Verify</span>
          </div>
          <div className="flex-1 h-1 mx-3 bg-gray-300">
            <div
              className={`h-full transition-all ${
                step >= 3 ? "bg-blue-600 w-full" : "w-0"
              }`}
            ></div>
          </div>
          <div
            className={`flex items-center ${
              step >= 3 ? "text-blue-600" : "text-gray-400"
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step >= 3 ? "bg-blue-600 text-white" : "bg-gray-300"
              }`}
            >
              3
            </div>
            <span className="ml-2 text-sm font-medium">Import</span>
          </div>
        </div>

        {/* Step 1: Enter UPI ID */}
        {step === 1 && (
          <>
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 border-l-4 border-purple-500 rounded-lg p-4">
              <h4 className="font-semibold text-purple-900 mb-2 flex items-center gap-2">
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
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                How UPI Auto-Sync Works
              </h4>
              <ul className="text-sm text-purple-800 space-y-1 list-disc list-inside ml-2">
                <li>Enter your UPI ID (e.g., yourname@paytm)</li>
                <li>Verify ownership with OTP</li>
                <li>Automatically fetch all your UPI transactions</li>
                <li>Transactions are categorized and imported instantly</li>
              </ul>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-sm text-blue-900 font-medium mb-1">
                Supported UPI Providers:
              </p>
              <div className="flex flex-wrap gap-2 mt-2">
                {[
                  "Google Pay",
                  "PhonePe",
                  "Paytm",
                  "BHIM",
                  "Amazon Pay",
                  "WhatsApp Pay",
                ].map((provider) => (
                  <span
                    key={provider}
                    className="px-3 py-1 bg-white text-blue-700 text-xs font-medium rounded-full border border-blue-200"
                  >
                    {provider}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Enter Your UPI ID
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={upiId}
                  onChange={(e) => setUpiId(e.target.value.toLowerCase())}
                  placeholder="yourname@paytm"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg 
                    focus:outline-none focus:ring-2 focus:ring-purple-500 
                    text-sm"
                  disabled={loading}
                />
                <div className="absolute right-3 top-3 text-gray-400">
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
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                </div>
              </div>
              <p className="mt-2 text-xs text-gray-500">
                Format: username@provider (e.g., john@paytm, mary@phonepe)
              </p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <div className="flex gap-2">
                <svg
                  className="w-5 h-5 text-yellow-600 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <div>
                  <p className="text-sm text-yellow-800 font-medium">
                    Demo Mode
                  </p>
                  <p className="text-xs text-yellow-700 mt-1">
                    This is a demo. In production, this would integrate with
                    official UPI/bank APIs to fetch real transactions securely.
                  </p>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Step 2: Verification */}
        {step === 2 && (
          <>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
              <svg
                className="w-12 h-12 text-green-600 mx-auto mb-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-sm text-green-800">
                Verification code sent to your UPI-linked mobile number
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Enter Verification Code
              </label>
              <input
                type="text"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                placeholder="Enter 6-digit code"
                maxLength={6}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg 
                  focus:outline-none focus:ring-2 focus:ring-purple-500 
                  text-center text-2xl tracking-widest font-mono"
                disabled={loading}
              />
              <p className="mt-2 text-xs text-gray-500 text-center">
                For demo, enter any 6 digits
              </p>
            </div>

            <div className="text-center">
              <button className="text-sm text-purple-600 hover:text-purple-800 font-medium">
                Resend Code
              </button>
            </div>
          </>
        )}

        {/* Step 3: Show Fetched Transactions */}
        {step === 3 && (
          <>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-semibold text-green-900 mb-2 flex items-center gap-2">
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
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Successfully Connected!
              </h4>
              <p className="text-sm text-green-800">
                Found {fetchedTransactions.length} transactions from{" "}
                <strong>{upiId}</strong>
              </p>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                <h5 className="text-sm font-semibold text-gray-900">
                  Transactions to Import
                </h5>
              </div>
              <div className="max-h-64 overflow-y-auto">
                {fetchedTransactions.map((tx) => (
                  <div
                    key={tx.id}
                    className="px-4 py-3 border-b border-gray-100 hover:bg-gray-50"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          {tx.description}
                        </p>
                        <div className="flex gap-3 mt-1">
                          <span className="text-xs text-gray-500">
                            {tx.date}
                          </span>
                          <span className="text-xs text-gray-500">•</span>
                          <span className="text-xs text-gray-600">
                            {tx.category}
                          </span>
                          <span className="text-xs text-gray-500">•</span>
                          <span className="text-xs text-gray-400 font-mono">
                            {tx.upiRef}
                          </span>
                        </div>
                      </div>
                      <div
                        className={`text-sm font-semibold ${
                          tx.amount < 0 ? "text-red-600" : "text-green-600"
                        }`}
                      >
                        {tx.amount < 0 ? "-" : "+"}₹
                        {Math.abs(tx.amount).toFixed(2)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-xs text-blue-800">
                💡 These transactions will be automatically categorized and
                added to your account
              </p>
            </div>
          </>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
          <Button variant="outline" onClick={handleClose} disabled={loading}>
            Cancel
          </Button>

          {step === 1 && (
            <Button
              onClick={handleConnectUPI}
              disabled={!upiId.trim() || loading}
            >
              {loading ? "Connecting..." : "Connect UPI"}
            </Button>
          )}

          {step === 2 && (
            <Button
              onClick={handleVerifyAndFetch}
              disabled={verificationCode.length !== 6 || loading}
            >
              {loading ? "Verifying..." : "Verify & Fetch Transactions"}
            </Button>
          )}

          {step === 3 && (
            <Button onClick={handleImportTransactions} disabled={loading}>
              {loading
                ? "Importing..."
                : `Import ${fetchedTransactions.length} Transactions`}
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
}
