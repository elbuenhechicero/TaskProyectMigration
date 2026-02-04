window.App = {
  currentUser: null,
  selectedTaskId: null,
  selectedProjectId: null,

  onUnauthorized() {
    this.currentUser = null;
    LoginView.show();
    Toast.show("Sesión expirada. Vuelve a iniciar sesión.", "error");
  },

  onLogin() {
    TaskController.loadTasks();
    TabController.showTab("tasks", { currentTarget: document.querySelector('.tab-button[data-tab="tasks"]') });
    CommentController.refreshTaskSelect();
    HistoryController.refreshTaskSelect();
    SearchController.refreshProjectSelect();
  },

  onLogout() {
    // Opcional: limpiar vistas si se desea
  },

  onTabTasks() {
    TaskController.loadTasks();
  },

  onTabProjects() {
    ProjectController.loadProjects();
  },

  refreshProjectSelects() {
    ProjectService.getAll().then((projects) => {
      TaskView.fillProjectSelect(projects);
      SearchView.fillProjectSelect(projects);
    });
  },

  init() {
    AuthController.init();
    TabController.init();
    TaskController.init();
    ProjectController.init();
    CommentController.init();
    HistoryController.init();
    NotificationController.init();
    SearchController.init();
    ReportController.init();

    if (AuthService.isLoggedIn()) {
      AuthService.getMe()
        .then((user) => {
          window.App.currentUser = user;
          LoginView.setCurrentUser(user.username);
          LoginView.hide();
          window.App.onLogin();
        })
        .catch(() => {
          ApiService.setToken(null);
          LoginView.show();
        });
    } else {
      LoginView.show();
    }
  },
};

document.addEventListener("DOMContentLoaded", async () => {
  try {
    await ViewLoader.loadAll();
    window.App.init();
  } catch (err) {
    console.error("Error cargando vistas:", err);
    document.getElementById("app").innerHTML =
      '<div class="p-8 text-center text-red-600">No se pudieron cargar las vistas. Asegúrate de abrir la app desde un servidor HTTP (no file://).</div>';
  }
});
