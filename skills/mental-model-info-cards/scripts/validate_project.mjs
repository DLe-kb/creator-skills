#!/usr/bin/env node
import { existsSync, readFileSync, statSync } from "node:fs";
import { resolve } from "node:path";
import vm from "node:vm";

const projectRoot = resolve(process.argv[2] ?? ".");
const toolRoot = existsSync(resolve(projectRoot, "tool-v1"))
  ? resolve(projectRoot, "tool-v1")
  : projectRoot;
const modelsFile = resolve(toolRoot, "data", "models.js");
const captionsFile = resolve(toolRoot, "data", "captions.md");
const outputRoot = resolve(toolRoot, "..", "output");
const expectedTypes = ["cover", "definition", "mechanism", "scenarios", "case", "boundary"];
const diagramKinds = new Set(["flow", "cycle", "balance", "matrix"]);

function fail(message) {
  console.error(`ERROR: ${message}`);
  process.exitCode = 1;
}

if (!existsSync(modelsFile)) {
  throw new Error(`Missing ${modelsFile}`);
}

const sandbox = { window: {} };
vm.createContext(sandbox);
vm.runInContext(readFileSync(modelsFile, "utf8"), sandbox);
const models = sandbox.window.cardModels;

if (!models || typeof models !== "object" || Object.keys(models).length === 0) {
  throw new Error("window.cardModels must contain at least one model");
}

const ids = new Set();
const slugs = new Set();
const captions = existsSync(captionsFile) ? readFileSync(captionsFile, "utf8") : "";

for (const [key, model] of Object.entries(models)) {
  const required = ["id", "slug", "name", "english", "category", "accent", "tags", "cards"];
  for (const field of required) {
    if (!model[field] || (Array.isArray(model[field]) && model[field].length === 0)) {
      fail(`${key} is missing ${field}`);
    }
  }

  if (key !== model.slug) fail(`${key}: object key must match slug ${model.slug}`);
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(model.slug)) fail(`${key}: invalid slug`);
  if (!/^M\d{3,}$/.test(model.id)) fail(`${key}: id must look like M001`);
  if (!/^#[0-9A-Fa-f]{6}$/.test(model.accent)) fail(`${key}: invalid accent color`);
  if (ids.has(model.id)) fail(`${key}: duplicate id ${model.id}`);
  if (slugs.has(model.slug)) fail(`${key}: duplicate slug ${model.slug}`);
  ids.add(model.id);
  slugs.add(model.slug);

  if (!Array.isArray(model.cards) || model.cards.length !== 6) {
    fail(`${key}: expected exactly 6 cards`);
    continue;
  }

  const actualTypes = model.cards.map((card) => card.type);
  if (actualTypes.join(",") !== expectedTypes.join(",")) {
    fail(`${key}: card order must be ${expectedTypes.join(", ")}`);
  }

  const mechanism = model.cards[2];
  if (!mechanism.diagram || !diagramKinds.has(mechanism.diagram.kind)) {
    fail(`${key}: mechanism diagram kind must be flow, cycle, balance, or matrix`);
  }

  if (!captions.includes(`## ${model.id}`)) fail(`${key}: caption heading for ${model.id} not found`);

  const outputDir = resolve(outputRoot, `${model.id}-${model.name}`);
  if (existsSync(outputDir)) {
    const names = ["01-cover.png", "02-definition.png", "03-mechanism.png", "04-prompt.png", "05-case.png", "06-further.png"];
    for (const name of names) {
      const file = resolve(outputDir, name);
      if (!existsSync(file) || statSync(file).size === 0) fail(`${key}: incomplete output ${name}`);
    }
  }
}

if (process.exitCode) process.exit(process.exitCode);
console.log(`Validated ${Object.keys(models).length} model(s) in ${projectRoot}`);
