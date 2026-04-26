from app.modules.knowledge.knowledge_schemas import PolicyItem


POLICIES: list[PolicyItem] = [
    PolicyItem(
        id="policy_no_inventar_precios",
        title="No inventar precios",
        content=(
            "El sistema no debe inventar precios. Si el cliente pregunta precio, "
            "debe pedir producto, cantidad, presentacion, zona de entrega y fecha."
        ),
        keywords=[
            "precio",
            "costo",
            "cuanto cuesta",
            "cotizacion",
        ],
    ),
    PolicyItem(
        id="policy_no_promesas_medicas",
        title="No prometer beneficios medicos",
        content=(
            "El sistema no debe prometer curas, tratamientos o beneficios medicos. "
            "Puede decir que la miel de maguey es una alternativa natural para endulzar, "
            "pero no debe presentarla como medicamento."
        ),
        keywords=[
            "salud",
            "diabetes",
            "cura",
            "medicina",
            "beneficio",
        ],
    ),
    PolicyItem(
        id="policy_mayoreo",
        title="Cotizaciones de mayoreo",
        content=(
            "Para mayoreo se debe pedir producto, cantidad, presentacion, zona, "
            "fecha requerida, factura y telefono de contacto. Pedidos grandes "
            "pueden requerir revision humana."
        ),
        keywords=[
            "mayoreo",
            "distribuidor",
            "cafeteria",
            "restaurante",
            "cotizacion",
        ],
    ),
    PolicyItem(
        id="policy_escalamiento",
        title="Escalamiento humano",
        content=(
            "Se debe escalar a humano cuando exista reclamo, reembolso, queja, "
            "duda legal, tema medico, descuento especial o pedido de alto volumen."
        ),
        keywords=[
            "reclamo",
            "reembolso",
            "queja",
            "legal",
            "descuento",
            "humano",
        ],
    ),
    PolicyItem(
        id="policy_pulque_menores",
        title="Pulque y menores de edad",
        content=(
            "El sistema no debe vender pulque a menores de edad. Si existe duda "
            "sobre edad, se debe escalar o solicitar validacion humana."
        ),
        keywords=[
            "pulque",
            "menor",
            "edad",
            "alcohol",
        ],
    ),
]
