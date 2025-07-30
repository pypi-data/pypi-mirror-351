import os
import astor
import requests
from typing import Optional, Dict, Any
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logger = logging.getLogger(__name__)

# API Configuration
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    logger.warning("HF_API_TOKEN not found in environment variables")

HF_API_URL = "https://api-inference.huggingface.co/models/TheStageAI/Elastic-DeepSeek-R1-Distill-Qwen-14B"
FALLBACK_MODEL = "https://api-inference.huggingface.co/models/gpt2"  # Simple fallback

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def query_hf_api(payload: Dict[str, Any], timeout: int = 20) -> Optional[Dict[str, Any]]:
    """Robust API query with retry logic."""
    try:
        response = requests.post(
            HF_API_URL,
            headers=HEADERS,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.warning(f"API request failed: {str(e)}")
        raise

def generate_comment_gpt(ast_node) -> str:
    """
    Generate high-quality comments using Hugging Face API with fallback handling.
    
    Args:
        ast_node: AST node to generate comment for
        
    Returns:
        Generated comment string or fallback message
    """
    if os.getenv('TESTING'):  # Allow for test detection
        return "Mocked GPT comment"
    if not HF_API_TOKEN:
        return "Auto-generated comment (API token not configured)"
    
    try:
        # Convert AST node to code
        code_snippet = astor.to_source(ast_node).strip()
        if not code_snippet:
            return "Auto-generated comment (empty code snippet)"
            
        prompt = (
            "Please generate a concise, professional docstring for this Python code.\n"
            "Focus on what the code does, not how it does it.\n"
            "Format: One complete sentence ending with a period.\n\n"
            f"Code:\n{code_snippet}\n\n"
            "Docstring:"
        )
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.3,
                "do_sample": True,
                "top_p": 0.9
            }
        }
        
        result = query_hf_api(payload)
        
        # Parse response
        if isinstance(result, list):
            generated_text = result[0].get("generated_text", "")
        else:
            generated_text = result.get("generated_text", "")
        
        # Extract just the docstring part
        comment = generated_text[len(prompt):].strip()
        
        # Clean up the response
        comment = comment.split("\n")[0].split(".")[0] + "." if comment else ""
        comment = comment.replace('"""', "").replace("'''", "").strip()
        
        return comment or "Auto-generated comment"
        
    except Exception as e:
        logger.error(f"Comment generation failed: {str(e)}")
        return f"Auto-generated comment (API error: {str(e)})"