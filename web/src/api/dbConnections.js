import { requestJson } from "./http";

function buildQuery(params) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.set(key, value);
    }
  });
  return query.toString();
}

export function listDbConnections(params = {}) {
  const query = buildQuery({
    page: 1,
    page_size: 20,
    ...params,
  });
  return requestJson(`/db-connections?${query}`);
}

export function createDbConnection(data) {
  return requestJson("/db-connections", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateDbConnection(connectionId, data) {
  return requestJson(`/db-connections/${connectionId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteDbConnection(connectionId) {
  return requestJson(`/db-connections/${connectionId}`, {
    method: "DELETE",
  });
}
