import { spawnSync } from "node:child_process";
import { copyFileSync, cpSync, existsSync, mkdirSync, readFileSync, rmSync, statSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath, pathToFileURL } from "node:url";
import vm from "node:vm";

const toolRoot = dirname(fileURLToPath(import.meta.url));
const browserCandidates = [
  process.env.CARDS_BROWSER,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
].filter(Boolean);
const chrome = browserCandidates.find((candidate) => existsSync(candidate));
if (!chrome) throw new Error("No supported browser found. Set CARDS_BROWSER to a Chrome-compatible browser path.");

const outputRoot = resolve(toolRoot, "..", "output");
const renderRoot = resolve(tmpdir(), `knowledge-cards-render-${Date.now()}`);
cpSync(toolRoot, renderRoot, { recursive: true, filter: (source) => !source.includes("/.DS_Store") });
const htmlUrl = pathToFileURL(resolve(renderRoot, "index.html")).href;

const sandbox = { window: {} };
vm.createContext(sandbox);
vm.runInContext(readFileSync(resolve(toolRoot, "data", "models.js"), "utf8"), sandbox);
const selectedModels = new Set((process.env.CARDS_MODELS ?? "").split(",").map((item) => item.trim()).filter(Boolean));
const pageNames = { cover: "cover", definition: "definition", mechanism: "mechanism", scenarios: "prompt", case: "case", boundary: "further" };

function expectedFiles(model) {
  return model.cards.map((card, index) => resolve(outputRoot, `${model.id}-${model.name}`, `${String(index + 1).padStart(2, "0")}-${pageNames[card.type]}.png`));
}

function isComplete(model) {
  return expectedFiles(model).every((file) => existsSync(file) && statSync(file).size > 0);
}

function sleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

try {
  for (const [modelKey, model] of Object.entries(sandbox.window.cardModels).sort(([, a], [, b]) => a.id.localeCompare(b.id))) {
    if (selectedModels.size > 0 && !selectedModels.has(modelKey) && !selectedModels.has(model.id) && !selectedModels.has(`${model.id}-${model.name}`)) continue;
    if (model.cards.length !== 6) throw new Error(`${model.id}-${model.name} must contain exactly 6 cards.`);
    if (process.env.CARDS_FORCE !== "1" && isComplete(model)) {
      console.log(`Skipping ${model.id}-${model.name}: output already complete.`);
      continue;
    }

    const outDir = resolve(outputRoot, `${model.id}-${model.name}`);
    mkdirSync(outDir, { recursive: true });

    for (let card = 1; card <= model.cards.length; card += 1) {
      const out = resolve(outDir, `${String(card).padStart(2, "0")}-${pageNames[model.cards[card - 1].type]}.png`);
      const url = `${htmlUrl}?model=${modelKey}&card=${card}`;
      let saved = false;

      for (let attempt = 1; attempt <= 3 && !saved; attempt += 1) {
        const profile = resolve(tmpdir(), `knowledge-cards-profile-${Date.now()}-${attempt}`);
        const shot = resolve(tmpdir(), `knowledge-card-${Date.now()}-${attempt}.png`);
        const result = spawnSync(chrome, ["--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--disable-extensions", "--disable-background-networking", "--disable-features=PaintHolding", "--no-first-run", "--no-default-browser-check", "--run-all-compositor-stages-before-draw", "--hide-scrollbars", "--force-device-scale-factor=1", "--window-size=1080,1440", `--user-data-dir=${profile}`, `--screenshot=${shot}`, url], { stdio: "inherit", timeout: 8000, killSignal: "SIGKILL" });
        if (existsSync(shot) && statSync(shot).size > 0) {
          copyFileSync(shot, out);
          console.log(`Saved -> ${out}`);
          saved = true;
        } else if (attempt === 3) {
          throw new Error(`Chrome did not create ${out}; exit status ${result.status}.`);
        }
        rmSync(shot, { force: true });
        rmSync(profile, { recursive: true, force: true });
        sleep(250);
      }
    }
  }
} finally {
  rmSync(renderRoot, { recursive: true, force: true });
}
