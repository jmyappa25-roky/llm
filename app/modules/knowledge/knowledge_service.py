from app.core.text import normalize_for_matching
from app.modules.knowledge.business_rules_data import COMMERCIAL_RULES
from app.modules.knowledge.faqs_data import FAQS
from app.modules.knowledge.knowledge_schemas import (
    CommercialRules,
    FAQItem,
    KnowledgeSearchResult,
    PolicyItem,
    ProductKnowledge,
)
from app.modules.knowledge.policies_data import POLICIES
from app.modules.knowledge.products_data import PRODUCTS


class KnowledgeService:
    def get_products(self) -> list[ProductKnowledge]:
        return [product for product in PRODUCTS if product.active]

    def get_product_by_id(self, product_id: str) -> ProductKnowledge | None:
        for product in self.get_products():
            if product.id == product_id:
                return product

        return None

    def detect_product(self, text: str) -> ProductKnowledge | None:
        normalized_text = normalize_for_matching(text)

        best_match: ProductKnowledge | None = None
        best_score = 0

        for product in self.get_products():
            search_terms = [
                normalize_for_matching(product.name),
                *[normalize_for_matching(alias) for alias in product.aliases],
            ]

            score = 0

            for term in search_terms:
                if term in normalized_text:
                    score += len(term)

            if score > best_score:
                best_match = product
                best_score = score

        return best_match

    def search_faqs(self, query: str, limit: int = 3) -> list[FAQItem]:
        normalized_query = normalize_for_matching(query)
        scored_faqs: list[tuple[int, FAQItem]] = []

        for faq in FAQS:
            if not faq.active:
                continue

            score = 0

            for keyword in faq.keywords:
                if normalize_for_matching(keyword) in normalized_query:
                    score += 1

            if faq.product_id and faq.product_id in normalized_query:
                score += 2

            if score > 0:
                scored_faqs.append((score, faq))

        scored_faqs.sort(key=lambda item: item[0], reverse=True)

        return [faq for _score, faq in scored_faqs[:limit]]

    def search_policies(self, query: str, limit: int = 3) -> list[PolicyItem]:
        normalized_query = normalize_for_matching(query)
        scored_policies: list[tuple[int, PolicyItem]] = []

        for policy in POLICIES:
            if not policy.active:
                continue

            score = 0

            for keyword in policy.keywords:
                if normalize_for_matching(keyword) in normalized_query:
                    score += 1

            if score > 0:
                scored_policies.append((score, policy))

        scored_policies.sort(key=lambda item: item[0], reverse=True)

        return [policy for _score, policy in scored_policies[:limit]]

    def search(self, query: str) -> KnowledgeSearchResult:
        product = self.detect_product(query)

        products: list[ProductKnowledge] = []
        if product is not None:
            products.append(product)

        return KnowledgeSearchResult(
            products=products,
            faqs=self.search_faqs(query),
            policies=self.search_policies(query),
        )

    def get_commercial_rules(self) -> CommercialRules:
        return COMMERCIAL_RULES


knowledge_service = KnowledgeService()
