import { useState, useEffect } from "react";
import RecipeCard from "./components/RecipeCard";
import HistoryPanel from "./components/HistoryPanel";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const SUGGESTIONS = [
  "Eggs", "Salmon", "Avocado", "Lentils",
  "Chicken breast", "Sweet potato", "Chickpeas",
  "Tofu", "Quinoa", "Spinach",
];

const LOADING_STEPS = [
  "RecipeAgent → searching nutrition data…",
  "RecipeAgent → selecting ingredients…",
  "StepAgent → writing cooking instructions…",
  "CalorieAgent → calculating macros…",
  "CalorieAgent → saving to database…",
];

export default function App() {
  const [food, setFood] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [tab, setTab] = useState("search");
  const [loadingText, setLoadingText] = useState(LOADING_STEPS[0]);

  useEffect(() => {
    let i = 0, iv;
    if (loading) {
      iv = setInterval(() => {
        i = (i + 1) % LOADING_STEPS.length;
        setLoadingText(LOADING_STEPS[i]);
      }, 1800);
    }
    return () => clearInterval(iv);
  }, [loading]);

  async function analyzeFood(override) {
    const query = (override || food).trim();
    if (!query) return;

    setFood(query);
    setLoading(true);
    setResult(null);
    setError("");
    setTab("search");

    try {
      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ food: query }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Agent pipeline failed");
      }
      setResult(await res.json());
    } catch (e) {
      setError(e.message || "Something went wrong. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  function reset() { setResult(null); setFood(""); setError(""); }

  return (
    <div className="app">
      <div className="ambient" />

      <main>
        <header>
          <div className="brand-mark">
            <div className="brand-icon">
              <svg viewBox="0 0 18 18" fill="none">
                <path d="M9 2L10.8 6.7H16L12 9.8L13.6 14.5L9 11.5L4.4 14.5L6 9.8L2 6.7H7.2L9 2Z"
                  stroke="#C9A84C" strokeWidth="1" fill="none" strokeLinejoin="round" />
              </svg>
            </div>
            <span className="brand-name">NutriAgent</span>
          </div>
          <h1>Food Intelligence,<br /><em>Beautifully Served</em></h1>
          <p className="header-sub">
            Three specialist agents working in sequence:<br />
            <span className="pipeline-label">RecipeAgent → StepAgent → CalorieAgent</span>
          </p>
        </header>

        <div className="tabs">
          <button className={`tab ${tab === "search" ? "active" : ""}`} onClick={() => setTab("search")}>
            ✦ Analyse Food
          </button>
          <button className={`tab ${tab === "history" ? "active" : ""}`} onClick={() => setTab("history")}>
            ◷ Recipe History
          </button>
        </div>

        {tab === "search" && (
          <div className="search-section">
            {!result && !loading && (
              <>
                <label className="search-label">Ingredient or dish</label>
                <div className="search-row">
                  <input
                    className="search-input"
                    type="text"
                    value={food}
                    onChange={e => setFood(e.target.value)}
                    onKeyDown={e => e.key === "Enter" && analyzeFood()}
                    placeholder="e.g. eggs, butter chicken, avocado…"
                    autoFocus
                  />
                  <button className="btn-gold large" onClick={() => analyzeFood()} disabled={loading}>
                    <span>✦</span> Analyse
                  </button>
                </div>
                <div className="chips">
                  {SUGGESTIONS.map(s => (
                    <button key={s} className="chip" onClick={() => analyzeFood(s)}>{s}</button>
                  ))}
                </div>
              </>
            )}

            {error && <div className="error-box">⚠ {error}</div>}

            {loading && (
              <div className="loading">
                <div className="loader-ring" />
                <p className="loading-text">{loadingText}</p>
                <div className="pipeline-viz">
                  <span className={loadingText.includes("Recipe") ? "pipe-step active" : "pipe-step done"}>RecipeAgent</span>
                  <span className="pipe-arrow">→</span>
                  <span className={loadingText.includes("Step") ? "pipe-step active" : loadingText.includes("Calorie") ? "pipe-step done" : "pipe-step"}>StepAgent</span>
                  <span className="pipe-arrow">→</span>
                  <span className={loadingText.includes("Calorie") ? "pipe-step active" : "pipe-step"}>CalorieAgent</span>
                </div>
              </div>
            )}

            {result && !loading && (
              <>
                <RecipeCard result={result} />
                <button className="btn-ghost" onClick={reset}>← Search another ingredient</button>
              </>
            )}
          </div>
        )}

        {tab === "history" && (
          <HistoryPanel
            apiBase={API_BASE}
            onLoad={r => { setResult(r); setTab("search"); }}
          />
        )}
      </main>
    </div>
  );
}