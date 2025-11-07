import { useState } from "react";
import { uploadTransactionsFile } from "../../api/upload";
import Modal from "../ui/Modal";
import Button from "../ui/Button";

/**
 * Bulk Upload Component
 * Allows users to upload CSV or Excel files with transaction data
 */
export default function BulkUpload({ isOpen, onClose, userId, onSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const ext = selectedFile.name.split(".").pop().toLowerCase();
      if (!["csv", "xlsx", "xls"].includes(ext)) {
        setError("Please select a CSV or Excel file (.csv, .xlsx, .xls)");
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError("");
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first");
      return;
    }

    setUploading(true);
    setError("");
    setResult(null);

    try {
      const response = await uploadTransactionsFile(file, userId);
      setResult(response);

      // Call onSuccess callback after successful upload
      if (onSuccess && response.success) {
        setTimeout(() => {
          onSuccess();
          handleClose();
        }, 2000);
      }
    } catch (err) {
      setError(err.message || "Failed to upload file");
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setError("");
    setResult(null);
    setUploading(false);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Bulk Upload Transactions"
    >
      <div className="space-y-4">
        {/* File Format Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-2">
            File Format Requirements:
          </h4>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>Supported formats: CSV, Excel (.xlsx, .xls)</li>
            <li>Required columns: description, amount, date, category</li>
            <li>Date format: YYYY-MM-DD</li>
            <li>Amount: negative for expenses, positive for income</li>
          </ul>
        </div>

        {/* Example */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 mb-2">Example:</h4>
          <pre className="text-xs text-gray-700 overflow-x-auto">
            {`description,amount,date,category
Grocery Shopping,-150.50,2024-01-15,Food
Salary,5000.00,2024-01-01,Income
Netflix Subscription,-15.99,2024-01-10,Entertainment`}
          </pre>
        </div>

        {/* File Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select File
          </label>
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100
              cursor-pointer"
            disabled={uploading}
          />
          {file && (
            <p className="mt-2 text-sm text-green-600">
              Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
            </p>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Success Result */}
        {result && result.success && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-semibold text-green-900 mb-2">
              ✓ Upload Successful!
            </h4>
            <div className="text-sm text-green-800 space-y-1">
              <p>Total transactions: {result.total}</p>
              <p>Successfully imported: {result.imported}</p>
              {result.skipped > 0 && (
                <p className="text-yellow-700">
                  Skipped (invalid): {result.skipped}
                </p>
              )}
            </div>
            {result.errors && result.errors.length > 0 && (
              <details className="mt-2">
                <summary className="cursor-pointer text-xs text-red-700 font-medium">
                  View errors ({result.errors.length})
                </summary>
                <ul className="mt-2 text-xs text-red-600 space-y-1 max-h-32 overflow-y-auto">
                  {result.errors.map((err, idx) => (
                    <li key={idx}>
                      Row {err.row}: {err.error}
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 justify-end pt-4">
          <Button variant="outline" onClick={handleClose} disabled={uploading}>
            Cancel
          </Button>
          <Button onClick={handleUpload} disabled={!file || uploading}>
            {uploading ? "Uploading..." : "Upload"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
