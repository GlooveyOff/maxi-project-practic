const BASE = import.meta.env.VITE_API_BASE || "/api";

function token() {
  return localStorage.getItem("token");
}

async function request(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth && token()) headers.Authorization = `Bearer ${token()}`;

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || `Ошибка ${res.status}`);
  }
  return data;
}

export const api = {
  login: (email, password) => request("/auth/login", { method: "POST", body: { email, password } }),
  register: (payload) => request("/auth/register", { method: "POST", body: payload }),
  me: () => request("/auth/me", { auth: true }),

  fields: {
    list: (q) => request(`/fields${q ? `?q=${encodeURIComponent(q)}` : ""}`),
    get: (id) => request(`/fields/${id}`),
    create: (data) => request("/fields", { method: "POST", body: data, auth: true }),
    update: (id, data) => request(`/fields/${id}`, { method: "PUT", body: data, auth: true }),
    remove: (id) => request(`/fields/${id}`, { method: "DELETE", auth: true }),
  },

  wells: {
    list: (params = {}) => {
      const q = new URLSearchParams(params).toString();
      return request(`/wells${q ? `?${q}` : ""}`);
    },
    create: (data) => request("/wells", { method: "POST", body: data, auth: true }),
    update: (id, data) => request(`/wells/${id}`, { method: "PUT", body: data, auth: true }),
    remove: (id) => request(`/wells/${id}`, { method: "DELETE", auth: true }),
  },

  requests: {
    list: (params = {}) => {
      const q = new URLSearchParams(params).toString();
      return request(`/requests${q ? `?${q}` : ""}`, { auth: true });
    },
    create: (data) => request("/requests", { method: "POST", body: data, auth: true }),
    patch: (id, data) => request(`/requests/${id}`, { method: "PATCH", body: data, auth: true }),
    remove: (id) => request(`/requests/${id}`, { method: "DELETE", auth: true }),
  },
};
