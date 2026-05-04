export default function RecipeCard({ result }) {
  const nut = result.nutrition || {};
  const nutLabels = { protein: "Protein", carbs: "Carbs", fat: "Fat", fibre: "Fibre", sugar: "Sugar" };

  return (
    <div className="recipe-result">
      <div className="result-header">
        <h2 className="result-title">{result.recipe_name}</h2>
        <div className="calorie-badge">
          <span className="calorie-number">{result.calories_per_serving}</span>
          <span className="calorie-label">kcal / serving</span>
        </div>
      </div>

      <div className="cards-grid">
        <div className="result-card">
          <div className="card-label">Ingredients</div>
          <ul className="ingredients-list">
            {(result.ingredients || []).map((ing, i) => <li key={i}>{ing}</li>)}
          </ul>
        </div>

        <div className="result-card">
          <div className="card-label">Nutrition per serving</div>
          <div className="nutrition-grid">
            {Object.entries(nutLabels).map(([key, label]) =>
              nut[key] ? (
                <div key={key} className="nutrition-item">
                  <span className="nutrition-val">{nut[key]}</span>
                  <span className="nutrition-name">{label}</span>
                </div>
              ) : null
            )}
          </div>
          {result.health_tip && <div className="health-tip">{result.health_tip}</div>}
        </div>

        <div className="result-card full">
          <div className="card-label">Method</div>
          <ol className="steps-list">
            {(result.steps || []).map((step, i) => (
              <li key={i}>
                <span className="step-num">{i + 1}</span>
                <span className="step-text">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      </div>

      {result.saved_id && (
        <div className="saved-badge">✓ Saved to database (ID #{result.saved_id})</div>
      )}
    </div>
  );
}
