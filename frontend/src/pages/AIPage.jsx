import React, { useEffect, useState } from "react";
import { useApp } from "@store/AppContext";
import {
  getWorkflowStatusAPI,
  getDashboardAPI,
  executeActionAPI,
} from "@api/finance";

export default function AIPage() {
  const { state } = useApp();
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [insights, setInsights] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [execMsg, setExecMsg] = useState(null);
  const [executingIdx, setExecutingIdx] = useState(null);
  const [rerunning, setRerunning] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        if (!state.user?.id) return;
        const s = await getWorkflowStatusAPI(state.user.id);
        setStatus(s);
        // Load insights from dashboard endpoint for the AI page
        const dash = await getDashboardAPI({
          user_id: state.user.id,
          timeframe: "30d",
        });
        if (Array.isArray(dash?.insights)) setInsights(dash.insights);
        if (Array.isArray(dash?.suggestions)) setSuggestions(dash.suggestions);
      } catch (e) {
        setError(e.message);
      }
    };
    load();
  }, [state.user?.id]);

  const executeSuggestion = async (sug, idx) => {
    try {
      setExecMsg(null);
      setExecutingIdx(idx ?? -1);
      await executeActionAPI({
        user_id: state.user.id,
        action: sug.action,
        params: sug.params,
      });
      setExecMsg(`Done: ${sug.label}`);
      // Refresh insights/suggestions from dashboard to reflect changes
      const dash = await getDashboardAPI({
        user_id: state.user.id,
        timeframe: "30d",
      });
      if (Array.isArray(dash?.insights)) setInsights(dash.insights);
      if (Array.isArray(dash?.suggestions)) setSuggestions(dash.suggestions);
      // Broadcast a global event so other screens (e.g., Dashboard) refresh
      window.dispatchEvent(
        new CustomEvent("finance:data-updated", {
          detail: {
            entity: sug.action?.split("_")?.[1] || "unknown",
            action: "execute",
          },
        })
      );
    } catch (e) {
      setExecMsg(`Failed: ${e.message}`);
    } finally {
      setExecutingIdx(null);
    }
  };

  const rerunWorkflow = async () => {
    if (!state.user?.id) return;
    setRerunning(true);
    setError(null);
    try {
      const s = await getWorkflowStatusAPI(state.user.id);
      setStatus(s);
      // Optionally refresh insights/suggestions alongside
      const dash = await getDashboardAPI({
        user_id: state.user.id,
        timeframe: "30d",
      });
      if (Array.isArray(dash?.insights)) setInsights(dash.insights);
      if (Array.isArray(dash?.suggestions)) setSuggestions(dash.suggestions);
    } catch (e) {
      setError(e.message);
    } finally {
      setRerunning(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-2">AI Assistant</h1>
        <p className="text-gray-600">
          Chat with the finance agent and view workflow progress.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Workflow Progress</h2>
            <button
              onClick={rerunWorkflow}
              disabled={rerunning || !state.user?.id}
              className={`px-3 py-1 text-sm rounded text-white ${
                rerunning ? "bg-gray-400" : "bg-green-600 hover:bg-green-700"
              }`}
            >
              {rerunning ? "Re-running..." : "Rerun"}
            </button>
          </div>
          {error && <p className="text-red-600 text-sm mb-2">{error}</p>}
          {status ? (
            <>
              {/* Visual Stepper */}
              {(() => {
                const stages = ["started", "mvp", "intermediate", "advanced"];
                const current = String(
                  status.current_stage ||
                    status.stage ||
                    state.workflowStage ||
                    "started"
                ).toLowerCase();
                const currentIdx = Math.max(0, stages.indexOf(current));
                const label = (s) => s.charAt(0).toUpperCase() + s.slice(1);
                return (
                  <div className="flex items-center justify-between">
                    {stages.map((stg, idx) => {
                      const isDone = idx < currentIdx;
                      const isCurrent = idx === currentIdx;
                      return (
                        <div key={stg} className="flex items-center w-full">
                          <div className="flex flex-col items-center text-center">
                            <div
                              className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold ${
                                isCurrent
                                  ? "bg-blue-600 text-white"
                                  : isDone
                                  ? "bg-green-500 text-white"
                                  : "bg-gray-200 text-gray-700"
                              }`}
                            >
                              {isDone ? "✓" : idx + 1}
                            </div>
                            <div
                              className={`mt-2 text-xs ${
                                isCurrent ? "text-blue-700" : "text-gray-600"
                              }`}
                            >
                              {label(stg)}
                            </div>
                          </div>
                          {idx < stages.length - 1 && (
                            <div
                              className={`h-0.5 flex-1 mx-2 ${
                                idx < currentIdx
                                  ? "bg-green-500"
                                  : "bg-gray-200"
                              }`}
                            />
                          )}
                        </div>
                      );
                    })}
                  </div>
                );
              })()}

              {/* Current Stage summary */}
              <div className="mt-4 text-sm text-gray-700">
                <span className="font-medium">Current stage:</span>{" "}
                <span className="uppercase tracking-wide text-blue-700">
                  {String(
                    status.current_stage || status.stage || state.workflowStage
                  )}
                </span>
              </div>

              {/* Next Steps as pills */}
              {Array.isArray(status.next_steps) &&
              status.next_steps.length > 0 ? (
                <div className="mt-3">
                  <div className="text-sm font-medium text-gray-700 mb-2">
                    Next steps
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {status.next_steps.map((ns, i) => (
                      <span
                        key={`${ns}-${i}`}
                        className="px-2 py-1 text-xs rounded-full bg-blue-50 text-blue-700 border border-blue-200"
                      >
                        {ns}
                      </span>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 text-sm mt-3">
                  No next steps available.
                </p>
              )}
            </>
          ) : (
            <p className="text-gray-500 text-sm">No status yet.</p>
          )}
        </div>
      </div>

      {/* AI Insights and Suggestions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">AI Insights</h2>
        <div className="space-y-3">
          {insights?.map((insight, i) => (
            <div
              key={i}
              className="p-3 rounded-lg border bg-blue-50 border-blue-200 text-blue-800"
            >
              <h4 className="font-medium mb-1">{insight.title}</h4>
              <p className="text-sm opacity-90">{insight.description}</p>
              {insight.category && (
                <p className="text-xs mt-1 opacity-75">
                  Category: {insight.category}
                </p>
              )}
            </div>
          ))}
          {(!insights || insights.length === 0) && (
            <p className="text-gray-500 text-sm">No insights available.</p>
          )}
        </div>
        <div className="mt-6">
          <h3 className="text-md font-semibold mb-3">Suggested Actions</h3>
          {execMsg && <p className="text-sm mb-2">{execMsg}</p>}
          <div className="space-y-2">
            {suggestions?.map((sug, i) => (
              <div key={i} className="p-3 rounded-lg border bg-gray-50">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{sug.label}</p>
                    {sug.explain && (
                      <p className="text-xs text-gray-600 mt-1">
                        {sug.explain}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() => executeSuggestion(sug, i)}
                    disabled={executingIdx === i}
                    className={`px-3 py-1 text-sm rounded text-white ${
                      executingIdx === i
                        ? "bg-gray-400"
                        : "bg-blue-600 hover:bg-blue-700"
                    }`}
                  >
                    {executingIdx === i ? "Executing..." : "Execute"}
                  </button>
                </div>
              </div>
            ))}
            {(!suggestions || suggestions.length === 0) && (
              <p className="text-gray-500 text-sm">
                No suggestions at this time.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
