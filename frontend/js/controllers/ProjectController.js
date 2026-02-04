const ProjectController = {
  init() {
    document.getElementById("projectForm").addEventListener("submit", (e) => {
      e.preventDefault();
      this.addProject();
    });
    document.querySelector("#projectForm button[name='update']").addEventListener("click", () => this.updateProject());
    document.querySelector("#projectForm button[name='delete']").addEventListener("click", () => this.deleteProject());
    document.getElementById("projectsTableBody").addEventListener("click", (e) => {
      const tr = e.target.closest("tr[data-project-id]");
      if (tr) this.selectProject(parseInt(tr.dataset.projectId, 10));
    });
  },

  async loadProjects() {
    try {
      const projects = await ProjectService.getAll();
      ProjectView.renderProjects(projects, window.App.selectedProjectId);
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },

  async addProject() {
    const data = ProjectView.getFormData();
    if (!data.name) {
      Toast.show("El nombre es requerido", "error");
      return;
    }
    try {
      await ProjectService.create(data);
      ProjectView.clearForm();
      window.App.selectedProjectId = null;
      await this.loadProjects();
      if (window.App.refreshProjectSelects) window.App.refreshProjectSelects();
      Toast.show("Proyecto agregado", "success");
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },

  async updateProject() {
    const id = window.App.selectedProjectId;
    if (!id) {
      Toast.show("Selecciona un proyecto de la tabla", "error");
      return;
    }
    const data = ProjectView.getFormData();
    if (!data.name) {
      Toast.show("El nombre es requerido", "error");
      return;
    }
    try {
      await ProjectService.update(id, data);
      ProjectView.clearForm();
      window.App.selectedProjectId = null;
      await this.loadProjects();
      if (window.App.refreshProjectSelects) window.App.refreshProjectSelects();
      Toast.show("Proyecto actualizado", "success");
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },

  async deleteProject() {
    const id = window.App.selectedProjectId;
    if (!id) {
      Toast.show("Selecciona un proyecto de la tabla", "error");
      return;
    }
    if (!confirm("¿Eliminar este proyecto?")) return;
    try {
      await ProjectService.delete(id);
      ProjectView.clearForm();
      window.App.selectedProjectId = null;
      await this.loadProjects();
      if (window.App.refreshProjectSelects) window.App.refreshProjectSelects();
      Toast.show("Proyecto eliminado", "success");
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },

  selectProject(id) {
    window.App.selectedProjectId = id;
    ProjectService.getAll().then((projects) => {
      const p = projects.find((x) => x.id === id);
      if (p) ProjectView.fillForm(p);
      ProjectView.highlightRow(id);
    });
  },
};
