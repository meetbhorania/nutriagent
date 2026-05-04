"""
NutriAgent MCP Server
Exposes nutrition tools that sub-agents can call via the MCP protocol.
Tools:
  - search_nutrition_data  : looks up nutrition facts for a food item
  - save_recipe            : persists recipe to SQLite
  - get_recipe_history     : retrieves saved recipes
"""

import json
import sqlite3
import os
import urllib.request
import urllib.parse
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "recipes.db")


def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            food_query  TEXT NOT NULL,
            recipe_name TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            steps       TEXT NOT NULL,
            calories    INTEGER,
            nutrition   TEXT,
            health_tip  TEXT,
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


# ── Exposed MCP Tools ────────────────────────────────────────────────────────

def search_nutrition_data(food_item: str) -> dict:
    """
    Search for real nutritional information about a food item.
    Returns summary text, key nutrition facts, and source URL.
    """
    try:
        query = urllib.parse.quote(f"{food_item} nutrition facts calories")
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "NutriAgent-MCP/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())

        abstract = data.get("Abstract", "").strip()
        source   = data.get("AbstractURL", "")
        related  = [
            r.get("Text", "") for r in data.get("RelatedTopics", [])[:4]
            if isinstance(r, dict) and r.get("Text")
        ]

        return {
            "success": True,
            "food_item": food_item,
            "summary": abstract or f"Nutritional data for {food_item} retrieved.",
            "key_facts": related,
            "source_url": source,
        }
    except Exception as e:
        return {
            "success": False,
            "food_item": food_item,
            "summary": f"Could not fetch live data for {food_item}. Using built-in knowledge.",
            "key_facts": [],
            "source_url": "",
        }


def save_recipe(
    food_query: str,
    recipe_name: str,
    ingredients: list[str],
    steps: list[str],
    calories: int,
    nutrition: dict,
    health_tip: str,
) -> dict:
    """Persist a completed recipe to the SQLite database."""
    try:
        conn = _get_db()
        cur = conn.execute(
            """INSERT INTO recipes
               (food_query, recipe_name, ingredients, steps, calories, nutrition, health_tip, created_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                food_query,
                recipe_name,
                json.dumps(ingredients),
                json.dumps(steps),
                int(calories),
                json.dumps(nutrition),
                health_tip,
                datetime.utcnow().isoformat(),
            ),
        )
        recipe_id = cur.lastrowid
        conn.commit()
        conn.close()
        return {"success": True, "recipe_id": recipe_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_recipe_history(limit: int = 20) -> dict:
    """Return list of previously saved recipes from the database."""
    try:
        conn = _get_db()
        rows = conn.execute(
            "SELECT id, food_query, recipe_name, calories, created_at FROM recipes ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        conn.close()
        return {
            "success": True,
            "count": len(rows),
            "recipes": [dict(r) for r in rows],
        }
    except Exception as e:
        return {"success": False, "error": str(e), "recipes": []}


def get_recipe_by_id(recipe_id: int) -> dict:
    """Retrieve a full recipe by its database ID."""
    try:
        conn = _get_db()
        row = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
        conn.close()
        if not row:
            return {"success": False, "error": f"No recipe with ID {recipe_id}"}
        r = dict(row)
        r["ingredients"] = json.loads(r["ingredients"])
        r["steps"]       = json.loads(r["steps"])
        r["nutrition"]   = json.loads(r["nutrition"])
        return {"success": True, "recipe": r}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Registry — ADK discovers tools from this dict
MCP_TOOLS = {
    "search_nutrition_data": search_nutrition_data,
    "save_recipe": save_recipe,
    "get_recipe_history": get_recipe_history,
    "get_recipe_by_id": get_recipe_by_id,
}
