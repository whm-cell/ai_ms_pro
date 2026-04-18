const SOURCES = {
  workingContext: "/docs/ai/working-context.md",
  stageStatus: "/docs/ai/status/stage-00-runtime-harness-foundation.md",
  traceability: "/docs/requirements/traceability-matrix.md",
};

const summaryGrid = document.querySelector("#summary-grid");
const queueList = document.querySelector("#queue-list");
const riskList = document.querySelector("#risk-list");
const searchInput = document.querySelector("#search-input");
const stageFilter = document.querySelector("#stage-filter");
const workstreamFilter = document.querySelector("#workstream-filter");
const statusFilter = document.querySelector("#status-filter");
const rowCount = document.querySelector("#row-count");
const matrixGrid = document.querySelector("#matrix-grid");
const detailTitle = document.querySelector("#detail-title");
const detailBody = document.querySelector("#detail-body");
const emptyStateTemplate = document.querySelector("#empty-state-template");

const state = {
  loadState: "loading",
  error: "",
  rows: [],
  workingContext: null,
  stageStatus: null,
  filters: {
    search: "",
    stage: "all",
    workstream: "all",
    status: "all",
  },
  selectedKey: null,
};

boot();

async function boot() {
  document.body.dataset.mode = new URLSearchParams(window.location.search).has("smoke")
    ? "smoke"
    : "default";
  bindControls();
  installTestApi();

  try {
    const [workingContextText, stageStatusText, traceabilityText] = await Promise.all([
      fetchText(SOURCES.workingContext),
      fetchText(SOURCES.stageStatus),
      fetchText(SOURCES.traceability),
    ]);

    state.workingContext = parseWorkingContext(workingContextText);
    state.stageStatus = parseStageStatus(stageStatusText);
    state.rows = parseTraceabilityMatrix(traceabilityText);
    state.loadState = "ready";

    populateFilters();
    render();
  } catch (error) {
    state.loadState = "error";
    state.error = error instanceof Error ? error.message : String(error);
    renderError();
  }
}

function bindControls() {
  searchInput.addEventListener("input", (event) => {
    state.filters.search = event.target.value.trim().toLowerCase();
    render();
  });

  stageFilter.addEventListener("change", (event) => {
    state.filters.stage = event.target.value;
    render();
  });

  workstreamFilter.addEventListener("change", (event) => {
    state.filters.workstream = event.target.value;
    render();
  });

  statusFilter.addEventListener("change", (event) => {
    state.filters.status = event.target.value;
    render();
  });
}

async function fetchText(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${path}: ${response.status}`);
  }
  return response.text();
}

function parseWorkingContext(text) {
  return {
    updatedAt: parseLabelValue(text, "更新时间"),
    stage: parseLabelValue(text, "当前阶段"),
    goals: extractListItems(text, "当前主目标"),
    queue: extractListItems(text, "当前活跃队列"),
    risks: extractListItems(text, "当前风险与阻塞"),
  };
}

function parseStageStatus(text) {
  return {
    updatedAt: parseLabelValue(text, "更新时间"),
    stage: parseLabelValue(text, "阶段"),
    status: parseLabelValue(text, "状态"),
    highlights: extractNestedListItems(text, "本阶段关键成果"),
    nextFocus: extractNestedListItems(text, "下一阶段重点"),
  };
}

function parseTraceabilityMatrix(text) {
  const matrixLines = extractTableLines(text, "矩阵");
  if (matrixLines.length < 3) {
    throw new Error("Traceability matrix did not contain enough rows.");
  }

  const headers = splitTableRow(matrixLines[0]);
  const dataLines = matrixLines.slice(2);
  return dataLines.map((line) => {
    const values = splitTableRow(line);
    const entry = Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""]));
    return {
      sourceDoc: entry["原始文档"] ?? "",
      requirement: entry["标准化需求"] ?? "",
      workstream: entry["工作流"] ?? "",
      stage: entry["开发阶段"] ?? "",
      status: entry["当前状态"] ?? "",
      evidence: entry["验收/测试"] ?? "",
      key: `${entry["工作流"] ?? ""}::${entry["标准化需求"] ?? ""}`,
    };
  });
}

function parseLabelValue(text, label) {
  const expression = new RegExp(`^${escapeRegExp(label)}[：:]\\s*(.+)$`, "m");
  const match = text.match(expression);
  return match ? match[1].trim() : "";
}

function extractListItems(text, heading) {
  return extractSectionLines(text, heading)
    .map((line) => {
      const match = line.match(/^\s*(?:[-*]|\d+\.)\s+(.+)$/);
      return match ? cleanInlineMarkdown(match[1]) : "";
    })
    .filter(Boolean);
}

function extractNestedListItems(text, heading) {
  return extractSectionLines(text, heading)
    .map((line) => {
      const match = line.match(/^\s*(?:[-*]|\d+\.)\s+(.+)$/);
      return match ? cleanInlineMarkdown(match[1]) : "";
    })
    .filter(Boolean);
}

function extractSectionLines(text, heading) {
  const lines = text.split(/\r?\n/);
  const targetHeading = `## ${heading}`;
  const collected = [];
  let capture = false;

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    if (line.startsWith("## ")) {
      if (capture) {
        break;
      }
      capture = line.trim() === targetHeading;
      continue;
    }
    if (capture) {
      collected.push(line);
    }
  }

  return collected;
}

function extractTableLines(text, heading) {
  const lines = text.split(/\r?\n/);
  const targetHeading = `## ${heading}`;
  const collected = [];
  let capture = false;

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (line.startsWith("## ")) {
      if (capture) {
        break;
      }
      capture = line === targetHeading;
      continue;
    }
    if (!capture) {
      continue;
    }
    if (!line) {
      if (collected.length > 0) {
        break;
      }
      continue;
    }
    if (line.startsWith("|")) {
      collected.push(line);
    }
  }

  return collected;
}

function splitTableRow(line) {
  return line
    .split("|")
    .slice(1, -1)
    .map((part) => cleanInlineMarkdown(part.trim()));
}

function cleanInlineMarkdown(value) {
  return value
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, "$1")
    .replace(/`/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function populateFilters() {
  populateSelect(stageFilter, state.rows.map((row) => row.stage), "All stages");
  populateSelect(workstreamFilter, state.rows.map((row) => row.workstream), "All workstreams");
  populateSelect(statusFilter, state.rows.map((row) => row.status), "All statuses");
}

function populateSelect(select, values, allLabel) {
  const uniqueValues = ["all", ...new Set(values.filter(Boolean))];
  select.innerHTML = "";
  uniqueValues.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value === "all" ? allLabel : value;
    select.append(option);
  });
}

function render() {
  renderSummary();
  renderContext();
  renderRows();
}

function renderSummary() {
  const completedCount = state.rows.filter((row) => row.status === "已完成").length;
  const smokeBackedCount = state.rows.filter((row) =>
    /scripts\/|python3|smoke/i.test(row.evidence)
  ).length;
  const workstreamCount = new Set(state.rows.map((row) => row.workstream)).size;

  const cards = [
    {
      label: "Current Stage",
      value: state.workingContext?.stage || "Unknown",
      note: `Status doc: ${state.stageStatus?.status || "unknown"}`,
    },
    {
      label: "Trace Rows",
      value: String(state.rows.length),
      note: "Rows currently published in traceability-matrix.md",
    },
    {
      label: "Completed Rows",
      value: String(completedCount),
      note: "Rows marked complete in the canonical matrix",
    },
    {
      label: "Smoke-backed Rows",
      value: String(smokeBackedCount),
      note: "Rows whose evidence references a repo-level script or smoke flow",
    },
    {
      label: "Workstreams",
      value: String(workstreamCount),
      note: `Updated ${state.workingContext?.updatedAt || "unknown"}`,
    },
  ];

  summaryGrid.innerHTML = "";
  cards.forEach((card) => {
    const article = document.createElement("article");
    article.className = "summary-card";
    article.innerHTML = `
      <p class="summary-label">${escapeHtml(card.label)}</p>
      <p class="summary-value">${escapeHtml(card.value)}</p>
      <p class="summary-note">${escapeHtml(card.note)}</p>
    `;
    summaryGrid.append(article);
  });
}

function renderContext() {
  renderList(queueList, state.workingContext?.queue ?? []);
  renderList(riskList, state.workingContext?.risks ?? []);
}

function renderList(target, items) {
  target.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    target.append(li);
  });
}

function renderRows() {
  const visibleRows = getVisibleRows();
  syncSelection(visibleRows);
  rowCount.textContent = `${visibleRows.length} visible / ${state.rows.length} total`;
  matrixGrid.innerHTML = "";

  if (!visibleRows.length) {
    matrixGrid.append(emptyStateTemplate.content.cloneNode(true));
    detailTitle.textContent = "No row selected";
    detailBody.innerHTML = "";
    return;
  }

  visibleRows.forEach((row) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `matrix-card${row.key === state.selectedKey ? " is-selected" : ""}`;
    button.innerHTML = `
      <div class="card-meta">
        <span class="chip chip-ws">${escapeHtml(row.workstream)}</span>
        <span class="chip chip-stage">${escapeHtml(row.stage)}</span>
        <span class="chip chip-status">${escapeHtml(row.status)}</span>
      </div>
      <h3 class="card-title">${escapeHtml(row.requirement)}</h3>
      <p class="card-evidence">${escapeHtml(row.evidence)}</p>
    `;
    button.addEventListener("click", () => {
      state.selectedKey = row.key;
      renderRows();
    });
    matrixGrid.append(button);
  });

  renderDetail(visibleRows.find((row) => row.key === state.selectedKey) ?? visibleRows[0]);
}

function renderDetail(row) {
  detailTitle.textContent = row.requirement;
  detailBody.innerHTML = `
    <ul class="detail-list">
      <li>
        <span class="detail-label">Source Requirement</span>
        <strong>${escapeHtml(row.sourceDoc)}</strong>
      </li>
      <li>
        <span class="detail-label">Workstream</span>
        <strong>${escapeHtml(row.workstream)}</strong>
      </li>
      <li>
        <span class="detail-label">Stage</span>
        <strong>${escapeHtml(row.stage)}</strong>
      </li>
      <li>
        <span class="detail-label">Canonical Status</span>
        <strong>${escapeHtml(row.status)}</strong>
      </li>
      <li>
        <span class="detail-label">Evidence</span>
        <span>${escapeHtml(row.evidence)}</span>
      </li>
    </ul>
    <div class="source-links">
      <a class="source-link" href="${SOURCES.traceability}">Open traceability matrix</a>
      <a class="source-link" href="${SOURCES.workingContext}">Open working context</a>
      <a class="source-link" href="${SOURCES.stageStatus}">Open stage status</a>
    </div>
  `;
}

function syncSelection(visibleRows) {
  if (!visibleRows.some((row) => row.key === state.selectedKey)) {
    state.selectedKey = visibleRows[0]?.key ?? null;
  }
}

function getVisibleRows() {
  return state.rows.filter((row) => {
    if (state.filters.stage !== "all" && row.stage !== state.filters.stage) {
      return false;
    }
    if (state.filters.workstream !== "all" && row.workstream !== state.filters.workstream) {
      return false;
    }
    if (state.filters.status !== "all" && row.status !== state.filters.status) {
      return false;
    }
    if (!state.filters.search) {
      return true;
    }
    const haystack = [row.sourceDoc, row.requirement, row.workstream, row.stage, row.status, row.evidence]
      .join(" ")
      .toLowerCase();
    return haystack.includes(state.filters.search);
  });
}

function renderError() {
  summaryGrid.innerHTML = "";
  queueList.innerHTML = "";
  riskList.innerHTML = "";
  matrixGrid.innerHTML = `<div class="empty-state"><p>${escapeHtml(state.error)}</p></div>`;
  rowCount.textContent = "0 visible / 0 total";
  detailTitle.textContent = "Load failed";
  detailBody.innerHTML = "";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function installTestApi() {
  window.__HARNESS_TRACE_CONSOLE_TEST__ = {
    getSnapshot() {
      const visibleRows = getVisibleRows();
      const completedCount = state.rows.filter((row) => row.status === "已完成").length;
      const smokeBackedCount = state.rows.filter((row) =>
        /scripts\/|python3|smoke/i.test(row.evidence)
      ).length;
      return {
        loadState: state.loadState,
        stage: state.workingContext?.stage ?? "",
        stageStatus: state.stageStatus?.status ?? "",
        totalRows: state.rows.length,
        rowCount: visibleRows.length,
        workstreams: [...new Set(state.rows.map((row) => row.workstream))],
        visibleRequirements: visibleRows.map((row) => row.requirement),
        selectedRequirement:
          visibleRows.find((row) => row.key === state.selectedKey)?.requirement ?? null,
        summary: {
          completedCount,
          smokeBackedCount,
          workstreamCount: new Set(state.rows.map((row) => row.workstream)).size,
        },
      };
    },
    setWorkstreamFilter(value) {
      workstreamFilter.value = value;
      state.filters.workstream = value;
      render();
      return this.getSnapshot();
    },
    setStageFilter(value) {
      stageFilter.value = value;
      state.filters.stage = value;
      render();
      return this.getSnapshot();
    },
    setStatusFilter(value) {
      statusFilter.value = value;
      state.filters.status = value;
      render();
      return this.getSnapshot();
    },
    setSearch(value) {
      searchInput.value = value;
      state.filters.search = value.trim().toLowerCase();
      render();
      return this.getSnapshot();
    },
    selectRequirement(requirementId) {
      const match = state.rows.find((row) => row.requirement === requirementId);
      if (match) {
        state.selectedKey = match.key;
        render();
      }
      return this.getSnapshot();
    },
    clearFilters() {
      searchInput.value = "";
      stageFilter.value = "all";
      workstreamFilter.value = "all";
      statusFilter.value = "all";
      state.filters = {
        search: "",
        stage: "all",
        workstream: "all",
        status: "all",
      };
      render();
      return this.getSnapshot();
    },
  };
}
