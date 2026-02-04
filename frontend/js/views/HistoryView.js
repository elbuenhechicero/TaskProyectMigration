const HistoryView = {
  renderHistory(entries, taskId) {
    const area = document.getElementById("historyArea");
    if (!entries || entries.length === 0) {
      area.value = taskId ? `No hay historial para la tarea #${taskId}.` : "No hay historial.";
      return;
    }
    let text = taskId ? `=== HISTORIAL TAREA #${taskId} ===\n\n` : "=== HISTORIAL COMPLETO ===\n\n";
    entries.forEach((e) => {
      text += `${e.timestamp || ""} - ${e.action || ""}\n`;
      text += `  Usuario: ${escapeHtml(e.username || "Desconocido")}\n`;
      text += `  Antes: ${escapeHtml(e.oldValue || "(vacío)")}\n`;
      text += `  Después: ${escapeHtml(e.newValue || "(vacío)")}\n---\n`;
    });
    area.value = text;
  },

  fillTaskSelect(tasks) {
    const sel = document.getElementById("historyTaskId");
    const first = sel.querySelector('option[value=""]');
    sel.innerHTML = "";
    if (first) sel.appendChild(first);
    (tasks || []).forEach((t) => {
      const opt = document.createElement("option");
      opt.value = t.id;
      opt.textContent = `#${t.id} - ${escapeHtml(t.title || "")}`;
      sel.appendChild(opt);
    });
  },

  getTaskId() {
    const v = document.getElementById("historyTaskId").value;
    return v === "" ? null : parseInt(v, 10);
  },
};
