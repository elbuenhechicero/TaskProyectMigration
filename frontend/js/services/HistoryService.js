const HistoryService = {
  async getByTaskId(taskId) {
    return ApiService.get(`/history?taskId=${taskId}`);
  },

  async getAll() {
    return ApiService.get("/history");
  },
};
