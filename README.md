# NutriAgent 🍽️

AI health food agent built with **Google ADK** (Agent Development Kit).
Enter any food item → three specialist agents work in sequence to deliver a healthy recipe, full cooking instructions, and accurate calorie/macro breakdown.

---

## Architecture — Mirrors the GitHub Reference Repo

```
health_food_agent/
├── .adk/                  ← ADK project config
├── mcp_server/            ← MCP tools (nutrition search, DB save/read)
│   └── tools.py
├── recipe_agent/          ← Sub-Agent 1: search + pick recipe + ingredients
│   └── agent.py
├── step_agent/            ← Sub-Agent 2: generate cooking instructions
│   └── agent.py
├── calorie_agent/         ← Sub-Agent 3: calculate macros + save to DB
│   └── agent.py
├── __init__.py
└── agent.py               ← Root SequentialAgent + FastAPI HTTP server
```

### ADK Pipeline (SequentialAgent)

```
User Input: "eggs"
     │
     ▼
┌─────────────────┐
│  RecipeAgent    │  → calls search_nutrition_data (MCP tool)
│                 │  → writes recipe_name + ingredients to session state
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   StepAgent     │  → reads session state["recipe_data"]
│                 │  → writes 5-7 cooking steps to session state
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CalorieAgent   │  → reads recipe_data + step_data from session state
│                 │  → calculates calories + macros
│                 │  → calls save_recipe (MCP tool) → SQLite DB
└─────────────────┘
         │
         ▼
  Final result returned to React frontend
```

### MCP Tools (in mcp_server/tools.py)

| Tool | Description |
|---|---|
| `search_nutrition_data` | DuckDuckGo instant answers for real nutrition facts |
| `save_recipe` | Persist completed recipe to SQLite database |
| `get_recipe_history` | Return list of saved recipes |
| `get_recipe_by_id` | Retrieve a specific recipe by ID |

---

## Quick Start

### 1 — Get a free Gemini API key
Go to: **https://aistudio.google.com/app/apikey**
Sign in → Create API key → copy it (starts with `AIza...`)

### 2 — Open in Antigravity
1. Extract this zip → you get a `nutriagent/` folder
2. Open **Google Antigravity**
3. Click **Open Folder** → select `nutriagent/`
4. Antigravity recognises it as a full multi-file workspace

### 3 — Create and activate a virtual environment (Terminal 1 in Antigravity)

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You'll see `(venv)` appear at the start of your terminal prompt — that means it's active.

### 4 — Install dependencies and configure environment

```bash
# Install all Python packages into the venv (not your global Python)
pip install -r requirements.txt

# Copy the env template and add your API key
cp .env.example .env
```

Now open `.env` in Antigravity's editor and set:
```
GOOGLE_API_KEY=AIzaSy...your_actual_key_here
```

### 5 — Start the backend (still in Terminal 1, venv active)

```bash
# Load your .env and start the FastAPI server
source .env && uvicorn health_food_agent.agent:app --reload --port 8000
```

**OR** use the ADK Dev UI for a full visual agent inspector:
```bash
source .env && adk web
```
The ADK Dev UI shows each agent's reasoning, tool calls, and session state step by step — great for demos.

### 6 — Start the frontend (Terminal 2 in Antigravity — no venv needed here)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

> **Note:** Every time you open a new terminal session to work on this project, re-activate the venv first:
> `source venv/` on Mac/Linux or `venv\Scripts\activate` on Windows.

---

## Using the ADK Dev UI

With venv active:
```bash
source .env && adk web
```

This gives you a visual interface to inspect:
- Each agent's reasoning steps
- Tool calls and responses  
- Session state at each stage
- Full event timeline

---

## Deploy to Cloud Run (one command)

```bash
# Build frontend first
cd frontend && npm run build && cd ..

# Deploy
gcloud run deploy nutriagent \
  --source . \
  --region europe-west2 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=AIzaSy...your_key
```

Or just tell Antigravity's agent: **"Deploy this project to Google Cloud Run"** and it will handle everything.

---

## API Reference

| Method | Endpoint | Body / Params |
|---|---|---|
| POST | `/api/analyze` | `{ food: "eggs", api_key: "AIza..." }` |
| GET | `/api/history` | `?limit=20` |
| GET | `/api/recipe/{id}` | — |
| GET | `/api/health` | — |

---

## Reference
Original repo: https://github.com/renuvkelkar/Health-Agent
Built with: Google ADK · Gemini 2.0 Flash · FastAPI · React · SQLite
