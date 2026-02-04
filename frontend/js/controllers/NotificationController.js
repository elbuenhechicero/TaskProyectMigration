const NotificationController = {
  init() {
    document.getElementById("loadNotificationsBtn").addEventListener("click", () => this.loadNotifications());
    document.getElementById("markNotificationsReadBtn").addEventListener("click", () => this.markRead());
  },

  async loadNotifications() {
    try {
      const list = await NotificationService.getUnread();
      NotificationView.render(list);
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },

  async markRead() {
    try {
      await NotificationService.markRead();
      await this.loadNotifications();
      Toast.show("Notificaciones marcadas como leídas", "success");
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },
};
