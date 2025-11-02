import React, { useEffect, useMemo, useRef, useState } from "react";
import { getWorkflowVisualizationAPI } from "@api/finance";

/**
 * WorkflowVisualizer
 * - Fetches workflow structure from backend (/workflow/visualization)
 * - Optionally streams a live run via SSE to highlight the active node
 */
export default function WorkflowVisualizer({ className = "", liveUserId, liveQuery }) {
  const [graph, setGraph] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeNode, setActiveNode] = useState(null);
  const esRef = useRef(null);

  // Fetch static graph
  useEffect(() => {
    let mounted = true;
    setLoading(true);
    getWorkflowVisualizationAPI()
      .then((res) => {
        if (!mounted) return;
        setGraph(res?.workflow_structure || null);
        setError(null);
      })
      .catch((e) => setError(e?.message || "Failed to load workflow graph"))
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, []);

  // Live stream for highlighting active node
  useEffect(() => {
    // Cleanup any previous stream
    if (esRef.current) {
      esRef.current.close();
      esRef.current = null;
    }
    setActiveNode(null);

    const enableLive = Boolean(liveUserId) && Boolean(liveQuery);
    if (!enableLive) return;

    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || "/api/v1";
      const url = `${apiBase}/workflow/run/stream?user_id=${encodeURIComponent(
        String(liveUserId)
      )}&query=${encodeURIComponent(String(liveQuery))}`;

      const es = new EventSource(url, { withCredentials: false });
      esRef.current = es;

      es.onmessage = (evt) => {
        try {
          const payload = JSON.parse(evt.data);
          const ev = String(payload?.event || "").toLowerCase();
          const node = payload?.data?.node;
          if (node && (ev.includes("node_start") || ev.includes("node_end"))) {
            setActiveNode(node);
          }
        } catch (_) {
          // ignore malformed events
        }
      };

      es.onerror = () => {
        // auto-close on error to avoid noisy console
        es.close();
        esRef.current = null;
      };
    } catch (_) {
      // ignore if EventSource fails
    }

    return () => {
      if (esRef.current) {
        esRef.current.close();
        esRef.current = null;
      }
    };
  }, [liveUserId, liveQuery]);

  const stages = useMemo(() => graph?.stages || [], [graph]);
  const nodeMap = useMemo(() => {
    const m = new Map();
    (graph?.nodes || []).forEach((n) => m.set(n.id, n));
    return m;
  }, [graph]);

  if (loading) {
    return (
      <div className={className}>
        <div className="text-gray-500">Loading workflow…</div>
      </div>
    );
  }
  if (error) {
    return (
      <div className={className}>
        <div className="text-red-600">{error}</div>
      </div>
    );
  }
  if (!graph) {
    return (
      <div className={className}>
        <div className="text-gray-500">No workflow data.</div>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Stage columns */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stages.map((stage) => (
          <div key={stage.id} className="border rounded-lg p-4 bg-gray-50">
            <div className="text-sm font-semibold mb-3">{stage.label}</div>
            <div className="flex flex-col gap-2">
              {stage.nodes.map((nid) => {
                const node = nodeMap.get(nid) || { id: nid, label: nid };
                const isActive = activeNode === node.id;
                return (
                  <div
                    key={node.id}
                    className={`text-sm px-3 py-2 rounded border bg-white flex items-center justify-between ${
                      isActive ? "border-blue-500 ring-2 ring-blue-200" : "border-gray-200"
                    }`}
                    title={node.id}
                  >
                    <span className="truncate">{node.label || node.id}</span>
                    {isActive && (
                      <span className="ml-2 inline-flex items-center text-xs text-blue-600">Active</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Legend and tips */}
      <div className="mt-4 text-xs text-gray-500">
        <div>Edges follow the standard stage flows; see the docs for details.</div>
        {liveUserId && liveQuery ? (
          <div className="mt-1">Live mode: streaming node events for the current query.</div>
        ) : (
          <div className="mt-1">Tip: provide a query above to see live node highlights.</div>
        )}
      </div>
    </div>
  );
}
