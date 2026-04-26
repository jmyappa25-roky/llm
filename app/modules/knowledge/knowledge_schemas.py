from pydantic import BaseModel, Field


class ProductPresentation(BaseModel):
    id: str
    name: str
    size_label: str
    unit: str
    active: bool = True


class ProductKnowledge(BaseModel):
    id: str
    name: str
    category: str
    aliases: list[str] = Field(default_factory=list)
    description: str
    use_cases: list[str] = Field(default_factory=list)
    presentations: list[ProductPresentation] = Field(default_factory=list)
    availability_note: str
    sales_notes: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    active: bool = True


class FAQItem(BaseModel):
    id: str
    question: str
    answer: str
    keywords: list[str] = Field(default_factory=list)
    product_id: str | None = None
    active: bool = True


class PolicyItem(BaseModel):
    id: str
    title: str
    content: str
    keywords: list[str] = Field(default_factory=list)
    active: bool = True


class CommercialRules(BaseModel):
    wholesale_min_quantity: int
    human_approval_quantity: int
    required_quote_fields: list[str]
    sensitive_topics: list[str]
    escalation_keywords: list[str]


class KnowledgeSearchResult(BaseModel):
    products: list[ProductKnowledge] = Field(default_factory=list)
    faqs: list[FAQItem] = Field(default_factory=list)
    policies: list[PolicyItem] = Field(default_factory=list)
