from app.modules.knowledge.knowledge_schemas import FAQItem


FAQS: list[FAQItem] = [
    FAQItem(
        id="faq_miel_usos",
        question="Para que sirve la miel de maguey?",
        answer=(
            "La miel de maguey puede usarse como alternativa natural para "
            "endulzar cafe, te, avena, postres, panaderia y bebidas. "
            "No debe considerarse un tratamiento medico."
        ),
        keywords=[
            "sirve",
            "uso",
            "usar",
            "miel",
            "endulzar",
            "cafe",
            "postres",
        ],
        product_id="miel_maguey",
    ),
    FAQItem(
        id="faq_precio",
        question="Cual es el precio?",
        answer=(
            "Para dar precio correcto se debe confirmar producto, cantidad, "
            "presentacion, zona de entrega y fecha requerida."
        ),
        keywords=[
            "precio",
            "cuanto cuesta",
            "costo",
            "cuanto vale",
            "mayoreo",
        ],
    ),
    FAQItem(
        id="faq_mayoreo",
        question="Manejan mayoreo?",
        answer=(
            "Si, se puede revisar cotizacion de mayoreo. Para prepararla "
            "se requiere producto, cantidad, presentacion, zona de entrega, "
            "fecha requerida y si necesita factura."
        ),
        keywords=[
            "mayoreo",
            "distribuidor",
            "cafeteria",
            "restaurante",
            "cantidad",
        ],
    ),
    FAQItem(
        id="faq_envios",
        question="Tienen envio?",
        answer=(
            "La entrega depende de la zona, producto, cantidad y fecha. "
            "Antes de confirmar se debe revisar disponibilidad y logistica."
        ),
        keywords=[
            "envio",
            "entrega",
            "domicilio",
            "mandan",
            "zona",
        ],
    ),
    FAQItem(
        id="faq_aguamiel_disponibilidad",
        question="Tienen aguamiel disponible?",
        answer=(
            "El aguamiel depende de produccion, temporada y logistica. "
            "Se debe confirmar litros requeridos, fecha y zona de entrega."
        ),
        keywords=[
            "aguamiel",
            "disponible",
            "litros",
            "temporada",
        ],
        product_id="aguamiel",
    ),
    FAQItem(
        id="faq_pulque",
        question="Venden pulque?",
        answer=(
            "Se puede revisar disponibilidad de pulque natural o curados, "
            "segun zona, litros requeridos y fecha. No se vende a menores."
        ),
        keywords=[
            "pulque",
            "curado",
            "curados",
            "litros",
            "evento",
        ],
        product_id="pulque",
    ),
]
