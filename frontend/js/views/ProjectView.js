const ProjectView = {
  renderProjects(projects, selectedProjectId) {
    const tbody = document.getElementById("projectsTableBody");
    tbody.innerHTML = "";
    projects.forEach((p) => {
      const tr = document.createElement("tr");
      tr.className = p.id === selectedProjectId ? "selected" : "";
      tr.dataset.projectId = p.id;
      tr.innerHTML = `
        <td>${escapeHtml(String(p.id))}</td>
        <td>${escapeHtml(p.name || "")}</td>
        <td>${escapeHtml(p.description || "")}</td>
      `;
      tbody.appendChild(tr);
    });
  },

  fillForm(project) {
    document.getElementById("projectName").value = project.name || "";
    document.getElementById("projectDescription").value = project.description || "";
  },

  clearForm() {
    document.getElementById("projectName").value = "";
    document.getElementById("projectDescription").value = "";
  },

  getFormData() {
    return {
      name: document.getElementById("projectName").value.trim(),
      description: document.getElementById("projectDescription").value.trim(),
    };
  },

  highlightRow(projectId) {
    document.querySelectorAll("#projectsTableBody tr").forEach((tr) => {
      tr.classList.toggle("selected", parseInt(tr.dataset.projectId, 10) === projectId);
    });
  },
};
