from typing import Union, Dict, Any
from .openai_integration import get_llm_response as get_openai_response
from .llama_integration import get_llm_response as get_llama_response
from backend.app.core.config import settings

def get_llm_response(
    prompt: str,
    response_format: str = "text",
    **kwargs
) -> Union[str, Dict[str, Any]]:
    """
    Select appropriate LLM based on configuration
    Args:
        prompt: Input prompt
        response_format: Expected format ('text' or 'json_object')
        **kwargs: Additional model-specific parameters
    Returns:
        Model response in requested format
    """
    if settings.USE_LOCAL_LLM:
        try:
            return get_llama_response(prompt, response_format, **kwargs)
        except Exception as e:
            if settings.FALLBACK_TO_OPENAI:
                return get_openai_response(prompt, response_format, **kwargs)
            raise
    return get_openai_response(prompt, response_format, **kwargs)