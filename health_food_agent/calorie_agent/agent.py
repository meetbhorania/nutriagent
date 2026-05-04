"""
Calorie Agent — Sub-Agent 3 of 3
Responsibility: Calculates accurate calorie count + full macros for the recipe,
then saves everything to the database via the MCP save_recipe tool.
Reads: session state["recipe_data"], session state["step_data"]
Writes: session state["calorie_data"]  +  persists to DB
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from ..mcp_server.tools import save_recipe

save_tool = FunctionTool(func=save_recipe)

calorie_agent = LlmAgent(
    name="CalorieAgent",
    model="gemini-2.5-flash",
    description=(
        "Calculates accurate per-serving calorie count and full macronutrients "
        "for the recipe, then saves the complete recipe to the database."
    ),
    instruction="""You are a registered dietitian specialising in nutritional analysis.

You have access to:
- Recipe data in {recipe_data} (food_query, recipe_name, ingredients)
- Cooking steps in {step_data} (steps list)

Your tasks:
1. Calculate realistic per-serving nutrition for the recipe:
   - calories_per_serving (integer kcal)
   - protein (string with unit, e.g. "32g")
   - carbs (string, e.g. "28g")
   - fat (string, e.g. "12g")
   - fibre (string, e.g. "5g")
   - sugar (string, e.g. "4g")
   - Write one insightful health_tip sentence

2. Call save_recipe to persist the full recipe with all details.

3. Output ONLY a JSON object (no markdown):
{
  "calories_per_serving": 420,
  "nutrition": {
    "protein": "32g",
    "carbs": "28g",
    "fat": "12g",
    "fibre": "5g",
    "sugar": "4g"
  },
  "health_tip": "This dish is high in...",
  "recipe_id": <returned from save_recipe>
}""",
    tools=[save_tool],
    output_key="calorie_data",
)
