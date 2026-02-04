const TaskController = {
  init() {
    document.getElementById("taskForm").addEventListener("submit", (e) => {
      e.preventDefault();
      this.addTask();
    });
    document.querySelector("#taskForm button[name='update']").addEventListener("click", () => this.updateTask());
    document.querySelector("#taskForm button[name='delete']").addEventListener("click", () => this.deleteTask());
    document.querySelector("#taskForm button[name='clear']").addEventListener("click", () => this.clearForm());
    document.getElementById("tasksTableBody").addEventListener("click", (e) => {
      const tr = e.target.closest("tr[data-task-id]");
      if (tr) this.selectTask(parseInt(tr.dataset.taskId, 10));
    });
  },

  async loadTasks() {
    try {
      const [tasks, projects, users, stats] = await Promise.all([
        TaskService.getAll(),
        ProjectService.getAll(),
        AuthService.getUsers(),
        TaskService.getStats(),
      ]);
      TaskView.fillProjectSelect(projects);
      TaskView.fillUserSelect(users);
      TaskView.renderTasks(tasks, window.App.selectedTaskId);
      TaskView.setStats(stats);
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },

  async addTask() {
    const data = TaskView.getFormData();
    if (!data.title) {
      Toast.show("El título es requerido", "error");
      return;
    }
    try {
      await TaskService.create(data);
      TaskView.clearForm();
      window.App.selectedTaskId = null;
      await this.loadTasks();
      Toast.show("Tarea agregada", "success");
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },

  async updateTask() {
    const id = window.App.selectedTaskId;
    if (!id) {
      Toast.show("Selecciona una tarea", "error");
      return;
    }
    const data = TaskView.getFormData();
    if (!data.title) {
      Toast.show("El título es requerido", "error");
      return;
    }
    try {
      await TaskService.update(id, data);
      TaskView.clearForm();
      window.App.selectedTaskId = null;
      await this.loadTasks();
      Toast.show("Tarea actualizada", "success");
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },

  async deleteTask() {
    const id = window.App.selectedTaskId;
    if (!id) {
      Toast.show("Selecciona una tarea", "error");
      return;
    }
    if (!confirm("¿Eliminar esta tarea?")) return;
    try {
      await TaskService.delete(id);
      TaskView.clearForm();
      window.App.selectedTaskId = null;
      await this.loadTasks();
      Toast.show("Tarea eliminada", "success");
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },

  selectTask(id) {
    window.App.selectedTaskId = id;
    TaskService.getById(id).then((task) => {
      TaskView.fillForm(task);
      TaskView.highlightRow(id);
    }).catch(() => Toast.show("Error al cargar tarea", "error"));
  },

  clearForm() {
    window.App.selectedTaskId = null;
    TaskView.clearForm();
    TaskView.highlightRow(null);
  },
};
