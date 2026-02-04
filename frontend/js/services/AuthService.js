const AuthService = {
  async login(username, password) {
    const data = await ApiService.post("/auth/login", { username, password });
    ApiService.setToken(data.token);
    return data.user;
  },

  logout() {
    ApiService.setToken(null);
  },

  isLoggedIn() {
    return !!ApiService.getToken();
  },

  async getMe() {
    return ApiService.get("/auth/me");
  },

  async getUsers() {
    return ApiService.get("/auth/users");
  },
};
