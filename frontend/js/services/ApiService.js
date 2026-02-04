const ApiService = {
  getToken() {
    return localStorage.getItem("token");
  },

  setToken(token) {
    if (token) localStorage.setItem("token", token);
    else localStorage.removeItem("token");
  },

  async request(path, options = {}) {
    const url = `${Config.API_BASE_URL}${path}`;
    const headers = {
      "Content-Type": "application/json",
      ...options.headers,
    };
    const token = this.getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(url, { ...options, headers });
    const data = await res.json().catch(() => ({}));

    if (res.status === 401) {
      this.setToken(null);
      if (typeof window.App !== "undefined" && window.App.onUnauthorized) {
        window.App.onUnauthorized();
      }
      throw new Error("Sesión expirada");
    }

    if (!res.ok) {
      throw new Error(data.error || `Error ${res.status}`);
    }
    return data;
  },

  get(path) {
    return this.request(path, { method: "GET" });
  },

  post(path, body) {
    return this.request(path, { method: "POST", body: JSON.stringify(body || {}) });
  },

  put(path, body) {
    return this.request(path, { method: "PUT", body: JSON.stringify(body || {}) });
  },

  delete(path) {
    return this.request(path, { method: "DELETE" });
  },
};
