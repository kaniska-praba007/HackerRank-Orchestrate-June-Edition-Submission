from langchain_google_genai import ChatGoogleGenerativeAI
from code.config import GEMINI_API_KEY

def build_gemini_llm(model_name: str, temperature: float = 0, max_tokens: int = 200):
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=GEMINI_API_KEY,
        temperature=temperature,
        max_output_tokens=max_tokens,
    )