import { useState, useEffect } from "react";

export default function HistoryPanel({ apiBase, onLoad }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState("");

  useEffect(() => {
    fetch(`${apiBase}/api/history?limit=30`)
      .then(r => r.json())
      .then(d => { setHistory(d.recipes || []); setLoading(false); })
      .catch(() => { setError("Could not load history. Is the backend running?"); setLoading(false); });
  }, [apiBase]);

  async function loadFull(id) {
    try {
      const r = await fetch(`${apiBase}/api/recipe/${id}`);
      const recipe = await r.json();
      onLoad({
        recipe_name: recipe.recipe_name,
        ingredients: recipe.ingredients,
        steps: recipe.steps,
        calories_per_serving: recipe.calories,
        nutrition: recipe.nutrition,
        health_tip: recipe.health_tip,
        saved_id: recipe.id,
        agent_reasoning: [],
      });
    } catch { alert("Failed to load recipe."); }
  }

  function fmtDate(iso) {
    try {
      return new Date(iso).toLocaleDateString("en-GB", {
        day: "numeric", month: "short", year: "numeric",
        hour: "2-digit", minute: "2-digit",
      });
    } catch { return iso; }
  }

  if (loading) return <div className="history-empty">Loading history…</div>;
  if (error)   return <div className="error-box">{error}</div>;
  if (!history.length) return (
    <div className="history-empty">
      <div style={{ fontSize: 32, marginBottom: 12, opacity: 0.3 }}>◷</div>
      No recipes yet. Analyse a food item to get started.
    </div>
  );

  return (
    <div>
      <p style={{ fontSize: 12, color: "var(--text-3)", fontFamily: "DM Mono, monospace", letterSpacing: "0.06em", marginBottom: 16, textTransform: "uppercase" }}>
        {history.length} recipe{history.length !== 1 ? "s" : ""} saved
      </p>
      <div className="history-grid">
        {history.map(r => (
          <div key={r.id} className="history-item" onClick={() => loadFull(r.id)}>
            <div className="history-item-left">
              <div className="history-recipe-name">{r.recipe_name}</div>
              <div className="history-meta">Query: {r.food_query} · {fmtDate(r.created_at)}</div>
            </div>
            <div className="history-cal">{r.calories} kcal</div>
          </div>
        ))}
      </div>
    </div>
  );
}
