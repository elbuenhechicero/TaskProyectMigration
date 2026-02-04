const LoginView = {
  show() {
    document.getElementById("loginPanel").classList.remove("hidden");
    document.getElementById("mainPanel").classList.add("hidden");
  },

  hide() {
    document.getElementById("loginPanel").classList.add("hidden");
    document.getElementById("mainPanel").classList.remove("hidden");
  },

  setCurrentUser(username) {
    const initial = username ? username.charAt(0).toUpperCase() : "?";
    const el = document.getElementById("currentUser");
    const sideName = document.getElementById("sidebarUserName");
    const sideAvatar = document.getElementById("sidebarUserAvatar");
    const topAvatar = document.getElementById("topbarUserAvatar");
    if (el) el.textContent = username;
    if (sideName) sideName.textContent = username;
    if (sideAvatar) sideAvatar.textContent = initial;
    if (topAvatar) topAvatar.textContent = initial;
  },
};
