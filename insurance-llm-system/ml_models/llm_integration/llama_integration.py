import logging
from typing import Union, Dict, Any
from transformers import AutoTokenizer, AutoModelForCausalLM
from ...backend.config import settings

logger = logging.getLogger(__name__)

class LlamaWrapper:
    def __init__(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.LLAMA_MODEL_NAME,
                cache_dir=settings.MODEL_CACHE_DIR
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.LLAMA_MODEL_NAME,
                cache_dir=settings.MODEL_CACHE_DIR,
                device_map="auto"
            )
            logger.info("Llama model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Llama model: {str(e)}")
            raise

    def get_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True
            )
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Llama inference failed: {str(e)}")
            raise

# Singleton instance
llama_wrapper = LlamaWrapper() if settings.USE_LOCAL_LLM else None

def get_llm_response(
    prompt: str,
    response_format: str = "text",
    **kwargs
) -> Union[str, Dict[str, Any]]:
    if not llama_wrapper:
        raise ValueError("Llama model not initialized")
    
    response = llama_wrapper.get_response(prompt, **kwargs)
    
    if response_format == "json_object":
        try:
            # Basic JSON extraction from response
            start = response.find('{')
            end = response.rfind('}') + 1
            return eval(response[start:end])
        except:
            return {"error": "Could not parse JSON response"}
    return response