// Live search, column sort, and row expand for CRM tables.
document.addEventListener("DOMContentLoaded", () => {
  // --- live search ---
  const search = document.querySelector("[data-table-search]");
  if (search) {
    const table = document.querySelector(search.dataset.tableSearch);
    const count = document.querySelector("[data-row-count]");
    const update = () => {
      const q = search.value.toLowerCase();
      let visible = 0;
      table.querySelectorAll("tbody tr:not(.detail-row)").forEach((tr) => {
        const show = tr.textContent.toLowerCase().includes(q);
        tr.style.display = show ? "" : "none";
        const det = tr.nextElementSibling;
        if (det && det.classList.contains("detail-row")) det.style.display = "none";
        if (show) visible++;
      });
      if (count) count.textContent = visible + " shown";
    };
    search.addEventListener("input", update);
    update();
  }

  // --- column sort (click header) ---
  document.querySelectorAll("table.crm th.sortable").forEach((th) => {
    th.addEventListener("click", () => {
      const table = th.closest("table");
      const tbody = table.querySelector("tbody");
      const idx = [...th.parentNode.children].indexOf(th);
      const dir = th.dataset.dir === "asc" ? -1 : 1;
      th.dataset.dir = dir === 1 ? "asc" : "desc";
      const rows = [...tbody.querySelectorAll("tr:not(.detail-row)")];
      const pairs = rows.map((r) => {
        const det = r.nextElementSibling;
        return [r, det && det.classList.contains("detail-row") ? det : null];
      });
      pairs.sort((a, b) => {
        const av = a[0].children[idx]?.textContent.trim() || "";
        const bv = b[0].children[idx]?.textContent.trim() || "";
        const an = parseFloat(av), bn = parseFloat(bv);
        if (!isNaN(an) && !isNaN(bn)) return (an - bn) * dir;
        return av.localeCompare(bv) * dir;
      });
      pairs.forEach(([r, d]) => { tbody.appendChild(r); if (d) tbody.appendChild(d); });
    });
  });

  // --- expand detail rows ---
  document.querySelectorAll(".expand-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const det = btn.closest("tr").nextElementSibling;
      if (det) det.style.display = det.style.display === "table-row" ? "none" : "table-row";
    });
  });
});
