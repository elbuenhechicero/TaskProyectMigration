/**
 * Escapa HTML para evitar XSS al mostrar datos de usuario.
 */
function escapeHtml(text) {
  if (text == null || text === "") return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
