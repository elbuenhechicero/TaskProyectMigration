const SearchController = {
  init() {
    document.getElementById("searchBtn").addEventListener("click", () => this.search());
    this.refreshProjectSelect();
  },

  async refreshProjectSelect() {
    try {
      const projects = await ProjectService.getAll();
      SearchView.fillProjectSelect(projects);
    } catch (_) {}
  },

  async search() {
    const filters = SearchView.getFilters();
    const body = {
      text: filters.text || undefined,
      status: filters.status || undefined,
      priority: filters.priority || undefined,
      projectId: filters.projectId || undefined,
    };
    if (body.projectId === 0) delete body.projectId;
    try {
      const tasks = await TaskService.search(body);
      SearchView.renderResults(tasks);
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },
};
