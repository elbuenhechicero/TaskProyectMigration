const ProjectService = {
  async getAll() {
    return ApiService.get("/projects");
  },

  async create(project) {
    return ApiService.post("/projects", project);
  },

  async update(id, project) {
    return ApiService.put(`/projects/${id}`, project);
  },

  async delete(id) {
    return ApiService.delete(`/projects/${id}`);
  },
};
