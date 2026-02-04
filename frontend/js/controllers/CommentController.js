const CommentController = {
  init() {
    document.getElementById("addCommentBtn").addEventListener("click", () => this.addComment());
    document.getElementById("loadCommentsBtn").addEventListener("click", () => this.loadComments());
  },

  async refreshTaskSelect() {
    try {
      const tasks = await TaskService.getAll();
      CommentView.fillTaskSelect(tasks);
    } catch (_) {}
  },

  async addComment() {
    const taskId = CommentView.getTaskId();
    const text = CommentView.getCommentText();
    if (!taskId) {
      Toast.show("Selecciona una tarea", "error");
      return;
    }
    if (!text) {
      Toast.show("El comentario no puede estar vacío", "error");
      return;
    }
    try {
      await CommentService.add(taskId, text);
      CommentView.clearCommentText();
      await this.loadComments();
      Toast.show("Comentario agregado", "success");
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },

  async loadComments() {
    const taskId = CommentView.getTaskId();
    if (!taskId) {
      CommentView.setNoTask();
      return;
    }
    try {
      const comments = await CommentService.getByTaskId(taskId);
      CommentView.renderComments(comments);
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },
};
