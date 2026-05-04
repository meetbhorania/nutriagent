"""
NutriAgent — Root Orchestrator
Uses ADK SequentialAgent to chain:
  RecipeAgent → StepAgent → CalorieAgent

Also exposes a FastAPI HTTP interface so the React frontend can talk to it.
Run with:  uvicorn health_food_agent.agent:app --reload --port 8000
Or via ADK dev UI:  adk web
"""

import json
import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
load_dotenv()  # auto-loads .env file from project root

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from google.adk.agents import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from .recipe_agent import recipe_agent
from .step_agent import step_agent
from .calorie_agent import calorie_agent
from .mcp_server.tools import get_recipe_history, get_recipe_by_id

# ── ADK Agent Setup ──────────────────────────────────────────────────────────

# Root agent: chains the 3 specialists in order
root_agent = SequentialAgent(
    name="NutriAgent",
    description=(
        "Orchestrates recipe search, step generation, and calorie calculation "
        "to produce a complete healthy recipe for any food item."
    ),
    sub_agents=[recipe_agent, step_agent, calorie_agent],
)

# ADK session service (in-memory; swap for DatabaseSessionService in prod)
session_service = InMemorySessionService()

APP_NAME = "nutriagent"


async def run_nutriagent(food: str, api_key: str) -> dict:
    """
    Execute the full ADK pipeline for a given food item.
    Returns merged result from all three sub-agent output keys.
    """
    os.environ["GOOGLE_API_KEY"] = api_key

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    session_id = f"session_{food.replace(' ', '_')}_{id(food)}"
    user_id    = "web_user"

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    user_message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=f"Generate a healthy recipe featuring: {food}")],
    )

    final_response = ""
    agent_steps    = []

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text or ""
        # Collect agent reasoning steps for the UI log
        if hasattr(event, "author") and event.author:
            step_text = ""
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        step_text = part.text[:180]
                    elif hasattr(part, "function_call") and part.function_call:
                        step_text = f"🔧 {part.function_call.name}(...)"
                    elif hasattr(part, "function_response") and part.function_response:
                        step_text = f"✓ Tool response received"
            if step_text:
                agent_steps.append(f"[{event.author}] {step_text}")

    # Pull sub-agent outputs from session state
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    state = session.state if session else {}

    recipe_data  = _parse_json_field(state.get("recipe_data", "{}"))
    step_data    = _parse_json_field(state.get("step_data", "{}"))
    calorie_data = _parse_json_field(state.get("calorie_data", "{}"))

    return {
        "recipe_name":          recipe_data.get("recipe_name", f"{food.title()} Recipe"),
        "food_query":           recipe_data.get("food_query", food),
        "ingredients":          recipe_data.get("ingredients", []),
        "steps":                step_data.get("steps", []),
        "calories_per_serving": calorie_data.get("calories_per_serving", 0),
        "nutrition":            calorie_data.get("nutrition", {}),
        "health_tip":           calorie_data.get("health_tip", ""),
        "saved_id":             calorie_data.get("recipe_id"),
        "agent_reasoning":      agent_steps,
    }


def _parse_json_field(value) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            cleaned = value.strip().replace("```json", "").replace("```", "").strip()
            import re
            match = re.search(r"\{[\s\S]*\}", cleaned)
            return json.loads(match.group(0)) if match else {}
        except Exception:
            return {}
    return {}


# ── FastAPI HTTP Server ──────────────────────────────────────────────────────

app = FastAPI(title="NutriAgent API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    food: str
    api_key: Optional[str] = None


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    api_key = req.api_key or os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        raise HTTPException(400, "GOOGLE_API_KEY not set. Pass api_key in request body or set env var.")
    if not req.food.strip():
        raise HTTPException(400, "Food item cannot be empty.")
    result = await run_nutriagent(req.food.strip(), api_key)
    return result


@app.get("/api/history")
def history(limit: int = 20):
    return get_recipe_history(limit)


@app.get("/api/recipe/{recipe_id}")
def recipe(recipe_id: int):
    result = get_recipe_by_id(recipe_id)
    if not result.get("success"):
        raise HTTPException(404, result.get("error", "Not found"))
    return result["recipe"]


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "framework": "Google ADK",
        "pipeline": "RecipeAgent → StepAgent → CalorieAgent",
        "mcp_tools": ["search_nutrition_data", "save_recipe", "get_recipe_history", "get_recipe_by_id"],
    }


# Serve built React frontend in production
_frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(_frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(_frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        return FileResponse(os.path.join(_frontend_dist, "index.html"))
