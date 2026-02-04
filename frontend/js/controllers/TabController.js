const TAB_TITLES = {
  tasks: "Tareas",
  projects: "Proyectos",
  comments: "Comentarios",
  history: "Historial",
  notifications: "Notificaciones",
  search: "Búsqueda",
  reports: "Reportes",
};

const TabController = {
  init() {
    document.querySelectorAll(".tab-button").forEach((btn) => {
      btn.addEventListener("click", (e) => this.showTab(e.currentTarget.dataset.tab, e));
    });
  },

  showTab(tabName, event) {
    document.querySelectorAll(".tab-content").forEach((tab) => tab.classList.add("hidden"));
    document.querySelectorAll(".tab-button").forEach((btn) => btn.classList.remove("active"));
    const content = document.getElementById(tabName + "Tab");
    const btn = document.querySelector(`.tab-button[data-tab="${tabName}"]`);
    if (content) content.classList.remove("hidden");
    if (btn) btn.classList.add("active");

    const titleEl = document.getElementById("currentSectionTitle");
    if (titleEl && TAB_TITLES[tabName]) titleEl.textContent = TAB_TITLES[tabName];

    if (tabName === "tasks") window.App.onTabTasks();
    else if (tabName === "projects") window.App.onTabProjects();
  },
};
