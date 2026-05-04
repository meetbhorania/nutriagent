"""
Recipe Agent — Sub-Agent 1 of 3
Responsibility: Given a food item, search for nutritional context and
decide on a healthy recipe name + ingredients list.
Writes results to session state: recipe_name, ingredients, food_query
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from ..mcp_server.tools import search_nutrition_data

# Wrap MCP tool as ADK FunctionTool
search_tool = FunctionTool(func=search_nutrition_data)

recipe_agent = LlmAgent(
    name="RecipeAgent",
    model="gemini-2.5-flash",
    description=(
        "Searches for nutritional data about a food item and decides on "
        "the best healthy recipe name and ingredient list."
    ),
    instruction="""You are a professional nutritionist and chef.

Your task:
1. Call search_nutrition_data with the food item the user provided
2. Based on the nutritional information returned, choose a healthy, appealing recipe name
3. List 6-10 specific ingredients with quantities (e.g. "200g chicken breast", "2 cloves garlic")

Output ONLY a JSON object with this exact structure (no markdown, no extra text):
{
  "food_query": "<original food item>",
  "recipe_name": "<dish name>",
  "ingredients": ["<ingredient 1>", "<ingredient 2>", ...]
}""",
    tools=[search_tool],
    output_key="recipe_data",  # written to session state
)
