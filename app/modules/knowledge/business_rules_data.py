from app.modules.knowledge.knowledge_schemas import CommercialRules


COMMERCIAL_RULES = CommercialRules(
    wholesale_min_quantity=20,
    human_approval_quantity=100,
    required_quote_fields=[
        "producto",
        "cantidad",
        "presentacion",
        "zona_entrega",
        "fecha_requerida",
        "requiere_factura",
        "telefono_contacto",
    ],
    sensitive_topics=[
        "salud",
        "diabetes",
        "cura",
        "medicina",
        "legal",
        "demanda",
        "menor de edad",
        "alcohol",
    ],
    escalation_keywords=[
        "reclamo",
        "queja",
        "reembolso",
        "devolucion",
        "demanda",
        "legal",
        "descuento especial",
        "humano",
        "asesor",
        "molesto",
        "enojado",
    ],
)
