/* T2/S1 — persistent, accessible theme toggle for SolveSheep. */
(function () {
  "use strict";

  var STORAGE_KEY = "ss-theme";
  var root = document.documentElement;
  var button = document.getElementById("theme-toggle");
  if (!button) return;

  function osPrefersDark() {
    return window.matchMedia("(prefers-color-scheme: dark)");
  }

  function savedChoice() {
    try {
      var value = window.localStorage.getItem(STORAGE_KEY);
      return value === "light" || value === "dark" ? value : null;
    } catch (error) {
      return null;
    }
  }

  function currentTheme() {
    return root.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    root.setAttribute("data-bs-theme", theme);
  }

  /* Accurate accessible name and pressed state: pressed = dark active. */
  function updateButton() {
    var theme = currentTheme();
    var next = theme === "dark" ? "light" : "dark";
    var label = "Switch to " + next + " theme";
    button.setAttribute("aria-pressed", String(theme === "dark"));
    button.setAttribute("aria-label", label);
    button.textContent = theme === "dark" ? "Light mode" : "Dark mode";
  }

  button.addEventListener("click", function () {
    var next = currentTheme() === "dark" ? "light" : "dark";
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch (error) {
      /* Private/blocked storage: still apply for this visit. */
    }
    applyTheme(next);
    updateButton();
  });

  /* Unsaved choices keep following the OS preference. */
  var osMedia = osPrefersDark();
  if (typeof osMedia.addEventListener === "function") {
    osMedia.addEventListener("change", function (event) {
      if (savedChoice()) return;
      applyTheme(event.matches ? "dark" : "light");
      updateButton();
    });
  }

  updateButton();
})();
