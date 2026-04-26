from app.modules.knowledge.knowledge_schemas import ProductKnowledge, ProductPresentation


PRODUCTS: list[ProductKnowledge] = [
    ProductKnowledge(
        id="miel_maguey",
        name="Miel de maguey",
        category="endulzante_natural",
        aliases=[
            "miel de maguey",
            "miel maguey",
            "jarabe de maguey",
            "endulzante de maguey",
            "miel de agave salmiana",
        ],
        description=(
            "Producto elaborado a partir de aguamiel de maguey. "
            "Puede usarse como alternativa natural para endulzar bebidas, "
            "postres y alimentos."
        ),
        use_cases=[
            "Cafe",
            "Te",
            "Avena",
            "Hot cakes",
            "Panaderia",
            "Reposteria",
            "Bebidas",
            "Uso en cafeterias",
            "Uso en restaurantes",
        ],
        presentations=[
            ProductPresentation(
                id="miel_250ml",
                name="Frasco de miel de maguey 250 ml",
                size_label="250 ml",
                unit="frasco",
            ),
            ProductPresentation(
                id="miel_500ml",
                name="Frasco de miel de maguey 500 ml",
                size_label="500 ml",
                unit="frasco",
            ),
            ProductPresentation(
                id="miel_1l",
                name="Miel de maguey 1 litro",
                size_label="1 litro",
                unit="litro",
            ),
        ],
        availability_note="Consultar disponibilidad antes de confirmar venta.",
        sales_notes=[
            "No inventar precios.",
            "Para cotizacion pedir cantidad, presentacion, zona y fecha.",
            "Puede ofrecerse para cafeterias, restaurantes y venta al publico.",
        ],
        safety_notes=[
            "No prometer beneficios medicos.",
            "No decir que cura enfermedades.",
            "Usar la frase: alternativa natural para endulzar.",
        ],
    ),
    ProductKnowledge(
        id="aguamiel",
        name="Aguamiel",
        category="bebida_natural",
        aliases=[
            "aguamiel",
            "agua miel",
            "agua de maguey",
            "aguamiel de maguey",
        ],
        description=(
            "Bebida natural extraida del maguey. Su disponibilidad depende "
            "de la produccion, temporada y logistica."
        ),
        use_cases=[
            "Consumo directo",
            "Bebidas naturales",
            "Materia prima para derivados del maguey",
        ],
        presentations=[
            ProductPresentation(
                id="aguamiel_1l",
                name="Aguamiel 1 litro",
                size_label="1 litro",
                unit="litro",
            ),
            ProductPresentation(
                id="aguamiel_5l",
                name="Aguamiel 5 litros",
                size_label="5 litros",
                unit="litros",
            ),
        ],
        availability_note="Disponibilidad limitada. Confirmar antes de ofrecer.",
        sales_notes=[
            "Pedir litros requeridos, fecha y zona de entrega.",
            "Confirmar si es para consumo personal, evento o proceso.",
        ],
        safety_notes=[
            "No prometer efectos medicinales.",
            "Mencionar que la disponibilidad puede variar.",
        ],
    ),
    ProductKnowledge(
        id="pulque",
        name="Pulque",
        category="bebida_fermentada",
        aliases=[
            "pulque",
            "pulque natural",
            "curado",
            "curados de pulque",
        ],
        description=(
            "Bebida tradicional fermentada derivada del maguey. "
            "Puede ofrecerse al mayoreo o menudeo segun disponibilidad, "
            "zona y condiciones de entrega."
        ),
        use_cases=[
            "Venta local",
            "Eventos",
            "Mayoreo",
            "Menudeo",
            "Curados",
        ],
        presentations=[
            ProductPresentation(
                id="pulque_1l",
                name="Pulque 1 litro",
                size_label="1 litro",
                unit="litro",
            ),
            ProductPresentation(
                id="pulque_5l",
                name="Pulque 5 litros",
                size_label="5 litros",
                unit="litros",
            ),
            ProductPresentation(
                id="pulque_20l",
                name="Pulque 20 litros",
                size_label="20 litros",
                unit="litros",
            ),
        ],
        availability_note="Consultar disponibilidad, zona y fecha de entrega.",
        sales_notes=[
            "Pedir tipo de pulque, litros, zona y fecha.",
            "Para eventos, pedir numero aproximado de personas.",
        ],
        safety_notes=[
            "No vender a menores.",
            "Validar regulaciones aplicables.",
            "Escalar a humano si hay duda legal o de edad.",
        ],
    ),
    ProductKnowledge(
        id="penca_maguey",
        name="Penca de maguey",
        category="insumo_gastronomico",
        aliases=[
            "penca",
            "penca de maguey",
            "pencas",
            "hoja de maguey",
        ],
        description=(
            "Penca de maguey usada como insumo gastronomico, principalmente "
            "para preparaciones tradicionales."
        ),
        use_cases=[
            "Barbacoa",
            "Cocina tradicional",
            "Eventos",
        ],
        presentations=[
            ProductPresentation(
                id="penca_pieza",
                name="Penca de maguey por pieza",
                size_label="pieza",
                unit="pieza",
            ),
        ],
        availability_note="Consultar disponibilidad y logistica de entrega.",
        sales_notes=[
            "Pedir cantidad de pencas, zona y fecha.",
        ],
        safety_notes=[
            "No prometer disponibilidad sin revisar.",
        ],
    ),
]
