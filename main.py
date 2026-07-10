import logging
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.api.routes import generate, conversations
from app.api.routes import models, health
from app.db.session import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Cloudflare AI-Service")

Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(generate.router)
app.include_router(conversations.router)
app.include_router(models.router)
app.include_router(health.router)