/* Progressive enhancement for jonchun.github.io.
   Two jobs: the mobile nav toggle, and an optional "recently updated"
   repository list fetched live from the GitHub API. Everything on the
   site works with this file absent or blocked. */

(function () {
  "use strict";

  /* ---- Mobile navigation toggle ---------------------------------------- */

  function initNav() {
    var toggle = document.querySelector(".nav-toggle");
    var nav = document.getElementById("site-nav");
    if (!toggle || !nav) return;

    function setOpen(open) {
      nav.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    }

    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });

    // Escape closes the menu and returns focus to the button.
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });

    // Reset state when the viewport grows past the mobile breakpoint so the
    // desktop nav is never left in a stale "open" class.
    var wide = window.matchMedia("(min-width: 48rem)");
    var onChange = function (event) {
      if (event.matches) setOpen(false);
    };
    if (typeof wide.addEventListener === "function") {
      wide.addEventListener("change", onChange);
    }
  }

  /* ---- Recently updated repositories ----------------------------------- */

  var API =
    "https://api.github.com/users/jon-chun/repos?sort=pushed&per_page=8";

  function formatDate(iso) {
    var date = new Date(iso);
    if (isNaN(date.getTime())) return "";
    return date.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric"
    });
  }

  function renderRepos(mount, repos) {
    var list = document.createElement("ul");
    list.className = "repo-list";

    repos.forEach(function (repo) {
      if (!repo || !repo.html_url || !repo.name) return;

      var item = document.createElement("li");

      var link = document.createElement("a");
      link.href = repo.html_url;
      link.rel = "noopener";
      link.textContent = repo.name;
      item.appendChild(link);

      if (repo.description) {
        var desc = document.createElement("span");
        desc.className = "repo-desc";
        desc.textContent = repo.description;
        item.appendChild(desc);
      }

      var bits = [];
      if (repo.language) bits.push(repo.language);
      if (repo.stargazers_count) {
        bits.push(
          repo.stargazers_count +
            (repo.stargazers_count === 1 ? " star" : " stars")
        );
      }
      if (repo.pushed_at) {
        var when = formatDate(repo.pushed_at);
        if (when) bits.push("updated " + when);
      }
      if (bits.length) {
        var meta = document.createElement("span");
        meta.className = "repo-meta";
        meta.textContent = bits.join(" · ");
        item.appendChild(meta);
      }

      list.appendChild(item);
    });

    if (!list.childNodes.length) return;

    // Only reveal the section once there is something real to show.
    mount.textContent = "";
    mount.appendChild(list);
    var section = mount.closest("[data-recent-section]");
    if (section) section.hidden = false;
  }

  function initRecentRepos() {
    var mount = document.getElementById("recent-repos");
    if (!mount || typeof window.fetch !== "function") return;

    fetch(API, { headers: { Accept: "application/vnd.github+json" } })
      .then(function (response) {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.json();
      })
      .then(function (repos) {
        if (Array.isArray(repos) && repos.length) renderRepos(mount, repos);
      })
      .catch(function () {
        /* Rate limited, offline or blocked: leave the page as served. */
      });
  }

  function init() {
    initNav();
    initRecentRepos();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
