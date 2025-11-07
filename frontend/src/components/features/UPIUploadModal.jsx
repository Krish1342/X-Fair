import React, { useState } from "react";
import { uploadUPIMessageAPI } from "@api/finance";
import { useApp } from "@store/AppContext";
import Button from "@components/ui/Button";
import Modal from "@components/ui/Modal";

const UPIUploadModal = ({ isOpen, onClose, onSuccess }) => {
  const { state, setToast } = useApp();
  const userId = state.user?.id;
  const [message, setMessage] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);

  const handleProcess = async () => {
    if (!message.trim() || !userId) return;

    try {
      setIsProcessing(true);
      const response = await uploadUPIMessageAPI(userId, message.trim());
      setResult(response);

      if (response.transaction_id) {
        setToast({
          message: "UPI transaction added successfully",
          type: "success",
        });

        // Trigger data refresh
        window.dispatchEvent(
          new CustomEvent("finance:data-updated", {
            detail: { entity: "transactions", action: "upi-upload" },
          })
        );

        if (onSuccess) onSuccess();
      } else if (response.error) {
        setToast({
          message: response.error,
          type: "error",
        });
      }
    } catch (error) {
      console.error("UPI processing error:", error);
      setToast({
        message:
          error.response?.data?.detail || "Failed to process UPI message",
        type: "error",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClose = () => {
    setMessage("");
    setResult(null);
    onClose();
  };

  const handleReset = () => {
    setMessage("");
    setResult(null);
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Add UPI Transaction">
      <div className="space-y-4">
        {/* Instructions */}
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <h4 className="font-semibold text-purple-900 mb-2">How to use:</h4>
          <ul className="text-sm text-purple-800 space-y-1 list-disc list-inside">
            <li>Copy the entire UPI transaction SMS from your bank</li>
            <li>Paste it in the text area below</li>
            <li>We'll automatically extract transaction details</li>
            <li>
              Supports: SBI, HDFC, ICICI, Axis, Kotak, PNB, BOB, Google Pay,
              PhonePe, Paytm
            </li>
          </ul>
        </div>

        {/* Example */}
        <details className="text-xs text-gray-600">
          <summary className="cursor-pointer font-medium hover:text-gray-900">
            View example SMS format
          </summary>
          <div className="mt-2 p-3 bg-gray-50 rounded border border-gray-200 font-mono">
            Rs 500.00 debited from A/c XX1234 on 15-03-2024. UPI Ref
            410123456789. Paid to AMAZON
          </div>
        </details>

        {/* Message Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            UPI Transaction Message
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Paste your UPI transaction SMS here..."
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg 
              focus:ring-2 focus:ring-purple-500 focus:border-transparent
              text-sm font-mono"
          />
          <p className="mt-1 text-xs text-gray-500">
            {message.length} characters
          </p>
        </div>

        {/* Processing Result */}
        {result && (
          <div
            className={`border rounded-lg p-4 ${
              result.transaction_id
                ? "bg-green-50 border-green-200"
                : "bg-red-50 border-red-200"
            }`}
          >
            {result.transaction_id ? (
              <div>
                <h4 className="font-semibold text-green-900 mb-3">
                  Transaction Added Successfully
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Amount:</span>
                    <span className="font-medium text-red-600">
                      -₹{result.amount}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Merchant:</span>
                    <span className="font-medium text-gray-900">
                      {result.merchant || "N/A"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Category:</span>
                    <span className="font-medium text-gray-900">
                      {result.category}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Date:</span>
                    <span className="font-medium text-gray-900">
                      {result.date}
                    </span>
                  </div>
                  {result.reference_number && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Ref Number:</span>
                      <span className="font-medium text-gray-900 font-mono text-xs">
                        {result.reference_number}
                      </span>
                    </div>
                  )}
                  {result.bank_detected && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Bank/App:</span>
                      <span className="font-medium text-gray-900">
                        {result.bank_detected}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div>
                <h4 className="font-semibold text-red-900 mb-2">
                  Failed to Process
                </h4>
                <p className="text-sm text-red-700">{result.error}</p>
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 pt-4">
          <Button
            onClick={handleProcess}
            disabled={!message.trim() || isProcessing}
            variant="primary"
            className="flex-1"
          >
            {isProcessing ? "Processing..." : "Process UPI Message"}
          </Button>
          {result && (
            <Button onClick={handleReset} variant="secondary">
              Add Another
            </Button>
          )}
          <Button onClick={handleClose} variant="secondary">
            {result ? "Close" : "Cancel"}
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default UPIUploadModal;
