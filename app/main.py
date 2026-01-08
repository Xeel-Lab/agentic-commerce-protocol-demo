# app/main.py
import os
import re
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

logger = logging.getLogger("acp.main")

from .routes.products import router as products_router
from .routes.checkout import router as checkout_router
from .routes.webhooks import router as webhooks_router
from .db import init_db

app = FastAPI(
    title="ACP-style Merchant API",
    version="0.3.0",
    description="ACP-like checkout API for GPT Actions demos. Public OpenAPI at /openapi.json",
)

# Middleware per normalizzare path con doppi slash (es. //products -> /products)
class NormalizePathMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Normalizza doppi slash nel path
        path = request.url.path
        # Sostituisci sequenze di slash multiple con un singolo slash
        normalized_path = re.sub(r'/+', '/', path)
        # Se il path è cambiato, modifica lo scope e ricrea la request
        if normalized_path != path:
            logger.info(f"Normalizing path: {path} -> {normalized_path}")
            # Crea un nuovo scope con il path normalizzato
            scope = dict(request.scope)
            scope["path"] = normalized_path
            # Ricrea la request con il nuovo scope
            request = Request(scope, request.receive)
        response = await call_next(request)
        return response

app.add_middleware(NormalizePathMiddleware)

# CORS: per demo lasciamo tutto aperto (stringi in produzione)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # ✅ 1) Inserisci il server dinamico da ENV (deve essere https)
    base = os.getenv("PUBLIC_BASE_URL", "").strip()
    if base and base.startswith("https://"):
        # Rimuovi trailing slash per evitare doppi slash nello schema OpenAPI
        base = base.rstrip('/')
        schema["servers"] = [{"url": base}]
    else:
        # fallback placeholder (verrà rifiutato dalle Actions se usato)
        schema["servers"] = [{"url": "https://replace-me.example.com"}]

    # ✅ 2) Aggiungi security scheme per API Key su header X-API-Key
    components = schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes["ApiKeyAuth"] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": "Provide your API key in the X-API-Key header."
    }
    # Applica la security **globale** (puoi toglierla se la definisci endpoint-by-endpoint)
    schema["security"] = [{"ApiKeyAuth": []}]

    app.openapi_schema = schema
    return app.openapi_schema

# monta lo schema OpenAPI dinamico
app.openapi = custom_openapi

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

# Routers
app.include_router(products_router, prefix="")
app.include_router(checkout_router, prefix="")
app.include_router(webhooks_router, prefix="")
