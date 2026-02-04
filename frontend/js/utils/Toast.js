const Toast = {
  container: null,

  init() {
    if (this.container) return;
    this.container = document.createElement("div");
    this.container.className = "fixed bottom-4 right-4 z-50 flex flex-col gap-2";
    this.container.setAttribute("aria-live", "polite");
    document.body.appendChild(this.container);
  },

  show(message, type = "info") {
    this.init();
    const styles = {
      success: "bg-teal-600 text-white shadow-lg shadow-teal-900/20",
      error: "bg-rose-500 text-white shadow-lg shadow-rose-900/20",
      info: "bg-slate-700 text-white shadow-lg shadow-slate-900/20",
    };
    const el = document.createElement("div");
    el.className = `px-5 py-3 rounded-xl font-medium text-sm ${styles[type] || styles.info}`;
    el.textContent = message;
    this.container.appendChild(el);
    setTimeout(() => {
      el.remove();
    }, 3200);
  },
};
