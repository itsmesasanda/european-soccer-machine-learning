const tabs = document.querySelectorAll(".tab-button");
const panels = document.querySelectorAll(".tab-panel");
const teamForm = document.querySelector("#team-form");
const csvForm = document.querySelector("#csv-form");
const csvFile = document.querySelector("#csv-file");
let batchRows = [];

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((item) => {
      const selected = item === tab;
      item.classList.toggle("active", selected);
      item.setAttribute("aria-selected", String(selected));
    });
    panels.forEach((panel) => {
      const selected = panel.id === tab.dataset.tab;
      panel.classList.toggle("active", selected);
      panel.hidden = !selected;
    });
  });
});

function setLoading(button, loading, loadingText) {
  if (!button.dataset.defaultText) button.dataset.defaultText = button.innerHTML;
  button.disabled = loading;
  button.innerHTML = loading ? `<span class="spinner"></span><span>${loadingText}</span>` : button.dataset.defaultText;
}

function showError(element, message) {
  element.textContent = message;
  element.hidden = false;
}

function clearError(element) {
  element.textContent = "";
  element.hidden = true;
}

async function responseError(response) {
  try {
    const body = await response.json();
    if (Array.isArray(body.errors) && body.errors.length) {
      return body.errors.map((error) => `${error.field}: ${error.message}`).join(" · ");
    }
    if (typeof body.detail === "string") return body.detail;
  } catch (_) {
    // Fall through to a safe generic message.
  }
  return "The request could not be completed. Please check your data and try again.";
}

teamForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const errorBox = document.querySelector("#single-error");
  const button = document.querySelector("#analyse-button");
  const resultCard = document.querySelector("#result-card");
  clearError(errorBox);

  if (!teamForm.reportValidity()) return;

  const formData = new FormData(teamForm);
  const payload = {};
  formData.forEach((value, key) => {
    payload[key] = key === "team_name" ? value.trim() : Number(value);
  });
  if (!payload.team_name) delete payload.team_name;

  setLoading(button, true, "Analysing team…");
  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error(await responseError(response));

    const result = await response.json();
    document.querySelector("#result-team").textContent = result.team_name;
    document.querySelector("#result-profile").textContent = result.team_profile;
    document.querySelector("#result-cluster").textContent = `Cluster ${result.cluster}`;
    document.querySelector("#result-distance").textContent = result.distance_to_centroid.toFixed(3);
    document.querySelector("#result-description").textContent = result.description;
    resultCard.hidden = false;
    resultCard.scrollIntoView({ behavior: "smooth", block: "center" });
  } catch (error) {
    resultCard.hidden = true;
    showError(errorBox, error.message);
  } finally {
    setLoading(button, false, "");
  }
});

csvFile.addEventListener("change", () => {
  document.querySelector("#file-label").textContent = csvFile.files[0]?.name || "Choose a CSV file";
});

const fileDrop = document.querySelector(".file-drop");
["dragenter", "dragover"].forEach((name) => fileDrop.addEventListener(name, (event) => {
  event.preventDefault();
  fileDrop.classList.add("dragging");
}));
["dragleave", "drop"].forEach((name) => fileDrop.addEventListener(name, (event) => {
  event.preventDefault();
  fileDrop.classList.remove("dragging");
}));
fileDrop.addEventListener("drop", (event) => {
  const file = event.dataTransfer.files[0];
  if (file) {
    const transfer = new DataTransfer();
    transfer.items.add(file);
    csvFile.files = transfer.files;
    document.querySelector("#file-label").textContent = file.name;
  }
});

csvForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const errorBox = document.querySelector("#csv-error");
  const button = document.querySelector("#csv-button");
  const resultsSection = document.querySelector("#batch-results");
  clearError(errorBox);

  if (!csvFile.files.length) {
    showError(errorBox, "Choose a CSV file before starting the analysis.");
    return;
  }

  const data = new FormData();
  data.append("file", csvFile.files[0]);
  setLoading(button, true, "Analysing CSV…");

  try {
    const response = await fetch("/predict-csv", { method: "POST", body: data });
    if (!response.ok) throw new Error(await responseError(response));

    const payload = await response.json();
    batchRows = payload.results;
    renderTable(batchRows);
    document.querySelector("#batch-count").textContent = `${payload.count} team${payload.count === 1 ? "" : "s"} profiled`;
    resultsSection.hidden = false;
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    resultsSection.hidden = true;
    showError(errorBox, error.message);
  } finally {
    setLoading(button, false, "");
  }
});

function renderTable(rows) {
  const body = document.querySelector("#results-body");
  body.replaceChildren();
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    [row.team_name, row.cluster, row.team_profile, Number(row.distance_to_centroid).toFixed(3)].forEach((value, index) => {
      const td = document.createElement("td");
      td.textContent = value;
      if (index === 1) td.className = "cluster-cell";
      tr.appendChild(td);
    });
    body.appendChild(tr);
  });
}

function csvCell(value) {
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

document.querySelector("#download-results").addEventListener("click", () => {
  if (!batchRows.length) return;
  const columns = ["team_name", "cluster", "team_profile", "distance_to_centroid", "description"];
  const lines = [columns.join(","), ...batchRows.map((row) => columns.map((column) => csvCell(row[column])).join(","))];
  const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "analysed_team_profiles.csv";
  link.click();
  URL.revokeObjectURL(url);
});
