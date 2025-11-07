import React, { useState, useRef } from "react";
import { uploadTransactionsAPI } from "@api/finance";
import { useApp } from "@store/AppContext";
import Button from "@components/ui/Button";
import Modal from "@components/ui/Modal";

const BulkUploadModal = ({ isOpen, onClose, onSuccess }) => {
  const { state, setToast } = useApp();
  const userId = state.user?.id;
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = [
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      ];
      const validExtensions = [".csv", ".xls", ".xlsx"];
      const fileExtension = selectedFile.name
        .toLowerCase()
        .substring(selectedFile.name.lastIndexOf("."));

      if (
        !validTypes.includes(selectedFile.type) &&
        !validExtensions.includes(fileExtension)
      ) {
        setToast({
          message: "Please upload a CSV or Excel file (.csv, .xls, .xlsx)",
          type: "error",
        });
        return;
      }

      setFile(selectedFile);
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file || !userId) return;

    try {
      setIsUploading(true);
      const response = await uploadTransactionsAPI(userId, file);
      setResult(response);

      if (response.success_count > 0) {
        setToast({
          message: `Successfully uploaded ${response.success_count} transaction(s)`,
          type: "success",
        });

        // Trigger data refresh
        window.dispatchEvent(
          new CustomEvent("finance:data-updated", {
            detail: { entity: "transactions", action: "bulk-upload" },
          })
        );

        if (onSuccess) onSuccess();
      }

      if (response.error_count > 0) {
        setToast({
          message: `${response.error_count} row(s) failed to upload. Check the errors below.`,
          type: "warning",
        });
      }
    } catch (error) {
      console.error("Upload error:", error);
      setToast({
        message: error.response?.data?.detail || "Failed to upload file",
        type: "error",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    onClose();
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Bulk Upload Transactions"
    >
      <div className="space-y-4">
        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-2">
            File Format Requirements:
          </h4>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>Supported formats: CSV, Excel (.xls, .xlsx)</li>
            <li>
              Required columns:{" "}
              <code className="bg-blue-100 px-1 rounded">description</code>,{" "}
              <code className="bg-blue-100 px-1 rounded">amount</code>,{" "}
              <code className="bg-blue-100 px-1 rounded">date</code>
            </li>
            <li>
              Optional column:{" "}
              <code className="bg-blue-100 px-1 rounded">category</code>
            </li>
            <li>Date format: YYYY-MM-DD (e.g., 2024-03-15)</li>
            <li>Amount: Negative for expenses, positive for income</li>
          </ul>
        </div>

        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select File
          </label>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xls,.xlsx"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100
              cursor-pointer"
          />
          {file && (
            <p className="mt-2 text-sm text-gray-600">
              Selected: <span className="font-medium">{file.name}</span> (
              {(file.size / 1024).toFixed(1)} KB)
            </p>
          )}
        </div>

        {/* Upload Result */}
        {result && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">Upload Summary</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Rows:</span>
                <span className="font-medium text-gray-900">
                  {result.total_rows}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-green-600">Successful:</span>
                <span className="font-medium text-green-600">
                  {result.success_count}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-red-600">Failed:</span>
                <span className="font-medium text-red-600">
                  {result.error_count}
                </span>
              </div>
            </div>

            {result.errors && result.errors.length > 0 && (
              <div className="mt-4">
                <h5 className="font-medium text-red-700 mb-2">Errors:</h5>
                <div className="max-h-40 overflow-y-auto space-y-1">
                  {result.errors.map((error, idx) => (
                    <div
                      key={idx}
                      className="text-xs text-red-600 bg-red-50 p-2 rounded"
                    >
                      Row {error.row}: {error.error}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 pt-4">
          <Button
            onClick={handleUpload}
            disabled={!file || isUploading}
            variant="primary"
            className="flex-1"
          >
            {isUploading ? "Uploading..." : "Upload"}
          </Button>
          {result && (
            <Button onClick={handleReset} variant="secondary">
              Upload Another
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

export default BulkUploadModal;
