from dataclasses import dataclass


@dataclass(frozen=True)
class AIModelConfig:
    name: str
    max_output_tokens: int
    temperature: float


DEFAULT_MODEL_CONFIG = AIModelConfig(
    name="gpt-5.4-mini",
    max_output_tokens=300,
    temperature=0.2,
)
