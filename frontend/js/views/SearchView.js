const SearchView = {
  renderResults(tasks) {
    const tbody = document.getElementById("searchTableBody");
    tbody.innerHTML = "";
    (tasks || []).forEach((t) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${escapeHtml(String(t.id))}</td>
        <td>${escapeHtml(t.title || "")}</td>
        <td>${escapeHtml(t.status || "Pendiente")}</td>
        <td>${escapeHtml(t.priority || "Media")}</td>
        <td>${escapeHtml(t.projectName || "Sin proyecto")}</td>
      `;
      tbody.appendChild(tr);
    });
  },

  fillProjectSelect(projects) {
    const sel = document.getElementById("searchProject");
    sel.innerHTML = '<option value="0">Todos</option>';
    (projects || []).forEach((p) => {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = escapeHtml(p.name);
      sel.appendChild(opt);
    });
  },

  getFilters() {
    return {
      text: document.getElementById("searchText").value.trim().toLowerCase(),
      status: document.getElementById("searchStatus").value,
      priority: document.getElementById("searchPriority").value,
      projectId: parseInt(document.getElementById("searchProject").value, 10) || 0,
    };
  },
};
