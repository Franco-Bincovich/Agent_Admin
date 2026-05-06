import re

_INJECTION_PATTERNS = [
    r"ignore (all |previous |above )?instructions",
    r"forget (everything|all|previous)",
    r"you are now",
    r"act as",
    r"system prompt",
    r"jailbreak",
]


def sanitize_for_prompt(text: str, max_length: int = 8000) -> str:
    """Trunca y elimina patrones de prompt injection antes de incluir en prompt (SEGURIDAD 6.1)."""
    text = text[:max_length]
    for pattern in _INJECTION_PATTERNS:
        text = re.sub(pattern, "[REMOVIDO]", text, flags=re.IGNORECASE)
    return text
