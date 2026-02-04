const ReportService = {
  async getReport(type) {
    return ApiService.get(`/reports/${type}`);
  },

  getExportCsvUrl() {
    const token = ApiService.getToken();
    return `${Config.API_BASE_URL}/reports/export/csv?token=${encodeURIComponent(token)}`;
  },

  async downloadCsv() {
    const token = ApiService.getToken();
    const res = await fetch(`${Config.API_BASE_URL}/reports/export/csv`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Error al exportar");
    const blob = await res.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "export_tasks.csv";
    a.click();
    URL.revokeObjectURL(a.href);
  },
};
