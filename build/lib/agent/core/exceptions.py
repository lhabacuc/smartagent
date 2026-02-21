
class SmartAgentError(Exception):
    """Exceção base para SmartAgent"""
    pass

class AnalysisError(SmartAgentError):
    """Erro durante análise de intenção"""
    pass

class ExecutionError(SmartAgentError):
    """Erro durante execução de ferramentas"""
    pass

class ResponseError(SmartAgentError):
    """Erro durante geração de resposta"""
    pass

class LLMError(SmartAgentError):
    """Erro de comunicação com LLM"""
    pass
