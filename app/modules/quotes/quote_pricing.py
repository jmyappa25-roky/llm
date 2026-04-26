from dataclasses import dataclass


@dataclass(frozen=True)
class ProductPriceRule:
    product_id: str
    unit_price_mxn: float
    wholesale_discount_percent: float
    wholesale_min_quantity: int


PRODUCT_PRICE_RULES: dict[str, ProductPriceRule] = {
    "miel_maguey": ProductPriceRule(
        product_id="miel_maguey",
        unit_price_mxn=145.0,
        wholesale_discount_percent=10.0,
        wholesale_min_quantity=20,
    ),
    "aguamiel": ProductPriceRule(
        product_id="aguamiel",
        unit_price_mxn=60.0,
        wholesale_discount_percent=8.0,
        wholesale_min_quantity=20,
    ),
    "pulque": ProductPriceRule(
        product_id="pulque",
        unit_price_mxn=55.0,
        wholesale_discount_percent=5.0,
        wholesale_min_quantity=20,
    ),
    "penca_maguey": ProductPriceRule(
        product_id="penca_maguey",
        unit_price_mxn=35.0,
        wholesale_discount_percent=5.0,
        wholesale_min_quantity=20,
    ),
}


def get_price_rule(product_id: str) -> ProductPriceRule | None:
    return PRODUCT_PRICE_RULES.get(product_id)
