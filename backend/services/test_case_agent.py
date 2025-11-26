"""
Test Case Generation Agent
Uses RAG to generate documentation-grounded test cases.
Key requirement: NO HALLUCINATIONS - all test cases must reference source docs.
"""

import json
import re
from typing import List, Dict, Any

from backend.services.rag_service import rag_service
from backend.models import TestCase, TestCaseResponse
from backend.utils.helpers import generate_test_id


class TestCaseAgent:
    """
    Generates test cases by combining RAG retrieval with LLM reasoning.
    Ensures all test cases are grounded in provided documentation.
    """

    def __init__(self):
        """Initialize with system prompt for test case generation."""
        # System prompt defines agent's role and output format
        self.system_prompt = """You are an expert QA Test Case Designer.

Your task is to generate comprehensive, documentation-grounded test cases.

CRITICAL RULES:
1. Base ALL test cases ONLY on the provided documentation
2. DO NOT invent, assume, or hallucinate any features not mentioned in docs
3. Each test case MUST reference which document(s) it's based on
4. Include both positive and negative test scenarios
5. Be specific and actionable

OUTPUT FORMAT:
Return test cases as a JSON array with this structure:
[
  {
    "test_id": "TC-001",
    "feature": "Feature name",
    "test_scenario": "Detailed scenario description",
    "test_type": "positive|negative|edge_case",
    "preconditions": "Setup required before test",
    "test_steps": [
      "Step 1: Action to perform",
      "Step 2: Next action",
      "Step 3: Verification"
    ],
    "expected_result": "What should happen",
    "grounded_in": "Exact source document name (e.g., product_specs.md)"
  }
]

Generate clear, testable scenarios that can be automated with Selenium."""

    def generate_test_cases(
            self,
            user_query: str,
            include_negative: bool = True
    ) -> TestCaseResponse:
        """
        Generate test cases based on user query and documentation.

        Process:
        1. Use RAG to retrieve relevant documentation
        2. Send to LLM with structured prompt
        3. Parse JSON response into TestCase objects
        4. Validate that all cases reference source docs

        Args:
            user_query: What to test (e.g., "discount code feature")
            include_negative: Whether to include negative test cases

        Returns:
            TestCaseResponse with list of TestCase objects

        Example:
            response = agent.generate_test_cases(
                "Generate test cases for discount code validation"
            )
            for tc in response.test_cases:
                print(tc.test_id, tc.feature)
        """
        try:
            # Enhance query if needed
            enhanced_query = user_query
            if include_negative:
                enhanced_query += " Include both positive and negative test scenarios."

            # Use RAG to get relevant context and generate response
            rag_result = rag_service.rag_query(
                user_query=enhanced_query,
                system_prompt=self.system_prompt,
                n_results=8,  # Get more context for test generation
                temperature=0.1  # Low temperature for structured output
            )

            response_text = rag_result['response']

            # Parse JSON from response
            test_cases_data = self._extract_json_from_response(response_text)

            if not test_cases_data:
                return TestCaseResponse(
                    success=False,
                    message="Failed to parse test cases from LLM response",
                    test_cases=[],
                    total_cases=0
                )

            # Convert to TestCase objects with validation
            test_cases = []
            for i, tc_data in enumerate(test_cases_data):
                try:
                    # Ensure test_id exists
                    if 'test_id' not in tc_data:
                        tc_data['test_id'] = generate_test_id(i + 1)

                    # Validate grounded_in field exists
                    if 'grounded_in' not in tc_data or not tc_data['grounded_in']:
                        # Try to infer from retrieved chunks
                        tc_data['grounded_in'] = self._infer_source_documents(
                            rag_result['retrieved_chunks']
                        )

                    # Create TestCase object (Pydantic validates structure)
                    test_case = TestCase(**tc_data)
                    test_cases.append(test_case)

                except Exception as e:
                    print(f"[WARN] Skipping invalid test case: {str(e)}")
                    continue

            if not test_cases:
                return TestCaseResponse(
                    success=False,
                    message="No valid test cases generated",
                    test_cases=[],
                    total_cases=0
                )

            return TestCaseResponse(
                success=True,
                message=f"Generated {len(test_cases)} test cases",
                test_cases=test_cases,
                total_cases=len(test_cases)
            )

        except Exception as e:
            return TestCaseResponse(
                success=False,
                message=f"Error generating test cases: {str(e)}",
                test_cases=[],
                total_cases=0
            )

    def _extract_json_from_response(self, response_text: str) -> List[Dict]:
        """
        Extract JSON array from LLM response.
        LLM might wrap JSON in markdown code blocks or add text.

        Args:
            response_text: Raw LLM response

        Returns:
            Parsed JSON list or None
        """
        try:
            # Try to find JSON array in response
            # Pattern 1: Look for ```json blocks
            json_pattern = r'```json\s*(.*?)\s*```'
            match = re.search(json_pattern, response_text, re.DOTALL)

            if match:
                json_str = match.group(1)
            else:
                # Pattern 2: Look for [ ... ] array
                array_pattern = r'\[.*\]'
                match = re.search(array_pattern, response_text, re.DOTALL)
                if match:
                    json_str = match.group(0)
                else:
                    # Pattern 3: Try entire response
                    json_str = response_text

            # Parse JSON
            data = json.loads(json_str)

            # Ensure it's a list
            if isinstance(data, dict):
                # If single test case, wrap in list
                data = [data]

            return data

        except json.JSONDecodeError as e:
            print(f"[WARN] JSON parsing error: {str(e)}")
            print(f"Response text: {response_text[:500]}...")
            return None

    def _infer_source_documents(self, retrieved_chunks: List[Dict]) -> str:
        """
        Infer source documents from retrieved chunks.
        Fallback when LLM doesn't specify grounded_in.

        Args:
            retrieved_chunks: List of chunks from RAG retrieval

        Returns:
            Comma-separated list of source documents
        """
        if not retrieved_chunks:
            return "documentation"

        sources = set()
        for chunk in retrieved_chunks[:3]:  # Top 3 sources
            source = chunk.get('source_document', '')
            if source:
                sources.add(source)

        return ", ".join(sorted(sources)) if sources else "documentation"

    def generate_test_cases_for_feature(
            self,
            feature_name: str,
            html_content: str = None
    ) -> TestCaseResponse:
        """
        Generate test cases for a specific feature.
        Can include HTML context for more accurate test generation.

        Args:
            feature_name: Name of feature to test
            html_content: Optional HTML to understand UI structure

        Returns:
            TestCaseResponse with generated test cases
        """
        query = f"Generate comprehensive test cases for the {feature_name} feature."

        if html_content:
            query += f"\n\nConsider the following HTML structure:\n{html_content[:1000]}"

        return self.generate_test_cases(query, include_negative=True)


# Singleton instance
test_case_agent = TestCaseAgent()