import { useApp } from "@store/AppContext";
import { chatAPI } from "@api/finance";

export function useChatAPI() {
  const { state, setToast } = useApp();
  const userId = state.user?.id || 1;

  const sendMessage = async (message) => {
    try {
      const response = await chatAPI({ message, user_id: userId });
      // If an action was auto-executed by the backend, broadcast so UI can refresh
      if (response?.executed) {
        // Friendly toast message
        const actionType = response?.action?.action || "action";
        const actionMsgMap = {
          add_transaction: "Transaction added",
          add_budget: "Budget saved",
          update_budget: "Budget updated",
          add_goal: "Goal created",
          update_goal: "Goal updated",
          add_recurring: "Recurring item added",
        };
        const msg = actionMsgMap[actionType] || `Executed: ${actionType}`;
        setToast({ message: msg, type: "success" });
        window.dispatchEvent(
          new CustomEvent("finance:data-updated", {
            detail: {
              entity: response?.action?.action || "chat",
              action: "execute",
            },
          })
        );
      }
      return response.response;
    } catch (error) {
      console.error("Error sending message:", error);
      return "I'm having trouble connecting right now. Please try again later.";
    }
  };

  return { sendMessage };
}
