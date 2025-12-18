import json
import os
from typing import List, Dict, Any

from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - handled at runtime
    genai = None

load_dotenv()


class GeminiClient:
    """Wrapper around Google Gemini models used for test generation."""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        env_model = os.getenv("GEMINI_MODEL")
        self.model_name = env_model or model_name
        self.api_key = os.getenv("GEMINI_API_KEY")
        self._model = None
        self._configure_client()

    @property
    def is_configured(self) -> bool:
        """Return True when the API key and SDK are available."""
        return self._model is not None

    def _configure_client(self):
        """Configure Gemini SDK if API key is present."""
        if not self.api_key or genai is None:
            return

        try:
            genai.configure(api_key=self.api_key)
            
            # Try available Gemini model names (based on actual API response)
            model_candidates = [
                self.model_name,
                "gemini-2.5-flash",
                "gemini-2.5-pro", 
                "gemini-2.0-flash-exp",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-pro"
            ]
            
            for model_name in model_candidates:
                try:
                    # Gemini models sometimes require the "models/" prefix
                    model_id = model_name
                    if not model_id.startswith("models/"):
                        model_id = f"models/{model_id}"
                    
                    self._model = genai.GenerativeModel(model_id)
                    self.model_name = model_name  # Update to working model
                    print(f"Successfully configured Gemini model: {model_name}")
                    break
                except Exception as e:
                    print(f"Failed to configure model {model_name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Failed to configure Gemini client: {e}")
            self._model = None

    def generate_test_cases(self, query: str, context: str) -> List[Dict[str, Any]]:
        """Call Gemini to generate structured test cases."""
        if not self.is_configured:
            raise RuntimeError("Gemini client is not configured. Check API key and model availability.")

        try:
            prompt = self._build_prompt(query, context)
            response = self._model.generate_content(prompt)
            output_text = response.text or ""
            return self._parse_response(output_text)
        except Exception as e:
            print(f"Gemini generation failed: {e}")
            raise RuntimeError(f"Gemini API error: {e}")

    def _build_prompt(self, query: str, context: str) -> str:
        """Compose prompt instructing Gemini to produce JSON output."""
        return f"""
You are a senior QA engineer. Use ONLY the documentation provided below to
create detailed UI test cases for the user request.

User request:
\"\"\"{query}\"\"\"

Documentation context:
\"\"\"{context}\"\"\"

Respond with pure JSON: an array of test case objects.
Each object must include the keys: test_id, feature, test_scenario,
expected_result, grounded_in, test_type (positive|negative|exploratory), steps.
The steps value must be an ordered list of actionable steps.
Use concise wording and reference the documents you relied on in grounded_in.
"""

    def _parse_response(self, output_text: str) -> List[Dict[str, Any]]:
        """Normalize Gemini output and convert to Python objects."""
        cleaned = output_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            # Remove optional language prefix like ```json
            cleaned = cleaned.split("\n", 1)[-1]
        try:
            data = json.loads(cleaned)
            if isinstance(data, dict):
                data = [data]
            return data
        except json.JSONDecodeError as exc:
            raise ValueError(f"Gemini response was not valid JSON: {exc}\nRaw output: {output_text}")

