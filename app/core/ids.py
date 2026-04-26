from uuid import uuid4


def new_id(prefix: str) -> str:
    clean_prefix = prefix.strip().lower().replace(" ", "_")
    return f"{clean_prefix}_{uuid4().hex[:12]}"
