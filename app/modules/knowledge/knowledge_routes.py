from fastapi import APIRouter, Query

from app.core.errors import AppError
from app.modules.knowledge.knowledge_schemas import (
    CommercialRules,
    KnowledgeSearchResult,
    ProductKnowledge,
)
from app.modules.knowledge.knowledge_service import knowledge_service

router = APIRouter(prefix="/api", tags=["knowledge"])


@router.get("/products", response_model=list[ProductKnowledge])
async def get_products() -> list[ProductKnowledge]:
    return knowledge_service.get_products()


@router.get("/products/{product_id}", response_model=ProductKnowledge)
async def get_product(product_id: str) -> ProductKnowledge:
    product = knowledge_service.get_product_by_id(product_id)

    if product is None:
        raise AppError(
            message="Producto no encontrado.",
            status_code=404,
            code="PRODUCT_NOT_FOUND",
        )

    return product


@router.get("/knowledge/search", response_model=KnowledgeSearchResult)
async def search_knowledge(
    query: str = Query(..., min_length=1, max_length=500),
) -> KnowledgeSearchResult:
    return knowledge_service.search(query)


@router.get("/knowledge/rules", response_model=CommercialRules)
async def get_rules() -> CommercialRules:
    return knowledge_service.get_commercial_rules()
