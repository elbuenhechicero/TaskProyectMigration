/**
 * Carga los fragmentos HTML de cada vista y los inyecta en el DOM.
 * Las rutas son relativas a la página que carga los scripts (p. ej. index.html).
 */
const ViewLoader = {
  /** Ruta base para las vistas (cambiar si la app se sirve desde un subdirectorio) */
  basePath: "views",

  async fetchView(name) {
    const url = `${this.basePath}/${name}.html`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`No se pudo cargar la vista: ${name}`);
    return res.text();
  },

  /**
   * Carga todas las vistas y las inyecta en sus contenedores.
   * Debe ejecutarse antes de inicializar controladores.
   */
  async loadAll() {
    const loginPanel = document.getElementById("loginPanel");
    const loginWrapper = loginPanel ? loginPanel.querySelector(".login-panel-wrapper") : null;
    const tabContainer = document.getElementById("tabContentContainer");

    if (!loginPanel || !tabContainer) {
      console.error("ViewLoader: faltan #loginPanel o #tabContentContainer en el DOM");
      return;
    }

    const [loginHtml, tasksHtml, projectsHtml, commentsHtml, historyHtml, notificationsHtml, searchHtml, reportsHtml] =
      await Promise.all([
        this.fetchView("login"),
        this.fetchView("tasks"),
        this.fetchView("projects"),
        this.fetchView("comments"),
        this.fetchView("history"),
        this.fetchView("notifications"),
        this.fetchView("search"),
        this.fetchView("reports"),
      ]);

    if (loginWrapper) loginWrapper.innerHTML = loginHtml;
    else loginPanel.innerHTML = loginHtml;

    tabContainer.innerHTML =
      tasksHtml +
      projectsHtml +
      commentsHtml +
      historyHtml +
      notificationsHtml +
      searchHtml +
      reportsHtml;
  },
};
