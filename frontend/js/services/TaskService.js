const TaskService = {
  async getAll() {
    return ApiService.get("/tasks");
  },

  async getStats() {
    return ApiService.get("/tasks/stats");
  },

  async getById(id) {
    return ApiService.get(`/tasks/${id}`);
  },

  async create(task) {
    return ApiService.post("/tasks", task);
  },

  async update(id, task) {
    return ApiService.put(`/tasks/${id}`, task);
  },

  async delete(id) {
    return ApiService.delete(`/tasks/${id}`);
  },

  async search(filters) {
    return ApiService.post("/tasks/search", filters);
  },
};
