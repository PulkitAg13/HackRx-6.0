import openai
import logging
from typing import Union, Dict, Any
from ...backend.app.core.config import settings

logger = logging.getLogger(__name__)

class OpenAIWrapper:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        openai.api_key = settings.OPENAI_API_KEY

    def get_response(
        self,
        prompt: str,
        response_format: str = "text",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Union[str, Dict[str, Any]]:
        try:
            response = openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": response_format} 
                if response_format == "json_object" else None
            )
            
            content = response.choices[0].message.content
            if response_format == "json_object":
                try:
                    return eval(content)
                except:
                    return {"error": "Invalid JSON response"}
            return content
            
        except Exception as e:
            logger.error(f"OpenAI request failed: {str(e)}")
            raise

# Singleton instance
openai_wrapper = OpenAIWrapper()

def get_llm_response(
    prompt: str,
    response_format: str = "text",
    **kwargs
) -> Union[str, Dict[str, Any]]:
    return openai_wrapper.get_response(
        prompt=prompt,
        response_format=response_format,
        **kwargs
    )