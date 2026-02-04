const CommentService = {
  async getByTaskId(taskId) {
    return ApiService.get(`/comments?taskId=${taskId}`);
  },

  async add(taskId, commentText) {
    return ApiService.post("/comments", { taskId, commentText });
  },
};
