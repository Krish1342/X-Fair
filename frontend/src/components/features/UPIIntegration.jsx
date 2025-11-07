import { useState } from "react";
import { parseUPIMessage } from "../../api/upload";
import Modal from "../ui/Modal";
import Button from "../ui/Button";

/**
 * UPI Integration Component
 * Allows users to paste UPI SMS messages to automatically create transactions
 */
export default function UPIIntegration({ isOpen, onClose, userId, onSuccess }) {
  const [message, setMessage] = useState("");
  const [parsing, setParsing] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleParse = async () => {
    if (!message.trim()) {
      setError("Please paste a UPI message");
      return;
    }

    setParsing(true);
    setError("");
    setResult(null);

    try {
      const response = await parseUPIMessage(message, userId);
      setResult(response);

      // Call onSuccess callback after successful parse
      if (onSuccess && response.success) {
        setTimeout(() => {
          onSuccess();
          handleClose();
        }, 2000);
      }
    } catch (err) {
      setError(err.message || "Failed to parse UPI message");
    } finally {
      setParsing(false);
    }
  };

  const handleClose = () => {
    setMessage("");
    setError("");
    setResult(null);
    setParsing(false);
    onClose();
  };

  const exampleMessages = [
    {
      bank: "SBI",
      message:
        "Rs.500.00 debited from A/c **1234 on 15-Jan-24 to VPA abc@paytm (UPI Ref No 401234567890). Available Balance: Rs.10,500.50",
    },
    {
      bank: "HDFC",
      message:
        "Rs 250.00 debited from your HDFC Bank A/c **5678 to VPA merchant@upi on 10-Jan-24. UPI:402345678901. Not you? Call 1860.",
    },
    {
      bank: "Google Pay",
      message:
        "You paid Rs.1,200.00 to Amazon via Google Pay UPI on 12-Jan-24. UPI transaction ID: 403456789012",
    },
  ];

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="UPI Message Parser">
      <div className="space-y-4">
        {/* Info */}
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <h4 className="font-semibold text-purple-900 mb-2">How it works:</h4>
          <ul className="text-sm text-purple-800 space-y-1 list-disc list-inside">
            <li>Copy UPI transaction SMS from your bank</li>
            <li>Paste the message below</li>
            <li>We'll automatically extract transaction details</li>
            <li>Supports 10+ banks and UPI apps</li>
          </ul>
        </div>

        {/* Supported Banks */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-sm text-blue-900 font-medium mb-1">
            Supported Banks & Apps:
          </p>
          <p className="text-xs text-blue-700">
            SBI, HDFC, ICICI, Axis, Kotak, PNB, BOB, Google Pay, PhonePe, Paytm,
            and more
          </p>
        </div>

        {/* Message Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Paste UPI Message
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Paste your UPI transaction SMS here..."
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md 
              focus:outline-none focus:ring-2 focus:ring-purple-500 
              text-sm resize-none"
            disabled={parsing}
          />
        </div>

        {/* Example Messages */}
        <details className="text-sm">
          <summary className="cursor-pointer text-gray-700 font-medium hover:text-gray-900">
            View Example Messages
          </summary>
          <div className="mt-3 space-y-3">
            {exampleMessages.map((ex, idx) => (
              <div
                key={idx}
                className="bg-gray-50 border border-gray-200 rounded p-3"
              >
                <p className="text-xs font-semibold text-gray-600 mb-1">
                  {ex.bank}:
                </p>
                <p className="text-xs text-gray-700 font-mono">{ex.message}</p>
                <button
                  onClick={() => setMessage(ex.message)}
                  className="mt-2 text-xs text-purple-600 hover:text-purple-800 font-medium"
                >
                  Use this example
                </button>
              </div>
            ))}
          </div>
        </details>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Success Result */}
        {result && result.success && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-semibold text-green-900 mb-3">
              ✓ Transaction Parsed Successfully!
            </h4>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="text-gray-600 font-medium">Description:</p>
                <p className="text-gray-900">
                  {result.transaction.description}
                </p>
              </div>
              <div>
                <p className="text-gray-600 font-medium">Amount:</p>
                <p
                  className={`font-semibold ${
                    result.transaction.amount < 0
                      ? "text-red-600"
                      : "text-green-600"
                  }`}
                >
                  ₹{Math.abs(result.transaction.amount).toFixed(2)}
                  {result.transaction.amount < 0 ? " (Expense)" : " (Income)"}
                </p>
              </div>
              <div>
                <p className="text-gray-600 font-medium">Date:</p>
                <p className="text-gray-900">{result.transaction.date}</p>
              </div>
              <div>
                <p className="text-gray-600 font-medium">Category:</p>
                <p className="text-gray-900">{result.transaction.category}</p>
              </div>
              {result.transaction.reference && (
                <div className="col-span-2">
                  <p className="text-gray-600 font-medium">Reference:</p>
                  <p className="text-gray-900 text-xs font-mono">
                    {result.transaction.reference}
                  </p>
                </div>
              )}
              {result.bank && (
                <div className="col-span-2">
                  <p className="text-gray-600 font-medium">Bank Detected:</p>
                  <p className="text-gray-900">{result.bank}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 justify-end pt-4">
          <Button variant="outline" onClick={handleClose} disabled={parsing}>
            Cancel
          </Button>
          <Button onClick={handleParse} disabled={!message.trim() || parsing}>
            {parsing ? "Parsing..." : "Parse & Add Transaction"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
