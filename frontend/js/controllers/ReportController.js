const ReportController = {
  init() {
    document.querySelectorAll("[data-report]").forEach((btn) => {
      btn.addEventListener("click", (e) => this.generateReport(e.currentTarget.dataset.report));
    });
    document.getElementById("exportCsvBtn").addEventListener("click", () => this.exportCsv());
  },

  async generateReport(type) {
    try {
      const data = await ReportService.getReport(type);
      ReportView.renderReport(data.report);
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },

  async exportCsv() {
    try {
      await ReportService.downloadCsv();
      Toast.show("Exportado a export_tasks.csv", "success");
    } catch (err) {
      Toast.show(err.message, "error");
    }
  },
};
