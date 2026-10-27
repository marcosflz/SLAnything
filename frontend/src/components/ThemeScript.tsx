export function ThemeScript() {
  const script = `
(function () {
  try {
    var saved = localStorage.getItem("aula-theme");
    document.documentElement.dataset.theme = saved === "dark" ? "dark" : "light";
    document.documentElement.classList.toggle(
      "sidebar-collapsed",
      localStorage.getItem("aula-sidebar-collapsed") === "1"
    );
  } catch (e) {}
})();
`;
  return <script dangerouslySetInnerHTML={{ __html: script }} />;
}
