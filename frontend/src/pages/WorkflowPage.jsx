import React, { useState } from "react";
import WorkflowVisualizer from "@components/features/WorkflowVisualizer";
import { useApp } from "@store/AppContext";

export default function WorkflowPage() {
  const { state } = useApp();
  const [query, setQuery] = useState("");
  const userId = state?.user?.id;

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-2">Workflow</h1>
        <p className="text-gray-600">Architecture and live execution trace.</p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-end">
          <div className="flex-1 w-full">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Test Query
            </label>
            <input
              type="text"
              className="w-full border rounded px-3 py-2"
              placeholder="e.g., Help me plan a vacation budget"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <div className="text-sm text-gray-600">
            User ID: <span className="font-medium">{userId || "N/A"}</span>
          </div>
        </div>
        <WorkflowVisualizer
          className="mt-6"
          liveUserId={userId}
          liveQuery={query || undefined}
        />
      </div>
    </div>
  );
}
