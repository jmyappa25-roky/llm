import re
import unicodedata


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_for_matching(text: str) -> str:
    clean_text = normalize_whitespace(text).lower()
    normalized = unicodedata.normalize("NFD", clean_text)

    return "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )


def extract_possible_quantity(text: str) -> int | None:
    match = re.search(r"\b\d{1,6}\b", text)

    if match is None:
        return None

    try:
        quantity = int(match.group(0))
    except ValueError:
        return None

    if quantity <= 0:
        return None

    return quantity


def extract_email(text: str) -> str | None:
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)

    if match is None:
        return None

    return match.group(0).lower()


def extract_phone(text: str) -> str | None:
    digits = re.sub(r"\D", "", text)

    if len(digits) < 10:
        return None

    if len(digits) > 10:
        return digits[-10:]

    return digits


def has_email(text: str) -> bool:
    return extract_email(text) is not None


def has_phone(text: str) -> bool:
    return extract_phone(text) is not None
