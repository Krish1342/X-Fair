import React from "react";
import ChatBot from "@features/ChatBot";

// Thin wrapper that renders the shared ChatBot in floating mode
const FloatingAssistant = () => {
  const htmlMode = import.meta?.env?.VITE_CHAT_HTML_MODE === "true";
  return <ChatBot htmlMode={htmlMode} />; // default variant is "floating"
};

export default FloatingAssistant;
