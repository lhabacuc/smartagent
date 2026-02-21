
import json
import re
from typing import Any, Dict, Optional

_THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def strip_think_blocks(text: str) -> str:
    """Remove blocos de raciocínio interno no formato <think>...</think>."""
    return _THINK_BLOCK_RE.sub("", text or "")


def safe_json(text: str) -> Optional[Dict[str, Any]]:
    """Extrai JSON de texto, mesmo com markdown ou texto extra"""
    text = strip_think_blocks(text).strip()

    try:
        # Tenta parse direto
        return json.loads(text)
    except Exception:
        pass
    
    # Procura por JSON dentro de markdown ou texto
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```|(\{.*?\})'
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    for match in matches:
        json_str = match[0] or match[1]
        try:
            return json.loads(json_str)
        except Exception:
            continue
    
    return None

def clean_response(text: str) -> str:
    """Remove markdown e formatação extra de respostas"""
    text = strip_think_blocks(text)
    # Remove code blocks
    text = re.sub(r'```[a-z]*\n(.*?)\n```', r'\1', text, flags=re.DOTALL)
    return text.strip()
