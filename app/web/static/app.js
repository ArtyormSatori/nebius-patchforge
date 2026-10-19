// PatchForge-Nemotron Frontend Logic

let currentJob = null;

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  loadPresets();
  loadHealth();
});

async function loadHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    console.log("PatchForge System Health:", data);
  } catch (err) {
    console.error("Health fetch failed:", err);
  }
}

async function loadPresets() {
  const container = document.getElementById("presets-container");
  try {
    const res = await fetch("/api/presets");
    const presets = await res.json();
    container.innerHTML = "";

    presets.forEach((preset) => {
      const btn = document.createElement("button");
      btn.className = "w-full text-left p-2.5 rounded-lg bg-slate-950/80 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 transition flex items-center justify-between text-xs group";
      btn.innerHTML = `
        <div class="flex items-center space-x-2 truncate">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span class="font-medium text-slate-300 group-hover:text-emerald-300 truncate">${preset.title}</span>
        </div>
        <span class="text-[10px] text-slate-500 font-mono uppercase">${preset.language}</span>
      `;
      btn.onclick = () => selectPreset(preset);
      container.appendChild(btn);
    });

    // Auto-select first preset
    if (presets.length > 0) {
      selectPreset(presets[0]);
    }
  } catch (err) {
    container.innerHTML = `<span class="text-xs text-red-400">Failed to load presets: ${err.message}</span>`;
  }
}

function selectPreset(preset) {
  document.getElementById("input-title").value = preset.title;
  document.getElementById("input-path").value = preset.file_path;
  document.getElementById("input-language").value = preset.language;
  document.getElementById("input-error").value = preset.error_log;
  document.getElementById("input-code").value = preset.code_context;
}

function setStepState(stepNumber, state) {
  // state: 'idle', 'running', 'done', 'error'
  const stepEl = document.getElementById(`step-${stepNumber}`);
  const iconEl = document.getElementById(`step-${stepNumber}-icon`);

  if (!stepEl || !iconEl) return;

  stepEl.classList.remove("border-emerald-500", "border-cyan-500", "border-amber-500", "border-red-500", "bg-emerald-950/30", "bg-cyan-950/30", "bg-amber-950/30");
  iconEl.classList.remove("bg-emerald-500", "bg-cyan-500", "bg-amber-500", "bg-red-500", "text-black", "animate-spin");

  if (state === "running") {
    stepEl.classList.add("border-cyan-500", "bg-cyan-950/30");
    iconEl.classList.add("bg-cyan-500", "text-black", "animate-spin");
    iconEl.innerHTML = `<i class="fa-solid fa-spinner"></i>`;
  } else if (state === "done") {
    stepEl.classList.add("border-emerald-500", "bg-emerald-950/30");
    iconEl.classList.add("bg-emerald-500", "text-black");
    iconEl.innerHTML = `<i class="fa-solid fa-check"></i>`;
  } else if (state === "error") {
    stepEl.classList.add("border-red-500");
    iconEl.classList.add("bg-red-500", "text-white");
    iconEl.innerHTML = `<i class="fa-solid fa-xmark"></i>`;
  } else {
    iconEl.innerHTML = `${stepNumber}`;
  }
}

async function runPipeline() {
  const submitBtn = document.getElementById("btn-submit");
  const statusBadge = document.getElementById("pipeline-status-badge");

  const title = document.getElementById("input-title").value.trim();
  const filePath = document.getElementById("input-path").value.trim();
  const language = document.getElementById("input-language").value;
  const errorLog = document.getElementById("input-error").value.trim();
  const codeContext = document.getElementById("input-code").value.trim();
  const enableTavily = document.getElementById("input-tavily").checked;

  if (!codeContext || !errorLog) {
    alert("Please provide both target source code and error incident log.");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.classList.add("opacity-50", "cursor-not-allowed");
  statusBadge.textContent = "RUNNING";
  statusBadge.className = "text-[11px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 animate-pulse";

  // Hide placeholder
  document.getElementById("placeholder-state").classList.add("hidden");

  // Reset steps
  [1, 2, 3, 4].forEach((s) => setStepState(s, "idle"));
  setStepState(1, "running");

  const payload = {
    title: title || "Remediation Request",
    file_path: filePath || "app/handler.py",
    language: language,
    error_log: errorLog,
    code_context: codeContext,
    enable_tavily_search: enableTavily,
  };

  try {
    const startTime = performance.now();
    const res = await fetch("/api/patch/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`API error HTTP ${res.status}`);
    }

    const data = await res.json();
    currentJob = data;
    const elapsed = Math.round(performance.now() - startTime);

    // Animate completion of steps
    setStepState(1, "done");
    setStepState(2, enableTavily ? "done" : "idle");
    setStepState(3, "done");
    setStepState(4, data.verification && data.verification.tests_passed ? "done" : "error");

    statusBadge.textContent = `COMPLETED (${elapsed}ms)`;
    statusBadge.className = "text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800";

    renderResults(data);
  } catch (err) {
    console.error("Pipeline failure:", err);
    statusBadge.textContent = "FAILED";
    statusBadge.className = "text-[11px] font-mono px-2 py-0.5 rounded bg-red-950 text-red-300 border border-red-800";
    alert(`Pipeline failed: ${err.message}`);
  } finally {
    submitBtn.disabled = false;
    submitBtn.classList.remove("opacity-50", "cursor-not-allowed");
  }
}

function renderResults(job) {
  // 1. Triage card
  if (job.triage) {
    document.getElementById("triage-card").classList.remove("hidden");
    document.getElementById("triage-type").textContent = job.triage.error_type;
    document.getElementById("triage-lines").textContent = job.triage.suspect_lines.join(", ") || "N/A";
    document.getElementById("triage-summary").textContent = job.triage.summary;
    document.getElementById("triage-latency").textContent = `${Math.round(job.triage.latency_ms)}ms`;

    const sevEl = document.getElementById("triage-severity");
    sevEl.textContent = job.triage.severity;
    if (job.triage.severity === "CRITICAL") {
      sevEl.className = "px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-red-950 border border-red-800 text-red-300";
    } else {
      sevEl.className = "px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-amber-950 border border-amber-800 text-amber-300";
    }
  }

  // 2. Tavily Card
  if (job.search && job.search.results && job.search.results.length > 0) {
    document.getElementById("tavily-card").classList.remove("hidden");
    document.getElementById("tavily-summary").textContent = job.search.summary;
    document.getElementById("tavily-live-badge").textContent = job.search.live_call ? "Live Tavily API" : "Simulated Intel";

    const hitsContainer = document.getElementById("tavily-hits");
    hitsContainer.innerHTML = "";
    job.search.results.forEach((hit) => {
      const div = document.createElement("div");
      div.className = "p-2 rounded bg-slate-950/80 border border-slate-800";
      div.innerHTML = `
        <div class="font-semibold text-slate-300 flex items-center justify-between mb-1">
          <span>${hit.title}</span>
          ${hit.url ? `<a href="${hit.url}" target="_blank" class="text-amber-400 hover:underline text-[10px] font-mono"><i class="fa-solid fa-arrow-up-right-from-square"></i> link</a>` : ""}
        </div>
        <p class="text-slate-400 text-[11px] leading-relaxed">${hit.snippet}</p>
      `;
      hitsContainer.appendChild(div);
    });
  } else {
    document.getElementById("tavily-card").classList.add("hidden");
  }

  // 3. RCA Card
  if (job.proposal) {
    document.getElementById("rca-card").classList.remove("hidden");
    document.getElementById("rca-root-cause").textContent = job.proposal.root_cause;
    document.getElementById("rca-strategy").textContent = job.proposal.fix_strategy;
    document.getElementById("rca-latency").textContent = `${Math.round(job.proposal.latency_ms)}ms`;

    // 4. Patch diff
    document.getElementById("patch-card").classList.remove("hidden");
    renderDiff(job.proposal.unified_diff);

    // Diff stats badge
    const statsBadge = document.getElementById("diff-stats-badge");
    if (statsBadge && job.verification && job.verification.diff_stats) {
      const stats = job.verification.diff_stats;
      statsBadge.textContent = `+${stats.additions || 0} / -${stats.deletions || 0} lines`;
      statsBadge.classList.remove("hidden");
    } else if (statsBadge) {
      statsBadge.classList.add("hidden");
    }
  }

  // 5. Verification Card
  if (job.verification) {
    document.getElementById("verification-card").classList.remove("hidden");
    document.getElementById("verification-details").textContent = job.verification.details;
    document.getElementById("verification-testplan").textContent = job.proposal ? job.proposal.test_plan : "No test plan provided";

    const verStatus = document.getElementById("verification-status");
    if (job.verification.tests_passed) {
      verStatus.textContent = "HERMETIC VERIFIED PASS";
      verStatus.className = "px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-950 border border-emerald-800 text-emerald-300";
    } else {
      verStatus.textContent = "VERIFICATION FAILED";
      verStatus.className = "px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-red-950 border border-red-800 text-red-300";
    }
  }
}

function renderDiff(diffText) {
  const container = document.getElementById("patch-diff");
  container.innerHTML = "";

  const lines = diffText.split("\n");
  lines.forEach((line) => {
    const span = document.createElement("span");
    if (line.startsWith("+++ ") || line.startsWith("--- ")) {
      span.className = "diff-line-header";
    } else if (line.startsWith("@@")) {
      span.className = "diff-line-hunk";
    } else if (line.startsWith("+")) {
      span.className = "diff-line-add";
    } else if (line.startsWith("-")) {
      span.className = "diff-line-del";
    } else {
      span.style.display = "block";
      span.style.padding = "0 4px";
    }
    span.textContent = line;
    container.appendChild(span);
  });
}

function downloadPatch() {
  if (!currentJob || !currentJob.proposal || !currentJob.proposal.unified_diff) {
    alert("No active patch available to download.");
    return;
  }
  const blob = new Blob([currentJob.proposal.unified_diff], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `patchforge_${currentJob.job_id}.patch`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function copyPatch() {
  if (!currentJob || !currentJob.proposal || !currentJob.proposal.unified_diff) {
    alert("No active patch available to copy.");
    return;
  }
  navigator.clipboard.writeText(currentJob.proposal.unified_diff).then(() => {
    const btnText = document.getElementById("copy-btn-text");
    if (btnText) {
      btnText.textContent = "Copied!";
      setTimeout(() => {
        btnText.textContent = "Copy";
      }, 2000);
    }
  }).catch((err) => {
    console.error("Clipboard copy failed:", err);
  });
}
