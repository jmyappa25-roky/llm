from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.env import settings
from app.core.errors import register_error_handlers
from app.core.logger import configure_logging, get_logger
from app.modules.admin.admin_routes import router as admin_router
from app.modules.ai.ai_routes import router as ai_router
from app.modules.audit.audit_routes import router as audit_router
from app.modules.chat.chat_routes import router as chat_router
from app.modules.customers.customer_routes import router as customer_router
from app.modules.database.database import init_db
from app.modules.inventory.inventory_routes import router as inventory_router
from app.modules.knowledge.knowledge_routes import router as knowledge_router
from app.modules.metrics.metrics_routes import router as metrics_router
from app.modules.orchestration.orchestration_routes import router as orchestration_router
from app.modules.quotes.quote_routes import router as quote_router
from app.modules.rules.rules_routes import router as rules_router
from app.modules.tools.tools_routes import router as tools_router

configure_logging()
logger = get_logger(__name__)

init_db()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend local por capas para atencion al cliente con OpenAI API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(chat_router)
app.include_router(knowledge_router)
app.include_router(rules_router)
app.include_router(orchestration_router)
app.include_router(tools_router)
app.include_router(ai_router)
app.include_router(audit_router)
app.include_router(metrics_router)
app.include_router(admin_router)
app.include_router(quote_router)
app.include_router(inventory_router)
app.include_router(customer_router)


@app.get("/")
async def root() -> dict:
    return {
        "ok": True,
        "message": "Sistema Inteligente de Atencion al Cliente activo",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health")
async def health_check() -> dict:
    return {
        "ok": True,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "ai_mode": settings.AI_MODE,
        "openai_enabled": settings.is_openai_enabled,
        "use_openai_analysis": settings.AI_USE_OPENAI_ANALYSIS,
        "use_openai_reply": settings.AI_USE_OPENAI_REPLY,
        "max_input_chars": settings.MAX_INPUT_CHARS,
        "database_url": settings.DATABASE_URL,
    }


logger.info("Aplicacion inicializada correctamente")
