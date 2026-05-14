import { useState } from "react";
import "./App.css";

// ── Idea Card ──────────────────────────────────────────────────────
function IdeaCard({ type, idea }) {
  const [open, setOpen] = useState(false);

  const config = {
    incremental:    { label: "Incremental",    icon: "📈", color: "#2563EB", bg: "#EFF6FF", border: "#BFDBFE" },
    radical:        { label: "Radical",        icon: "💥", color: "#DC2626", bg: "#FEF2F2", border: "#FECACA" },
    ready_made:     { label: "Ready-Made",     icon: "📦", color: "#059669", bg: "#ECFDF5", border: "#A7F3D0" },
    out_of_the_box: { label: "Out of the Box", icon: "🌀", color: "#7C3AED", bg: "#F5F3FF", border: "#DDD6FE" },
  }[type];

  if (!idea) return null;

  return (
    <div
      className={`idea-card ${open ? "idea-open" : ""}`}
      style={{ "--cc": config.color, "--cb": config.bg, "--cbr": config.border }}
    >
      <div className="idea-header" onClick={() => setOpen(!open)}>
        <div className="idea-icon" style={{ background: open ? config.color : config.bg }}>
          <span style={{ filter: open ? "brightness(10)" : "none" }}>{config.icon}</span>
        </div>
        <div className="idea-meta">
          <span className="idea-tag"
            style={{ color: config.color, background: config.bg, border: `1px solid ${config.border}` }}>
            {config.label}
          </span>
          <p className="idea-title">{idea.title}</p>
        </div>
        <span className="idea-chevron">{open ? "▲" : "▼"}</span>
      </div>

      {open && (
        <div className="idea-body">
          <p className="idea-desc">{idea.description}</p>
          <div className="idea-facts">
            <div className="idea-fact">
              <span className="fact-lbl">Why this window</span>
              <span className="fact-val">{idea.rationale}</span>
            </div>
            <div className="idea-fact">
              <span className="fact-lbl">Expected impact</span>
              <span className="fact-val">{idea.impact}</span>
            </div>
          </div>
          {idea.source && <p className="idea-source">🔗 {idea.source}</p>}
        </div>
      )}
    </div>
  );
}

// ── Sub-Phase Panel ────────────────────────────────────────────────
// Shows the ideas and barriers for ONE specific sub-phase (e.g. "0-6 months")
function SubPhasePanel({ data }) {
  if (!data) return null;

  return (
    <div className="subphase-panel">
      {/* Barriers */}
      {data.potential_problems?.length > 0 && (
        <div className="barriers">
          <p className="barriers-title">⚠ Innovation Barriers</p>
          <div className="barriers-grid">
            {data.potential_problems.map((p, i) => (
              <div key={i} className="barrier-item">
                <span className="barrier-num">{i + 1}</span>
                <span className="barrier-text">{p}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 4 Idea Cards */}
      <div className="ideas-grid">
        {["incremental", "radical", "ready_made", "out_of_the_box"].map(type => (
          <IdeaCard key={type} type={type} idea={data[type]} />
        ))}
      </div>
    </div>
  );
}

// ── Horizon Panel ──────────────────────────────────────────────────
// Shows clickable sub-phase tabs and switches content between them
function HorizonPanel({ data }) {
  const [activeSubPhase, setActiveSubPhase] = useState(0);

  if (!data) return null;

  const subPhases = data.sub_phases || [];
  const subPhaseData = data.subphase_data || [];
  const currentData = subPhaseData[activeSubPhase];

  return (
    <div className="horizon-panel">

      {/* Clickable sub-phase tabs */}
      {subPhases.length > 1 && (
        <div className="subphase-tabs">
          {subPhases.map((sp, i) => (
            <button
              key={sp}
              className={`subphase-tab ${activeSubPhase === i ? "subphase-tab-active" : ""}`}
              onClick={() => setActiveSubPhase(i)}
            >
              {sp}
            </button>
          ))}
        </div>
      )}

      {/* Single sub-phase (FUTURE) — just show as label */}
      {subPhases.length === 1 && (
        <div className="subphase-tabs">
          <span className="subphase-tab subphase-tab-active">{subPhases[0]}</span>
        </div>
      )}

      {/* Content for active sub-phase */}
      <SubPhasePanel data={currentData} />
    </div>
  );
}

// ── Main App ───────────────────────────────────────────────────────
const MAIN_TABS = [
  { key: "now",    label: "NOW",    sub: "0–24 months", color: "#EA580C" },
  { key: "next",   label: "NEXT",   sub: "1–5 years",   color: "#1D4ED8" },
  { key: "future", label: "FUTURE", sub: "5–10 years",  color: "#065F46" },
];

const LOADING_STEPS = [
  "Analyzing product landscape...",
  "Benchmarking competitors...",
  "Generating NOW 0-6 months ideas...",
  "Generating NOW 6-24 months ideas...",
  "Generating NEXT 1-2 year ideas...",
  "Generating NEXT 2-5 year ideas...",
  "Generating FUTURE 5-10 year ideas...",
  "Structuring your blueprint...",
];

export default function App() {
  const [product, setProduct]     = useState("");
  const [blueprint, setBlueprint] = useState(null);
  const [loading, setLoading]     = useState(false);
  const [activeTab, setActiveTab] = useState("now");
  const [step, setStep]           = useState(0);
  const [error, setError]         = useState("");

  const generate = async () => {
    if (!product.trim()) { setError("Please enter a product name."); return; }
    setError("");
    setBlueprint(null);
    setLoading(true);
    setStep(0);
    setActiveTab("now");

    // Animate loading steps — 5 AI calls so takes ~90 seconds
    let s = 0;
    const interval = setInterval(() => {
      s = Math.min(s + 1, LOADING_STEPS.length - 1);
      setStep(s);
    }, 12000);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/blueprint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product: product.trim() }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Server error");
      setBlueprint(data.blueprint);
    } catch (err) {
      setError(err.message || "Something went wrong. Is the backend running?");
    }

    clearInterval(interval);
    setLoading(false);
  };

  // ── LOADING ────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="screen-center">
        <div className="loader-spinner" />
        <h2 className="loader-title">Researching "{product}"</h2>
        <p className="loader-step">{LOADING_STEPS[step]}</p>
        <div className="loader-steps">
          {LOADING_STEPS.map((s, i) => (
            <div key={i} className={`lstep ${i < step ? "lstep-done" : i === step ? "lstep-active" : ""}`}>
              <span className="lstep-dot">{i < step ? "✓" : ""}</span>
              <span className="lstep-text">{s}</span>
            </div>
          ))}
        </div>
        <p className="loader-note">Generating 5 separate idea sets — takes ~90 seconds</p>
      </div>
    );
  }

  // ── RESULTS ────────────────────────────────────────────────────
  if (blueprint) {
    return (
      <div className="screen-results">

        {/* Top bar */}
        <div className="results-topbar">
          <div>
            <span className="results-badge">Innovation Blueprint</span>
            {blueprint.domain && <span className="results-domain">{blueprint.domain}</span>}
            <h2 className="results-product">{blueprint.product}</h2>
            {blueprint.executive_summary && (
              <p className="results-summary">{blueprint.executive_summary}</p>
            )}
          </div>
          <button className="btn-reset" onClick={() => { setBlueprint(null); setProduct(""); }}>
            ↩ New Blueprint
          </button>
        </div>

        {/* Main horizon tabs: NOW / NEXT / FUTURE */}
        <div className="tab-bar">
          {MAIN_TABS.map(t => (
            <button
              key={t.key}
              className={`tab-btn ${activeTab === t.key ? "tab-active" : ""}`}
              style={activeTab === t.key ? { background: t.color } : {}}
              onClick={() => setActiveTab(t.key)}
            >
              <span className="tab-label">{t.label}</span>
              <span className="tab-sub">{t.sub}</span>
            </button>
          ))}
        </div>

        {/* Horizon content with clickable sub-phase tabs inside */}
        <HorizonPanel data={blueprint[activeTab]} />
      </div>
    );
  }

  // ── INPUT ──────────────────────────────────────────────────────
  return (
    <div className="screen-center">
      <div className="input-badge">dormakaba · R&D Innovation Engine</div>
      <h1 className="input-title">
        What should we <span className="input-accent">innovate</span> next?
      </h1>
      <p className="input-desc">
        Enter any product to generate a <strong>NOW · NEXT · FUTURE</strong> innovation blueprint
        <br />
        <span style={{ fontSize: "13px", color: "#475569" }}>
          Each horizon has clickable sub-phases with separate idea sets
        </span>
      </p>

      <div className="input-card">
        <div className="input-row">
          <input
            type="text"
            className="product-input"
            placeholder="e.g. Electronic Door Lock, Smart Key Card..."
            value={product}
            onChange={e => setProduct(e.target.value)}
            onKeyDown={e => e.key === "Enter" && generate()}
          />
          <button className="btn-generate" onClick={generate} disabled={!product.trim()}>
            Generate Blueprint →
          </button>
        </div>
        {error && <p className="input-error">⚠ {error}</p>}

        <div className="example-pills">
          <span className="pills-label">Try:</span>
          {["Electronic Door Lock", "Hotel Key Card", "Biometric Reader", "Smart Lock"].map(p => (
            <button key={p} className="pill" onClick={() => setProduct(p)}>{p}</button>
          ))}
        </div>
      </div>

      <div className="feature-row">
        {[
          "📰 Live Research", " Patent Signals", " Competitor Intel",
          " 4 Idea Types", "⏱ 5 Sub-Phases", "⚠ Innovation Barriers"
        ].map(f => (
          <span key={f} className="feat">{f}</span>
        ))}
      </div>
    </div>
  );
}
