import { useState } from "react";
import { parseUPIMessage } from "@api/upload";
import Modal from "@components/ui/Modal";
import Button from "@components/ui/Button";
import { useApp } from "@store/AppContext";

/**
 * UPI Transaction Modal
 * Allows users to paste UPI SMS messages to automatically extract transaction data
 */
export default function UPIModal({ isOpen, onClose, userId, onSuccess }) {
  const { setToast } = useApp();
  const [message, setMessage] = useState("");
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    if (!message.trim()) {
      setToast({ message: "Please enter a UPI message", type: "error" });
      return;
    }

    setProcessing(true);
    setResult(null);

    try {
      const response = await parseUPIMessage(message, userId);

      if (response.success) {
        setResult(response);
        setToast({
          message: "Transaction added successfully from UPI message",
          type: "success",
        });

        // Trigger data refresh event
        window.dispatchEvent(
          new CustomEvent("finance:data-updated", {
            detail: { entity: "transactions", action: "upi-add" },
          })
        );

        if (onSuccess) {
          setTimeout(() => {
            onSuccess();
            handleClose();
          }, 2000);
        }
      }
    } catch (err) {
      console.error("UPI parsing error:", err);
      setToast({
        message: err.response?.data?.detail || "Failed to parse UPI message",
        type: "error",
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleClose = () => {
    setMessage("");
    setResult(null);
    setProcessing(false);
    onClose();
  };

  const exampleMessages = [
    {
      bank: "SBI",
      text: "Rs 500.00 debited from A/c **1234 on 15-Jan-24 to VPA merchant@paytm (UPI Ref No 123456789)",
    },
    {
      bank: "HDFC",
      text: "Rs. 1,250.50 debited from your HDFC Bank A/c XX1234 on 16-Jan-24. Info: UPI/123456789/Payment to merchant@phonepe",
    },
    {
      bank: "PhonePe",
      text: "You paid ₹300 to Merchant Name via PhonePe. Transaction ID: PP123456789",
    },
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Add Transaction from UPI Message"
    >
      <div className="space-y-4">
        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-2">How it works:</h4>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>Copy your UPI transaction SMS or notification</li>
            <li>Paste it in the text box below</li>
            <li>We'll automatically extract the transaction details</li>
            <li>
              Supports SBI, HDFC, ICICI, Axis, PhonePe, Google Pay, and more
            </li>
          </ul>
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
            rows={5}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            disabled={processing}
          />
        </div>

        {/* Example Messages */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Example Messages (Click to use):
          </h4>
          <div className="space-y-2">
            {exampleMessages.map((example, idx) => (
              <button
                key={idx}
                onClick={() => setMessage(example.text)}
                className="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors"
              >
                <div className="text-xs font-medium text-gray-600 mb-1">
                  {example.bank}
                </div>
                <div className="text-xs text-gray-700 break-words">
                  {example.text}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Result Display */}
        {result && result.success && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-semibold text-green-900 mb-2">
              ✓ Transaction Extracted Successfully!
            </h4>
            <div className="text-sm text-green-800 space-y-1">
              {result.transaction && (
                <>
                  <p>
                    <span className="font-medium">Description:</span>{" "}
                    {result.transaction.description}
                  </p>
                  <p>
                    <span className="font-medium">Amount:</span> ₹
                    {Math.abs(result.transaction.amount).toFixed(2)}
                  </p>
                  <p>
                    <span className="font-medium">Category:</span>{" "}
                    {result.transaction.category}
                  </p>
                  <p>
                    <span className="font-medium">Date:</span>{" "}
                    {result.transaction.date}
                  </p>
                  {result.transaction.merchant && (
                    <p>
                      <span className="font-medium">Merchant:</span>{" "}
                      {result.transaction.merchant}
                    </p>
                  )}
                </>
              )}
            </div>
            {result.parsed_data && (
              <details className="mt-3">
                <summary className="cursor-pointer text-xs text-green-700 font-medium">
                  View parsed data
                </summary>
                <pre className="mt-2 text-xs text-green-600 bg-green-100 p-2 rounded overflow-x-auto">
                  {JSON.stringify(result.parsed_data, null, 2)}
                </pre>
              </details>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 justify-end pt-4">
          <Button variant="outline" onClick={handleClose} disabled={processing}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!message.trim() || processing}
          >
            {processing ? "Processing..." : "Add Transaction"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
