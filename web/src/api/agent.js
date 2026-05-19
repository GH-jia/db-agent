import { requestJson } from "./http";

export function listDbConnections() {
  return requestJson("/db-connections?page=1&page_size=100&status=active");
}

export function chatWithAgent({ sessionId, message, connectionId, userId = null }) {
  return requestJson("/agent/chat", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      message,
      connection_id: connectionId,
      user_id: userId,
    }),
  });
}
