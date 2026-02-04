const AuthController = {
  init() {
    document.getElementById("loginForm").addEventListener("submit", (e) => {
      e.preventDefault();
      this.login();
    });
    document.getElementById("logoutBtn").addEventListener("click", () => this.logout());
  },

  async login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
      Toast.show("Usuario y contraseña requeridos", "error");
      return;
    }

    try {
      const user = await AuthService.login(username, password);
      LoginView.setCurrentUser(user.username);
      LoginView.hide();
      window.App.currentUser = user;
      window.App.onLogin();
    } catch (err) {
      Toast.show(err.message || "Credenciales inválidas", "error");
    }
  },

  logout() {
    AuthService.logout();
    window.App.currentUser = null;
    window.App.selectedTaskId = null;
    window.App.selectedProjectId = null;
    LoginView.show();
    if (window.App.onLogout) window.App.onLogout();
  },
};
