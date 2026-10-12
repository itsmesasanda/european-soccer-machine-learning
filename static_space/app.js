"use strict";

const REQUIRED_COLUMNS = Object.freeze([
  "avg_overall_rating",
  "avg_potential",
  "goalkeeper_rating",
  "avg_pace",
  "avg_physical",
  "avg_defence",
  "avg_attack",
  "buildUpPlaySpeed",
  "buildUpPlayPassing",
  "chanceCreationPassing",
  "chanceCreationCrossing",
  "chanceCreationShooting",
  "defencePressure",
  "defenceAggression",
  "defenceTeamWidth",
]);

const EXPECTED_FEATURES = Object.freeze([
  "avg_overall_rating",
  "development_gap",
  "goalkeeper_relative_strength",
  "avg_pace",
  "avg_physical",
  "avg_defence",
  "attack_defence_balance",
  "buildUpPlaySpeed",
  "buildUpPlayPassing",
  "chanceCreationPassing",
  "chanceCreationCrossing",
  "chanceCreationShooting",
  "defencePressure",
  "defenceAggression",
  "defenceTeamWidth",
]);

const MAX_CSV_BYTES = 5 * 1024 * 1024;
let modelData = null;
let currentBatchResults = [];
let currentDownloadUrl = null;

function arraysEqual(left, right) {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}

function setModelData(data) {
  if (!data || data.format_version !== 1) throw new Error("Unsupported model data format.");
  if (!Array.isArray(data.features) || !arraysEqual(data.features, EXPECTED_FEATURES)) {
    throw new Error("The model feature order is invalid.");
  }

  const means = data.scaler?.mean;
  const scales = data.scaler?.scale;
  const centres = data.kmeans?.cluster_centers;
  if (!Array.isArray(means) || means.length !== EXPECTED_FEATURES.length || !means.every(Number.isFinite)) {
    throw new Error("The scaler means are invalid.");
  }
  if (!Array.isArray(scales) || scales.length !== EXPECTED_FEATURES.length || !scales.every((value) => Number.isFinite(value) && value > 0)) {
    throw new Error("The scaler scales are invalid.");
  }
  if (!Array.isArray(centres) || centres.length !== 5 || !centres.every((row) => Array.isArray(row) && row.length === EXPECTED_FEATURES.length && row.every(Number.isFinite))) {
    throw new Error("The K-Means centroids are invalid.");
  }
  for (let cluster = 0; cluster < 5; cluster += 1) {
    if (typeof data.profile_names?.[String(cluster)] !== "string") throw new Error("The profile mapping is invalid.");
  }
  modelData = data;
}

function normaliseRawTeam(rawTeam, rowNumber = null) {
  const team = {};
  const prefix = rowNumber === null ? "" : `Row ${rowNumber}: `;

  for (const column of REQUIRED_COLUMNS) {
    const rawValue = rawTeam[column];
    if (rawValue === undefined || rawValue === null || String(rawValue).trim() === "") {
      throw new Error(`${prefix}missing numeric value in ${column}.`);
    }
    const numericValue = Number(rawValue);
    if (!Number.isFinite(numericValue)) {
      throw new Error(`${prefix}non-numeric value in ${column}.`);
    }
    if (numericValue < 0 || numericValue > 100) {
      throw new Error(`${prefix}${column} must be between 0 and 100.`);
    }
    team[column] = numericValue;
  }

  const suppliedName = rawTeam.team_name === undefined || rawTeam.team_name === null
    ? ""
    : String(rawTeam.team_name).trim();
  team.team_name = suppliedName || (rowNumber === null ? "Team 1" : `Team ${rowNumber - 1}`);
  return team;
}

function predictTeam(rawTeam, rowNumber = null) {
  if (!modelData) throw new Error("Model parameters have not loaded yet.");
  const team = normaliseRawTeam(rawTeam, rowNumber);

  const engineered = {
    ...team,
    development_gap: team.avg_potential - team.avg_overall_rating,
    goalkeeper_relative_strength: team.goalkeeper_rating - team.avg_overall_rating,
    attack_defence_balance: team.avg_attack - team.avg_defence,
  };

  const standardized = modelData.features.map((feature, index) => (
    (engineered[feature] - modelData.scaler.mean[index]) / modelData.scaler.scale[index]
  ));

  let assignedCluster = -1;
  let closestDistance = Number.POSITIVE_INFINITY;
  modelData.kmeans.cluster_centers.forEach((centroid, cluster) => {
    const squaredDistance = standardized.reduce((sum, value, index) => {
      const difference = value - centroid[index];
      return sum + difference * difference;
    }, 0);
    const distance = Math.sqrt(squaredDistance);
    if (distance < closestDistance) {
      closestDistance = distance;
      assignedCluster = cluster;
    }
  });

  return {
    team_name: team.team_name,
    cluster: assignedCluster,
    team_profile: modelData.profile_names[String(assignedCluster)],
    distance_to_centroid: Number(closestDistance.toFixed(3)),
    description: modelData.profile_descriptions[String(assignedCluster)],
  };
}

function parseCSV(text) {
  if (typeof text !== "string" || text.trim() === "") throw new Error("The uploaded CSV file is empty.");

  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];
    if (inQuotes) {
      if (character === '"' && text[index + 1] === '"') {
        field += '"';
        index += 1;
      } else if (character === '"') {
        inQuotes = false;
      } else {
        field += character;
      }
    } else if (character === '"') {
      if (field !== "") throw new Error("The CSV contains an unexpected quote.");
      inQuotes = true;
    } else if (character === ",") {
      row.push(field);
      field = "";
    } else if (character === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else if (character !== "\r") {
      field += character;
    }
  }

  if (inQuotes) throw new Error("The CSV contains an unclosed quoted value.");
  row.push(field);
  rows.push(row);

  return rows.filter((candidate) => candidate.some((value) => value.trim() !== ""));
}

function analyseCsvText(text) {
  const rows = parseCSV(text);
  if (rows.length === 0) throw new Error("The uploaded CSV file is empty.");

  const headers = rows[0].map((header, index) => {
    const cleaned = index === 0 ? header.replace(/^\uFEFF/, "") : header;
    return cleaned.trim();
  });
  const duplicateHeaders = headers.filter((header, index) => header && headers.indexOf(header) !== index);
  if (duplicateHeaders.length) throw new Error(`Duplicate CSV columns: ${[...new Set(duplicateHeaders)].join(", ")}.`);

  const missingColumns = REQUIRED_COLUMNS.filter((column) => !headers.includes(column));
  if (missingColumns.length) throw new Error(`Missing required columns: ${missingColumns.join(", ")}.`);
  if (rows.length === 1) throw new Error("The uploaded CSV contains no team data rows.");

  return rows.slice(1).map((values, index) => {
    const rawTeam = {};
    headers.forEach((header, columnIndex) => { if (header) rawTeam[header] = values[columnIndex]; });
    return predictTeam(rawTeam, index + 2);
  });
}

function clearError(element) {
  element.textContent = "";
  element.hidden = true;
}

function showError(element, message) {
  element.textContent = message;
  element.hidden = false;
}

function csvCell(value) {
  let text = String(value ?? "");
  if (/^[=+\-@]/.test(text)) text = `'${text}`;
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function renderBatchTable(results) {
  const body = document.querySelector("#results-body");
  body.replaceChildren();
  results.forEach((result) => {
    const tableRow = document.createElement("tr");
    [result.team_name, result.cluster, result.team_profile, result.distance_to_centroid.toFixed(3)].forEach((value, index) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      if (index === 1) cell.className = "cluster-cell";
      tableRow.appendChild(cell);
    });
    body.appendChild(tableRow);
  });
}

function downloadBatchResults() {
  if (!currentBatchResults.length) return;
  const columns = ["team_name", "cluster", "team_profile", "distance_to_centroid"];
  const lines = [
    columns.join(","),
    ...currentBatchResults.map((row) => columns.map((column) => csvCell(row[column])).join(",")),
  ];
  if (currentDownloadUrl) URL.revokeObjectURL(currentDownloadUrl);
  currentDownloadUrl = URL.createObjectURL(new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = currentDownloadUrl;
  link.download = "analysed_team_profiles.csv";
  link.click();
}

function initialiseTabs() {
  const tabs = document.querySelectorAll(".tab-button");
  const panels = document.querySelectorAll(".tab-panel");
  tabs.forEach((tab) => tab.addEventListener("click", () => {
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
  }));
}

function initialiseMetricInputs() {
  document.querySelectorAll(".metric").forEach((metric) => {
    const slider = metric.querySelector('input[type="range"]');
    const number = metric.querySelector('input[type="number"]');
    slider.addEventListener("input", () => { number.value = slider.value; });
    number.addEventListener("input", () => {
      if (number.value !== "" && Number(number.value) >= 0 && Number(number.value) <= 100) slider.value = number.value;
    });
  });
}

function initialiseSingleForm() {
  const form = document.querySelector("#team-form");
  const errorBox = document.querySelector("#single-error");
  const resultCard = document.querySelector("#result-card");
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    clearError(errorBox);
    try {
      const rawTeam = { team_name: form.elements.team_name.value };
      REQUIRED_COLUMNS.forEach((column) => { rawTeam[column] = form.elements[column].value; });
      const result = predictTeam(rawTeam);
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
    }
  });
}

function setSelectedFile(file) {
  const input = document.querySelector("#csv-file");
  const label = document.querySelector("#file-label");
  if (!file) {
    label.textContent = "Choose a CSV file";
    return;
  }
  const transfer = new DataTransfer();
  transfer.items.add(file);
  input.files = transfer.files;
  label.textContent = file.name;
}

function initialiseCsvForm() {
  const form = document.querySelector("#csv-form");
  const input = document.querySelector("#csv-file");
  const drop = document.querySelector("#file-drop");
  const errorBox = document.querySelector("#csv-error");
  const resultsSection = document.querySelector("#batch-results");

  input.addEventListener("change", () => setSelectedFile(input.files[0]));
  ["dragenter", "dragover"].forEach((eventName) => drop.addEventListener(eventName, (event) => {
    event.preventDefault();
    drop.classList.add("dragging");
  }));
  ["dragleave", "drop"].forEach((eventName) => drop.addEventListener(eventName, (event) => {
    event.preventDefault();
    drop.classList.remove("dragging");
  }));
  drop.addEventListener("drop", (event) => setSelectedFile(event.dataTransfer.files[0]));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearError(errorBox);
    resultsSection.hidden = true;
    const file = input.files[0];
    if (!file) {
      showError(errorBox, "Choose a CSV file before starting the analysis.");
      return;
    }
    if (!file.name.toLowerCase().endsWith(".csv")) {
      showError(errorBox, "Please choose a file with a .csv extension.");
      return;
    }
    if (file.size === 0) {
      showError(errorBox, "The uploaded CSV file is empty.");
      return;
    }
    if (file.size > MAX_CSV_BYTES) {
      showError(errorBox, "The CSV is larger than the 5 MB browser-processing limit.");
      return;
    }

    try {
      currentBatchResults = analyseCsvText(await file.text());
      renderBatchTable(currentBatchResults);
      document.querySelector("#batch-count").textContent = `${currentBatchResults.length} team${currentBatchResults.length === 1 ? "" : "s"} profiled`;
      resultsSection.hidden = false;
      resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
      showError(errorBox, error.message);
    }
  });

  document.querySelector("#download-results").addEventListener("click", downloadBatchResults);
}

async function initialiseBrowserApp() {
  initialiseTabs();
  initialiseMetricInputs();
  initialiseSingleForm();
  initialiseCsvForm();
  const columns = document.querySelector("#required-columns");
  REQUIRED_COLUMNS.forEach((column) => {
    const code = document.createElement("code");
    code.textContent = column;
    columns.appendChild(code);
  });

  const status = document.querySelector("#model-status");
  try {
    const response = await fetch("model_data.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    setModelData(await response.json());
    status.querySelector("span:last-child").textContent = "Model parameters loaded · inference ready";
    status.querySelector(".status-dot").classList.remove("loading");
    document.querySelector("#analyse-button").disabled = false;
    document.querySelector("#csv-button").disabled = false;
  } catch (error) {
    status.querySelector("span:last-child").textContent = "Model parameters could not be loaded";
    status.querySelector(".status-dot").classList.remove("loading");
    status.querySelector(".status-dot").classList.add("error");
    showError(document.querySelector("#single-error"), "The model data could not be loaded. Refresh the page or verify model_data.json is present.");
  }
}

globalThis.TeamProfiler = Object.freeze({
  REQUIRED_COLUMNS,
  EXPECTED_FEATURES,
  setModelData,
  predictTeam,
  parseCSV,
  analyseCsvText,
});

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", initialiseBrowserApp);
}
