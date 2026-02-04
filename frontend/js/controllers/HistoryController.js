const HistoryController = {
  init() {
    document.getElementById("loadHistoryBtn").addEventListener("click", () => this.loadHistory());
  },

  async refreshTaskSelect() {
    try {
      const tasks = await TaskService.getAll();
      HistoryView.fillTaskSelect(tasks);
    } catch (_) {}
  },

  async loadHistory() {
    const taskId = HistoryView.getTaskId();
    try {
      const entries = taskId
        ? await HistoryService.getByTaskId(taskId)
        : await HistoryService.getAll();
      HistoryView.renderHistory(entries, taskId);
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },
};
