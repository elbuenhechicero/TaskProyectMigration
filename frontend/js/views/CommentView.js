const CommentView = {
  renderComments(comments) {
    const area = document.getElementById("commentsArea");
    if (!comments || comments.length === 0) {
      area.value = "No hay comentarios para esta tarea.";
      return;
    }
    const taskId = comments[0] && comments[0].taskId;
    let text = `=== COMENTARIOS TAREA #${taskId} ===\n\n`;
    comments.forEach((c) => {
      text += `[${c.createdAt || ""}] ${escapeHtml(c.username || "Usuario")}: ${escapeHtml(c.commentText || "")}\n---\n`;
    });
    area.value = text;
  },

  setNoTask() {
    document.getElementById("commentsArea").value = "Selecciona una tarea para ver comentarios.";
  },

  fillTaskSelect(tasks) {
    const sel = document.getElementById("commentTaskId");
    sel.innerHTML = '<option value="">Seleccionar tarea</option>';
    (tasks || []).forEach((t) => {
      const opt = document.createElement("option");
      opt.value = t.id;
      opt.textContent = `#${t.id} - ${escapeHtml(t.title || "")}`;
      sel.appendChild(opt);
    });
  },

  getTaskId() {
    return parseInt(document.getElementById("commentTaskId").value, 10) || null;
  },

  getCommentText() {
    return document.getElementById("commentText").value.trim();
  },

  clearCommentText() {
    document.getElementById("commentText").value = "";
  },
};
