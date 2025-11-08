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
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const ext = selectedFile.name.split(".").pop().toLowerCase();
      if (!["csv", "xlsx", "xls", "pdf"].includes(ext)) {
        setError(
          "Please select a CSV, Excel, or PDF file (.csv, .xlsx, .xls, .pdf)"
        );
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError("");
      setResult(null);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      const ext = droppedFile.name.split(".").pop().toLowerCase();
      if (!["csv", "xlsx", "xls", "pdf"].includes(ext)) {
        setError(
          "Please select a CSV, Excel, or PDF file (.csv, .xlsx, .xls, .pdf)"
        );
        setFile(null);
        return;
      }
      setFile(droppedFile);
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

  const downloadTemplate = () => {
    const csvContent = `description,amount,date,category
Grocery Shopping,-150.50,2024-01-15,Food & Dining
Salary,5000.00,2024-01-01,Income
Netflix Subscription,-15.99,2024-01-10,Entertainment
Uber Ride,-25.00,2024-01-12,Transportation
Restaurant Bill,-75.50,2024-01-14,Food & Dining`;

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "transactions_template.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Bulk Upload Transactions"
      size="lg"
    >
      <div className="space-y-4">
        {/* Header Info */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
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
            How to Use Bulk Upload
          </h4>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside ml-2">
            <li>
              Supported formats: CSV, Excel (.xlsx, .xls), PDF (bank statements)
            </li>
            <li>Click the file input below to select your file</li>
            <li>Preview your selection, then click Upload</li>
          </ul>
        </div>

        {/* File Format Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="font-semibold text-blue-900 mb-2">
                File Format Requirements:
              </h4>
              <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
                <li>
                  Supported formats: CSV, Excel (.xlsx, .xls), PDF (bank
                  statements)
                </li>
                <li>Required columns: description, amount, date, category</li>
                <li>Date format: YYYY-MM-DD</li>
                <li>Amount: negative for expenses, positive for income</li>
                <li>PDF: Automatically extracts from bank statement format</li>
              </ul>
            </div>
            <button
              onClick={downloadTemplate}
              className="ml-4 px-3 py-2 text-xs font-medium text-blue-700 bg-white border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors flex items-center gap-1 whitespace-nowrap"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Download Template
            </button>
          </div>
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
        <div
          className={`border-2 border-dashed rounded-lg p-6 transition-all ${
            dragActive
              ? "border-blue-500 bg-blue-50"
              : "border-gray-300 hover:border-blue-400"
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <label
            htmlFor="file-upload"
            className="block text-sm font-medium text-gray-700 mb-3 text-center"
          >
            {dragActive
              ? "Drop your file here!"
              : "Drag & Drop or Click to Select File"}
          </label>
          <div className="flex flex-col items-center justify-center space-y-3">
            <svg
              className={`w-16 h-16 ${
                dragActive ? "text-blue-500" : "text-gray-400"
              }`}
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
            <input
              type="file"
              id="file-upload"
              accept=".csv,.xlsx,.xls,.pdf"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-900
                file:mr-4 file:py-3 file:px-6
                file:rounded-lg file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-600 file:text-white
                hover:file:bg-blue-700
                file:cursor-pointer
                cursor-pointer
                border border-gray-300 rounded-lg
                focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={uploading}
            />
            <p className="text-xs text-gray-500">
              Supported formats: CSV, Excel (.xlsx, .xls), PDF
            </p>
          </div>
          {file && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-800 font-medium">
                ✓ Selected: {file.name}
              </p>
              <p className="text-xs text-green-600">
                Size: {(file.size / 1024).toFixed(2)} KB
              </p>
            </div>
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
              <p>
                Total transactions: {result.summary?.total_rows || result.total}
              </p>
              <p>
                Successfully imported:{" "}
                {result.summary?.success_count || result.imported}
              </p>
              {(result.summary?.error_count || result.skipped) > 0 && (
                <p className="text-yellow-700">
                  Skipped (invalid):{" "}
                  {result.summary?.error_count || result.skipped}
                </p>
              )}
            </div>
            {result.summary?.errors && result.summary.errors.length > 0 && (
              <details className="mt-2">
                <summary className="cursor-pointer text-xs text-red-700 font-medium">
                  View errors ({result.summary.errors.length})
                </summary>
                <ul className="mt-2 text-xs text-red-600 space-y-1 max-h-32 overflow-y-auto">
                  {result.summary.errors.map((err, idx) => (
                    <li key={idx}>{err}</li>
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
