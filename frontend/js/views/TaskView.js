const TaskView = {
  renderTasks(tasks, selectedTaskId) {
    const tbody = document.getElementById("tasksTableBody");
    tbody.innerHTML = "";
    tasks.forEach((task) => {
      const tr = document.createElement("tr");
      tr.className = task.id === selectedTaskId ? "selected" : "";
      tr.dataset.taskId = task.id;
      tr.innerHTML = `
        <td>${escapeHtml(String(task.id))}</td>
        <td>${escapeHtml(task.title || "")}</td>
        <td>${escapeHtml(task.status || "Pendiente")}</td>
        <td>${escapeHtml(task.priority || "Media")}</td>
        <td>${escapeHtml(task.projectName || "Sin proyecto")}</td>
        <td>${escapeHtml(task.assignedToName || "Sin asignar")}</td>
        <td>${escapeHtml(task.dueDate || "Sin fecha")}</td>
      `;
      tbody.appendChild(tr);
    });
  },

  setStats(stats) {
    const el = document.getElementById("statsText");
    if (!stats) {
      el.textContent = "";
      return;
    }
    el.textContent = `Total: ${stats.total} | Completadas: ${stats.completed} | Pendientes: ${stats.pending} | Alta prioridad: ${stats.highPriority} | Vencidas: ${stats.overdue}`;
  },

  fillForm(task) {
    document.getElementById("taskTitle").value = task.title || "";
    document.getElementById("taskDescription").value = task.description || "";
    document.getElementById("taskStatus").value = task.status || "Pendiente";
    document.getElementById("taskPriority").value = task.priority || "Media";
    document.getElementById("taskProject").value = task.projectId || "";
    document.getElementById("taskAssigned").value = task.assignedTo || "";
    document.getElementById("taskDueDate").value = task.dueDate ? task.dueDate.slice(0, 10) : "";
    document.getElementById("taskHours").value = task.estimatedHours ?? "";
  },

  clearForm() {
    document.getElementById("taskTitle").value = "";
    document.getElementById("taskDescription").value = "";
    document.getElementById("taskStatus").selectedIndex = 0;
    document.getElementById("taskPriority").selectedIndex = 1;
    document.getElementById("taskProject").selectedIndex = 0;
    document.getElementById("taskAssigned").selectedIndex = 0;
    document.getElementById("taskDueDate").value = "";
    document.getElementById("taskHours").value = "";
  },

  fillProjectSelect(projects) {
    const sel = document.getElementById("taskProject");
    sel.innerHTML = "";
    projects.forEach((p) => {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = escapeHtml(p.name);
      sel.appendChild(opt);
    });
  },

  fillUserSelect(users) {
    const sel = document.getElementById("taskAssigned");
    sel.innerHTML = '<option value="">Sin asignar</option>';
    users.forEach((u) => {
      const opt = document.createElement("option");
      opt.value = u.id;
      opt.textContent = escapeHtml(u.username);
      sel.appendChild(opt);
    });
  },

  getFormData() {
    return {
      title: document.getElementById("taskTitle").value.trim(),
      description: document.getElementById("taskDescription").value.trim(),
      status: document.getElementById("taskStatus").value,
      priority: document.getElementById("taskPriority").value,
      projectId: parseInt(document.getElementById("taskProject").value, 10) || 0,
      assignedTo: parseInt(document.getElementById("taskAssigned").value, 10) || 0,
      dueDate: document.getElementById("taskDueDate").value || "",
      estimatedHours: parseFloat(document.getElementById("taskHours").value) || 0,
    };
  },

  highlightRow(taskId) {
    document.querySelectorAll("#tasksTableBody tr").forEach((tr) => {
      tr.classList.toggle("selected", parseInt(tr.dataset.taskId, 10) === taskId);
    });
  },
};
