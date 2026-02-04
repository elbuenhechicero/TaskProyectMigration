const NotificationView = {
  render(notifications) {
    const area = document.getElementById("notificationsArea");
    if (!notifications || notifications.length === 0) {
      area.value = "No hay notificaciones nuevas.";
      return;
    }
    let text = "=== NOTIFICACIONES ===\n\n";
    notifications.forEach((n) => {
      text += `• [${n.type || ""}] ${escapeHtml(n.message || "")} (${n.createdAt || ""})\n`;
    });
    area.value = text;
  },
};
