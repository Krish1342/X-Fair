import { useState, useRef, useEffect } from "react";
import { useChatAPI } from "../../api/apis";
import "../../styles/ChatBot.css";

export default function ChatBot() {
  const { sendMessage: sendChatMessage } = useChatAPI();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hi! I'm your Finance Assistant. How can I help you today?",
      isBot: true,
      timestamp: new Date(),
      isHtml: false,
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      isBot: false,
      timestamp: new Date(),
      isHtml: false,
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentMessage = inputMessage;
    setInputMessage("");
    setIsTyping(true);

    try {
      const response = await sendChatMessage(currentMessage);

      // Check if response contains HTML
      const isHtmlResponse = response.includes("<") && response.includes(">");

      const botMessage = {
        id: Date.now() + 1,
        text: response,
        isBot: true,
        timestamp: new Date(),
        isHtml: isHtmlResponse,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage = {
        id: Date.now() + 1,
        text: "I'm experiencing technical difficulties. Please try again later.",
        isBot: true,
        timestamp: new Date(),
        isHtml: false,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  // Send a specific text (used by quick actions) without relying on async state updates
  const sendMessageText = async (text) => {
    if (!text || !text.trim()) return;

    const userMessage = {
      id: Date.now(),
      text,
      isBot: false,
      timestamp: new Date(),
      isHtml: false,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const response = await sendChatMessage(text);
      const isHtmlResponse = response.includes("<") && response.includes(">");
      const botMessage = {
        id: Date.now() + 1,
        text: response,
        isBot: true,
        timestamp: new Date(),
        isHtml: isHtmlResponse,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage = {
        id: Date.now() + 1,
        text: "I'm experiencing technical difficulties. Please try again later.",
        isBot: true,
        timestamp: new Date(),
        isHtml: false,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const quickActions = [
    "How can I manage my budget?",
    "Help me track transactions",
    "Set up financial goals",
  ];

  return (
    <>
      {/* Chat Toggle Button */}
      <button
        className={`chat-toggle ${isOpen ? "open" : ""}`}
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: "fixed",
          bottom: "80px",
          right: "20px",
          width: "60px",
          height: "60px",
          borderRadius: "50%",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          color: "white",
          border: "none",
          cursor: "pointer",
          fontSize: "24px",
          boxShadow: "0 4px 12px rgba(102, 126, 234, 0.3)",
          zIndex: 1000,
          transition: "all 0.3s ease",
        }}
        onMouseEnter={(e) => {
          e.target.style.transform = "scale(1.1)";
          e.target.style.boxShadow = "0 6px 20px rgba(102, 126, 234, 0.4)";
        }}
        onMouseLeave={(e) => {
          e.target.style.transform = "scale(1)";
          e.target.style.boxShadow = "0 4px 12px rgba(102, 126, 234, 0.3)";
        }}
      >
        {isOpen ? "✕" : "💬"}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <div className="chat-header-info">
              <div className="ai-avatar">💰</div>
              <div>
                <h3>Finance Assistant</h3>
                <p>Your Financial Helper</p>
              </div>
            </div>
            <button className="close-chat" onClick={() => setIsOpen(false)}>
              ✕
            </button>
          </div>

          <div className="chat-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.isBot ? "bot" : "user"}`}
                style={{
                  display: message.text || !message.isBot ? "" : "none",
                }}
              >
                <div className="message-content">
                  {message.text &&
                    (message.isHtml ? (
                      <div
                        className="html-content"
                        dangerouslySetInnerHTML={{ __html: message.text }}
                      />
                    ) : (
                      <p>{message.text}</p>
                    ))}
                  {!isTyping && message.text && (
                    <span className="message-time">
                      {formatTime(message.timestamp)}
                    </span>
                  )}
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="message bot typing">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Actions */}
          <div
            className={`quick-actions ${
              messages.length <= 1 ? "show" : "hide"
            }`}
          >
            {quickActions.map((action, index) => (
              <button
                key={index}
                className="quick-action"
                onClick={() => sendMessageText(action)}
              >
                {action}
              </button>
            ))}
          </div>

          <form onSubmit={sendMessage} className="chat-input-form">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              className="chat-input"
              disabled={isTyping}
            />
            <button
              type="submit"
              className="send-button"
              disabled={isTyping || !inputMessage.trim()}
            >
              ➤
            </button>
          </form>
        </div>
      )}
    </>
  );
}
