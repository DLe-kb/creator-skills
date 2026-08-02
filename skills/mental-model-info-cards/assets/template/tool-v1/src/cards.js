const models = window.cardModels;
const theme = window.cardTheme ?? {};

function xml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function marker(accent) {
  return `
    <defs>
      <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
        <path d="M2,2 L10,6 L2,10" fill="none" stroke="${accent}" stroke-width="2.4" />
      </marker>
    </defs>
  `;
}

function flowDiagram(config, accent) {
  const nodes = config.nodes.slice(0, 4);
  const width = 196;
  const gap = (928 - nodes.length * width) / (nodes.length + 1);
  const y = 225;
  const boxes = nodes.map((node, index) => {
    const x = gap + index * (width + gap);
    const arrow = index === nodes.length - 1 ? "" : `
      <line x1="${x + width}" y1="${y + 72}" x2="${x + width + gap - 12}" y2="${y + 72}" stroke="${accent}" stroke-width="5" marker-end="url(#arrow)" />
    `;
    return `
      <rect x="${x}" y="${y}" width="${width}" height="144" fill="none" stroke="${index === nodes.length - 1 ? accent : "#151515"}" stroke-width="${index === nodes.length - 1 ? 4 : 2}" />
      <text x="${x + width / 2}" y="${y + 82}" text-anchor="middle" class="svg-text" font-size="27">${xml(node)}</text>
      ${arrow}
    `;
  }).join("");
  return `<svg viewBox="0 0 928 710" role="img" aria-label="流程图">${marker(accent)}${boxes}<text x="464" y="500" text-anchor="middle" class="svg-muted" font-size="26">${xml(config.note ?? "")}</text></svg>`;
}

function cycleDiagram(config, accent) {
  const nodes = config.nodes.slice(0, 4);
  const positions = [[364, 52], [650, 275], [364, 498], [78, 275]];
  const boxes = nodes.map((node, index) => {
    const [x, y] = positions[index];
    return `<rect x="${x}" y="${y}" width="200" height="112" fill="none" stroke="${index === 0 ? accent : "#151515"}" stroke-width="3" /><text x="${x + 100}" y="${y + 66}" text-anchor="middle" class="svg-text" font-size="26">${xml(node)}</text>`;
  }).join("");
  return `<svg viewBox="0 0 928 710" role="img" aria-label="循环图">${marker(accent)}${boxes}<path d="M570 108 C730 120 790 210 760 275" fill="none" stroke="${accent}" stroke-width="5" marker-end="url(#arrow)"/><path d="M750 390 C720 530 630 570 570 554" fill="none" stroke="${accent}" stroke-width="5" marker-end="url(#arrow)"/><path d="M358 554 C210 550 150 470 168 390" fill="none" stroke="${accent}" stroke-width="5" marker-end="url(#arrow)"/><path d="M168 275 C190 140 290 100 358 108" fill="none" stroke="${accent}" stroke-width="5" marker-end="url(#arrow)"/><text x="464" y="360" text-anchor="middle" class="svg-muted" font-size="26">${xml(config.note ?? "反馈循环")}</text></svg>`;
}

function balanceDiagram(config, accent) {
  const left = config.left ?? "变量 A";
  const right = config.right ?? "变量 B";
  return `<svg viewBox="0 0 928 710" role="img" aria-label="平衡图"><line x1="464" y1="170" x2="464" y2="520" stroke="#151515" stroke-width="6"/><line x1="200" y1="300" x2="728" y2="300" stroke="${accent}" stroke-width="10"/><circle cx="464" cy="300" r="28" fill="${accent}"/><rect x="80" y="350" width="270" height="150" fill="none" stroke="#151515" stroke-width="3"/><rect x="578" y="350" width="270" height="150" fill="none" stroke="#151515" stroke-width="3"/><text x="215" y="438" text-anchor="middle" class="svg-text" font-size="30">${xml(left)}</text><text x="713" y="438" text-anchor="middle" class="svg-text" font-size="30">${xml(right)}</text><text x="464" y="600" text-anchor="middle" class="svg-muted" font-size="26">${xml(config.note ?? "识别取舍与平衡")}</text></svg>`;
}

function matrixDiagram(config, accent) {
  const quadrants = (config.quadrants ?? ["A", "B", "C", "D"]).slice(0, 4);
  const positions = [[110, 100], [484, 100], [110, 370], [484, 370]];
  const boxes = quadrants.map((label, index) => {
    const [x, y] = positions[index];
    return `<rect x="${x}" y="${y}" width="334" height="220" fill="none" stroke="${index === 1 ? accent : "#151515"}" stroke-width="${index === 1 ? 4 : 2}"/><text x="${x + 167}" y="${y + 120}" text-anchor="middle" class="svg-text" font-size="29">${xml(label)}</text>`;
  }).join("");
  return `<svg viewBox="0 0 928 710" role="img" aria-label="四象限图">${boxes}<text x="464" y="660" text-anchor="middle" class="svg-muted" font-size="24">${xml(config.xLabel ?? "横轴")} × ${xml(config.yLabel ?? "纵轴")}</text></svg>`;
}

function diagram(config, accent) {
  if (config.kind === "cycle") return cycleDiagram(config, accent);
  if (config.kind === "balance") return balanceDiagram(config, accent);
  if (config.kind === "matrix") return matrixDiagram(config, accent);
  return flowDiagram(config, accent);
}

function header(model, card, index, total) {
  return `<div class="meta"><div class="meta-left"><span class="pill accent">${model.id}</span><span>${model.english}</span></div><div class="meta-right"><span class="pill">${model.category}</span><span>${String(index + 1).padStart(2, "0")} / ${String(total).padStart(2, "0")}</span></div></div><div class="section-label">${card.label}</div>`;
}

function footer(model, index, total) {
  return `<footer class="footer"><div class="tagline">${model.tags.map((tag) => `<span class="tag">${tag}</span>`).join("")}</div><div class="footer-center">${theme.brand ?? "Knowledge Cards"}</div><div class="footer-right">${String(index + 1).padStart(2, "0")} of ${String(total).padStart(2, "0")}</div></footer>`;
}

function renderCard(model, card, index) {
  const total = model.cards.length;
  let content = "";

  if (card.type === "cover") content = `<section class="content"><div class="eyebrow">${card.label}</div><h1 class="title">${card.title}</h1><h2 class="title en">${card.titleEn}</h2><p class="subtitle">${card.subtitle}</p><div class="big-number">${model.id.replace(/^M/, "")}</div></section>`;
  if (card.type === "definition") content = `<section class="content definition"><div class="eyebrow">${card.label}</div><div class="statement">${card.statement}</div><p class="note">${card.note}</p><div class="compact-grid">${card.facts.map(([kicker, text]) => `<div class="fact-box"><div class="fact-kicker">${kicker}</div><div class="fact-text">${text}</div></div>`).join("")}</div></section>`;
  if (card.type === "mechanism") content = `<section class="content diagram-wrap"><div><div class="eyebrow">${card.label}</div><h2 class="diagram-title">${card.title}</h2></div><div class="diagram">${diagram(card.diagram, model.accent)}</div></section>`;
  if (card.type === "scenarios") content = `<section class="content"><div class="eyebrow">${card.label}</div><h2 class="diagram-title">${card.title}</h2><div class="scenario-grid">${card.items.map(([num, title, copy, rule]) => `<article class="scenario"><div class="scenario-num">${num}</div><div class="scenario-title">${title}</div><div class="scenario-copy">${copy}</div><div class="mini-rule">${rule}</div></article>`).join("")}</div></section>`;
  if (card.type === "case") content = `<section class="content"><div class="eyebrow">${card.label}</div><h2 class="diagram-title">${card.title}</h2><div class="case-layout"><div class="case-hero"><div class="case-title">${card.caseTitle}</div><div class="case-copy">${card.caseCopy}</div></div><div class="case-steps">${card.steps.map(([num, title, copy]) => `<div class="case-step"><div class="case-step-num">${num}</div><div class="case-step-title">${title}</div><div class="case-step-copy">${copy}</div></div>`).join("")}</div><div class="warning">${card.takeaway}</div></div></section>`;
  if (card.type === "boundary") content = `<section class="content boundary"><div class="eyebrow">${card.label}</div><h2 class="diagram-title">${card.title}</h2><div><div class="warning">${card.warning}</div><p class="note">${card.note}</p></div><div class="reading-list">${card.readings.map(([item, note], i) => `<div class="reading-item"><div class="reading-num">${String(i + 1).padStart(2, "0")}</div><div class="reading-title">${item}<span class="reading-note">${note}</span></div></div>`).join("")}<div class="thinking-box"><div class="thinking-label">行动建议</div><div class="thinking-text">${card.thinking}</div></div></div></section>`;

  return `<article class="card" style="--accent: ${model.accent}">${header(model, card, index, total)}${content}${footer(model, index, total)}</article>`;
}

function render() {
  const params = new URLSearchParams(window.location.search);
  const modelKey = params.get("model");
  const cardParam = params.get("card");
  const app = document.querySelector("#app");
  document.documentElement.style.setProperty("--paper", theme.paper ?? "#EFEDE4");

  if (modelKey && cardParam) {
    const model = models[modelKey];
    const index = Number(cardParam) - 1;
    if (!model || !model.cards[index]) {
      app.textContent = "Model or card not found.";
      return;
    }
    document.body.classList.add("export");
    app.innerHTML = `<div class="board">${renderCard(model, model.cards[index], index)}</div>`;
    return;
  }

  const cards = Object.values(models).sort((a, b) => a.id.localeCompare(b.id)).flatMap((model) => model.cards.map((card, index) => renderCard(model, card, index))).join("");
  app.innerHTML = `<div class="board">${cards}</div>`;
}

render();
