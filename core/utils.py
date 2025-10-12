
import json
import re
from typing import Any, Dict, Optional

def safe_json(text: str) -> Optional[Dict[str, Any]]:
    """Extrai JSON de texto, mesmo com markdown ou texto extra"""
    try:
        # Tenta parse direto
        return json.loads(text)
    except:
        pass
    
    # Procura por JSON dentro de markdown ou texto
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```|(\{.*?\})'
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    for match in matches:
        json_str = match[0] or match[1]
        try:
            return json.loads(json_str)
        except:
            continue
    
    return None

def clean_response(text: str) -> str:
    """Remove markdown e formatação extra de respostas"""
    # Remove code blocks
    text = re.sub(r'```[a-z]*\n(.*?)\n```', r'\1', text, flags=re.DOTALL)
    return text.strip()
