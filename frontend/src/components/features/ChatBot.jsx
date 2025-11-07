import { useState, useRef, useEffect } from "react";
import { useChatAPI } from "../../api/apis";
import DOMPurify from "dompurify";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
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
  const [copiedCode, setCopiedCode] = useState(null);
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

  // Copy code to clipboard
  const copyToClipboard = (code, id) => {
    navigator.clipboard.writeText(code).then(() => {
      setCopiedCode(id);
      setTimeout(() => setCopiedCode(null), 2000);
    });
  };

  // Render message content with proper HTML sanitization and code highlighting
  const renderMessageContent = (message) => {
    if (!message.text) return null;

    if (message.isHtml) {
      // Sanitize HTML to prevent XSS attacks
      const sanitizedHtml = DOMPurify.sanitize(message.text, {
        ALLOWED_TAGS: [
          "p",
          "br",
          "strong",
          "em",
          "u",
          "h1",
          "h2",
          "h3",
          "h4",
          "h5",
          "h6",
          "ul",
          "ol",
          "li",
          "a",
          "code",
          "pre",
          "blockquote",
          "span",
          "div",
        ],
        ALLOWED_ATTR: ["href", "target", "rel", "class"],
      });

      // Check if contains code blocks
      const codeBlockRegex = /<pre><code[^>]*>([\s\S]*?)<\/code><\/pre>/g;
      const hasCodeBlocks = codeBlockRegex.test(sanitizedHtml);

      if (hasCodeBlocks) {
        // Parse and render code blocks with syntax highlighting
        const parts = [];
        let lastIndex = 0;
        const regex = /<pre><code[^>]*>([\s\S]*?)<\/code><\/pre>/g;
        let match;

        while ((match = regex.exec(message.text)) !== null) {
          // Add text before code block
          if (match.index > lastIndex) {
            const textBefore = message.text.substring(lastIndex, match.index);
            parts.push(
              <div
                key={`text-${lastIndex}`}
                dangerouslySetInnerHTML={{
                  __html: DOMPurify.sanitize(textBefore),
                }}
              />
            );
          }

          // Add code block with copy button
          const code = match[1].replace(/<[^>]*>/g, ""); // Strip HTML tags from code
          const codeId = `${message.id}-${match.index}`;
          parts.push(
            <div key={`code-${match.index}`} className="code-block-wrapper">
              <div className="code-block-header">
                <span className="code-label">Code</span>
                <button
                  className="copy-code-btn"
                  onClick={() => copyToClipboard(code, codeId)}
                  aria-label="Copy code to clipboard"
                >
                  {copiedCode === codeId ? (
                    <>
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
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                      <span>Copied!</span>
                    </>
                  ) : (
                    <>
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
                          d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                        />
                      </svg>
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
              <SyntaxHighlighter
                language="javascript"
                style={vscDarkPlus}
                customStyle={{
                  margin: 0,
                  borderRadius: "0 0 8px 8px",
                  fontSize: "13px",
                }}
              >
                {code}
              </SyntaxHighlighter>
            </div>
          );

          lastIndex = match.index + match[0].length;
        }

        // Add remaining text after last code block
        if (lastIndex < message.text.length) {
          const textAfter = message.text.substring(lastIndex);
          parts.push(
            <div
              key={`text-${lastIndex}`}
              dangerouslySetInnerHTML={{
                __html: DOMPurify.sanitize(textAfter),
              }}
            />
          );
        }

        return <div className="html-content">{parts}</div>;
      }

      // No code blocks, just render sanitized HTML
      return (
        <div
          className="html-content"
          dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
        />
      );
    }

    // Plain text message
    return <p>{message.text}</p>;
  };

  const quickActions = [
    { text: "How can I manage my budget?", icon: "💰" },
    { text: "Help me track transactions", icon: "📊" },
    { text: "Set up financial goals", icon: "🎯" },
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
                  {renderMessageContent(message)}
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
                onClick={() => sendMessageText(action.text)}
                aria-label={action.text}
              >
                <span className="quick-action-icon">{action.icon}</span>
                <span className="quick-action-text">{action.text}</span>
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
