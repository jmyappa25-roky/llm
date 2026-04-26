from app.modules.knowledge.knowledge_service import knowledge_service


def build_analysis_prompt(
    message: str,
    local_product: str | None,
    local_quantity: int | None,
) -> str:
    products = knowledge_service.get_products()
    product_lines = []

    for product in products:
        aliases = ", ".join(product.aliases)
        product_lines.append(
            f"- {product.id}: {product.name}. Aliases: {aliases}"
        )

    product_catalog_text = "\n".join(product_lines)

    return f"""
Analiza el siguiente mensaje de cliente.

Mensaje:
{message}

Producto detectado localmente:
{local_product}

Cantidad detectada localmente:
{local_quantity}

Catalogo permitido:
{product_catalog_text}

Devuelve un JSON con estos campos:
- intent
- customer_type
- product
- quantity
- urgency
- needs_human
- missing_data
- safety_flags
- reply_suggestion
- confidence

Valores permitidos para intent:
saludo, informacion_producto, precio, cotizacion_mayoreo, venta_menudeo, envio, disponibilidad, reclamo, soporte_pedido, reembolso, facturacion, humano, otro

Valores permitidos para customer_type:
desconocido, menudeo, mayoreo, distribuidor, restaurante, cafeteria, evento, cliente_molesto

Valores permitidos para product:
none, miel_maguey, aguamiel, pulque, penca_maguey

Valores permitidos para urgency:
baja, media, alta

Reglas para missing_data:
- Para precio, envio o cotizacion_mayoreo pueden faltar: producto, cantidad, presentacion, zona_entrega.
- Para cotizacion_mayoreo tambien pueden faltar: fecha_requerida, requiere_factura, telefono_contacto.
- Para reclamo o reembolso pueden faltar: numero_pedido, medio_contacto.

Responde solo el JSON.
"""
