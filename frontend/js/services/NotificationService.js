const NotificationService = {
  async getUnread() {
    return ApiService.get("/notifications?unread=true");
  },

  async markRead() {
    return ApiService.post("/notifications/read");
  },
};
