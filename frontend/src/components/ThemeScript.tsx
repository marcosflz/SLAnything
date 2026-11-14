export function ThemeScript() {
  // Sin elección guardada se respeta la preferencia del sistema.
  const script = `
(function () {
  try {
    var saved = localStorage.getItem("aula-theme");
    var dark = saved ? saved === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    document.documentElement.classList.toggle(
      "sidebar-collapsed",
      localStorage.getItem("aula-sidebar-collapsed") === "1"
    );
  } catch (e) {}
})();
`;
  return <script dangerouslySetInnerHTML={{ __html: script }} />;
}
