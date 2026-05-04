"""
Step Agent — Sub-Agent 2 of 3
Responsibility: Takes the recipe name + ingredients from session state
and generates clear, numbered cooking steps.
Reads: session state["recipe_data"]
Writes: session state["step_data"]
"""

from google.adk.agents import LlmAgent

step_agent = LlmAgent(
    name="StepAgent",
    model="gemini-2.5-flash",
    description=(
        "Generates detailed, step-by-step cooking instructions for the recipe "
        "that was identified by RecipeAgent."
    ),
    instruction="""You are an expert chef writing recipe instructions.

The previous agent has identified a recipe. It is stored in {recipe_data}.

Your task:
- Read the recipe_name and ingredients from {recipe_data}
- Write 5-7 clear, actionable cooking steps
- Each step should be practical and specific (temperatures, timings, techniques)

Output ONLY a JSON object (no markdown, no extra text):
{
  "steps": [
    "Step description 1",
    "Step description 2",
    ...
  ]
}""",
    output_key="step_data",
)
