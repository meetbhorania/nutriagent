FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY health_food_agent/ ./health_food_agent/
COPY frontend/dist/ ./frontend/dist/

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "health_food_agent.agent:app", "--host", "0.0.0.0", "--port", "8080"]
