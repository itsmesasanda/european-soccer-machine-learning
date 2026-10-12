"use strict";

const fs = require("fs");
const path = require("path");

const spaceRoot = process.argv[2];
require(path.join(spaceRoot, "app.js"));
const modelData = JSON.parse(
  fs.readFileSync(path.join(spaceRoot, "model_data.json"), "utf8"),
);
globalThis.TeamProfiler.setModelData(modelData);

const input = JSON.parse(fs.readFileSync(0, "utf8"));
const predictions = input.rows.map((row, index) =>
  globalThis.TeamProfiler.predictTeam(row, index + 2),
);
const csvResults = globalThis.TeamProfiler.analyseCsvText(input.csv);

function errorFor(csvText) {
  try {
    globalThis.TeamProfiler.analyseCsvText(csvText);
    return null;
  } catch (error) {
    return error.message;
  }
}

const validHeaders = ["team_name", ...globalThis.TeamProfiler.REQUIRED_COLUMNS];
const validValues = [
  "Test FC",
  ...globalThis.TeamProfiler.REQUIRED_COLUMNS.map(() => "50"),
];
const nonNumericValues = [...validValues];
nonNumericValues[validHeaders.indexOf("avg_pace")] = "invalid";
const outOfRangeValues = [...validValues];
outOfRangeValues[validHeaders.indexOf("avg_attack")] = "101";
const missingValueValues = [...validValues];
missingValueValues[validHeaders.indexOf("avg_defence")] = "";

const validationErrors = {
  empty: errorFor(""),
  noRows: errorFor(validHeaders.join(",")),
  missingColumns: errorFor("team_name,avg_overall_rating\nTest FC,50"),
  nonNumeric: errorFor(
    `${validHeaders.join(",")}\n${nonNumericValues.join(",")}`,
  ),
  outOfRange: errorFor(
    `${validHeaders.join(",")}\n${outOfRangeValues.join(",")}`,
  ),
  missingValue: errorFor(
    `${validHeaders.join(",")}\n${missingValueValues.join(",")}`,
  ),
};

process.stdout.write(
  JSON.stringify({ predictions, csvResults, validationErrors }),
);
