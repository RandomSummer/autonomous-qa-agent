"""
Selenium Script Generation Agent
Converts test cases into executable Python Selenium scripts.
"""

import re
from pathlib import Path
from typing import List

from backend.services.rag_service import rag_service
from backend.models import TestCase, SeleniumScript, ScriptGenerationResponse
from backend.utils.helpers import generate_script_filename, extract_code_from_markdown
from backend.config import settings

class ScriptGenerationAgent:
    """Generates Selenium Python scripts from test cases.
    Analyzes HTML structure to use correct selectors (IDs, names, etc.).
    """

    def __init__(self) -> None:
        """Initialize with system prompt for script generation."""
        self.system_prompt = """You are an expert Selenium WebDriver (Python) developer.
Your task is to generate clean, executable Selenium test scripts.

CRITICAL REQUIREMENTS:
1. Use the EXACT element selectors (IDs, names, classes) from the provided HTML
2. Generate COMPLETE, RUNNABLE Python code
3. Include proper imports and setup
4. Add explicit waits for element loading
5. Include assertions to verify expected results
6. Add helpful comments
7. Handle common exceptions
8. Use Chrome WebDriver with webdriver-manager:
   service = Service(ChromeDriverManager().install())
   driver = webdriver.Chrome(service=service)
9. Use relative paths for the HTML file:
   current_dir = os.path.dirname(os.path.abspath(__file__))
   html_path = os.path.abspath(os.path.join(current_dir, "..", "uploads", "checkout.html"))
   driver.get(f"file:///{html_path}")
10. Include detailed debug prints and error handling as requested.
"""

    def generate_script(self, test_case: TestCase, html_content: str) -> ScriptGenerationResponse:
        """Generate Selenium script from a test case and HTML.
        Returns a ScriptGenerationResponse.
        """
        try:
            # Extract HTML element information
            html_context = self._extract_html_elements(html_content)

            # Build comprehensive prompt
            user_prompt = f"""Generate a Selenium Python script for this test case:

TEST CASE:
- Test ID: {test_case.test_id}
- Feature: {test_case.feature}
- Scenario: {test_case.test_scenario}
- Type: {test_case.test_type}

TEST STEPS:
{self._format_test_steps(test_case.test_steps)}

EXPECTED RESULT:
{test_case.expected_result}

HTML ELEMENTS AVAILABLE:
{html_context}

FULL HTML CONTEXT (for reference):
{html_content[:2000]}

Generate a complete, executable Selenium script that:
1. Uses the EXACT IDs and names from the HTML above
2. Implements all test steps
3. Includes assertions for the expected result
4. Is ready to run without modifications"""

            # Retrieve additional context from docs if needed
            doc_context = ""
            if getattr(test_case, "grounded_in", None):
                doc_results = rag_service.retrieve_context(
                    query=f"{test_case.feature} {test_case.test_scenario}",
                    n_results=3,
                )
                if doc_results:
                    doc_context = "\n\nRELEVANT DOCUMENTATION:\n" + rag_service.format_context(doc_results)

            # Generate script using LLM
            response = rag_service.generate_response(
                user_query=user_prompt + doc_context,
                context="",  # already included in prompt
                system_prompt=self.system_prompt,
                temperature=0.1,
            )

            # Extract and clean code
            script_content = extract_code_from_markdown(response)
            script_content = self._clean_script(script_content)

            # Generate filename
            filename = generate_script_filename(test_case.test_id)

            # Create SeleniumScript object matching model fields
            script = SeleniumScript(
                test_id=test_case.test_id,
                script_content=script_content,
                filename=filename,
                description=f"Selenium script for test case {test_case.test_id}",
                grounded_in=getattr(test_case, "grounded_in", None),
            )

            # Save to file
            self._save_script(script)

            return ScriptGenerationResponse(
                success=True,
                message=f"Script generated successfully: {filename}",
                script=script,
            )
        except Exception as e:
            return ScriptGenerationResponse(
                success=False,
                message=f"Error generating script: {str(e)}",
                script=None,
            )

    def _extract_html_elements(self, html_content: str) -> str:
        """Extract key HTML elements (forms, inputs, buttons) for LLM context.
        Returns a formatted string.
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, "lxml")
        elements: List[str] = []
        for form in soup.find_all("form"):
            form_id = form.get("id", "no-id")
            elements.append(f"\nFORM: id='{form_id}'")
            for inp in form.find_all(["input", "textarea", "select"]):
                inp_type = inp.get("type", "text")
                inp_id = inp.get("id", "")
                inp_name = inp.get("name", "")
                inp_placeholder = inp.get("placeholder", "")
                info = f"  - {inp.name.upper()}"
                if inp_id:
                    info += f" id='{inp_id}'"
                if inp_name:
                    info += f" name='{inp_name}'"
                if inp_type != "text":
                    info += f" type='{inp_type}'"
                if inp_placeholder:
                    info += f" placeholder='{inp_placeholder}'"
                elements.append(info)
            for btn in form.find_all(["button", "input"]):
                if btn.name == "button" or btn.get("type") in ["submit", "button"]:
                    btn_id = btn.get("id", "")
                    btn_text = btn.get_text(strip=True) or btn.get("value", "")
                    btn_type = btn.get("type", "button")
                    info = "  - BUTTON"
                    if btn_id:
                        info += f" id='{btn_id}'"
                    info += f" type='{btn_type}'"
                    if btn_text:
                        info += f" text='{btn_text}'"
                    elements.append(info)
        for btn in soup.find_all("button"):
            if not btn.find_parent("form"):
                btn_id = btn.get("id", "")
                btn_text = btn.get_text(strip=True)
                if btn_id:
                    elements.append(f"\nBUTTON (standalone): id='{btn_id}' text='{btn_text}'")
        return "\n".join(elements) if elements else "No specific elements found"

    def _format_test_steps(self, steps: List[str]) -> str:
        """Format test steps as a numbered list."""
        return "\n".join([f"{i + 1}. {step}" for i, step in enumerate(steps)])

    def _clean_script(self, script: str) -> str:
        """Clean up generated script: remove markdown artifacts and ensure imports."""
        script = re.sub(r"```python|```", "", script)
        script = script.strip()
        if not script.startswith("from") and not script.startswith("import"):
            imports = """from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

"""
            script = imports + script
        return script

    def _save_script(self, script: SeleniumScript) -> Path:
        """Save generated script to file and return the path."""
        output_path = settings.OUTPUT_PATH / script.filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(script.script_content)
        print(f"[SAVE] Script saved: {output_path}")
        return output_path

    def generate_multiple_scripts(self, test_cases: List[TestCase], html_content: str) -> List[ScriptGenerationResponse]:
        """Generate scripts for multiple test cases."""
        responses: List[ScriptGenerationResponse] = []
        for i, test_case in enumerate(test_cases):
            print(f"\n[GEN] Generating script {i + 1}/{len(test_cases)}: {test_case.test_id}")
            response = self.generate_script(test_case, html_content)
            responses.append(response)
        return responses

# Singleton instance
script_agent = ScriptGenerationAgent()
