from typing import List, Dict, Any, Optional
import json
import re
from .knowledge_base import KnowledgeBase
from .llm_client import GeminiClient

class TestGenerator:
    """Generate test cases based on documentation and user queries"""
    
    def __init__(self, knowledge_base: KnowledgeBase, llm_client: Optional[GeminiClient] = None):
        self.knowledge_base = knowledge_base
        self.llm_client = llm_client
    
    def generate_test_cases(self, query: str) -> List[Dict[str, Any]]:
        """Generate test cases based on query and retrieved context"""
        try:
            # Retrieve relevant context from knowledge base
            context_chunks = self.knowledge_base.query(query, n_results=8)
            
            if not context_chunks:
                return [{
                    "test_id": "TC-001",
                    "feature": "General",
                    "test_scenario": "No relevant documentation found",
                    "expected_result": "Please upload relevant documentation first",
                    "grounded_in": "No source",
                    "test_type": "informational"
                }]
            
            # Build context string
            context = self._build_context_string(context_chunks)
            
            # Try LLM-backed generation first when configured
            if self.llm_client and self.llm_client.is_configured:
                try:
                    test_cases = self.llm_client.generate_test_cases(query, context)
                    if test_cases:
                        return test_cases
                except Exception as llm_error:
                    print(f"Gemini generation failed, falling back to rule-based logic: {llm_error}")
            
            # Fallback to rule-based generation
            test_cases = self._generate_rule_based_test_cases(query, context, context_chunks)
            
            return test_cases
            
        except Exception as e:
            raise Exception(f"Error generating test cases: {str(e)}")
    
    def _build_context_string(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []
        for chunk in context_chunks:
            source = chunk['metadata']['source']
            text = chunk['text']
            context_parts.append(f"[Source: {source}]\n{text}\n")
        
        return "\n".join(context_parts)
    
    def _generate_rule_based_test_cases(self, query: str, context: str, context_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate test cases using rule-based approach"""
        test_cases = []
        
        # Extract features and rules from context
        features = self._extract_features(context, query)
        
        test_id_counter = 1
        
        for feature_name, feature_info in features.items():
            # Generate positive test cases
            positive_cases = self._generate_positive_test_cases(
                feature_name, feature_info, test_id_counter
            )
            test_cases.extend(positive_cases)
            test_id_counter += len(positive_cases)
            
            # Generate negative test cases
            negative_cases = self._generate_negative_test_cases(
                feature_name, feature_info, test_id_counter
            )
            test_cases.extend(negative_cases)
            test_id_counter += len(negative_cases)
        
        return test_cases if test_cases else self._generate_generic_test_cases(query, context_chunks)
    
    def _extract_features(self, context: str, query: str) -> Dict[str, Dict[str, Any]]:
        """Extract features and their specifications from context"""
        features = {}
        
        # Common e-commerce features to look for
        feature_patterns = {
            'discount_code': ['discount', 'coupon', 'promo', 'save15'],
            'cart': ['cart', 'add to cart', 'quantity', 'item'],
            'shipping': ['shipping', 'delivery', 'standard', 'express'],
            'payment': ['payment', 'credit card', 'paypal', 'pay now'],
            'form_validation': ['validation', 'error', 'required', 'email'],
            'user_details': ['name', 'email', 'address', 'user']
        }
        
        for feature, keywords in feature_patterns.items():
            if any(keyword.lower() in context.lower() or keyword.lower() in query.lower() for keyword in keywords):
                features[feature] = self._extract_feature_rules(feature, context)
        
        return features
    
    def _extract_feature_rules(self, feature: str, context: str) -> Dict[str, Any]:
        """Extract specific rules for a feature from context"""
        rules = {'source_docs': [], 'specifications': []}
        
        # Extract source documents
        source_pattern = r'\[Source: ([^\]]+)\]'
        sources = re.findall(source_pattern, context)
        rules['source_docs'] = list(set(sources))
        
        # Feature-specific rule extraction
        if feature == 'discount_code':
            if 'save15' in context.lower() and '15%' in context.lower():
                rules['specifications'].append('SAVE15 code applies 15% discount')
            if 'discount' in context.lower():
                rules['specifications'].append('Discount code functionality available')
        
        elif feature == 'shipping':
            if 'express' in context.lower() and '$10' in context:
                rules['specifications'].append('Express shipping costs $10')
            if 'standard' in context.lower() and 'free' in context.lower():
                rules['specifications'].append('Standard shipping is free')
        
        elif feature == 'form_validation':
            if 'red' in context.lower() and 'error' in context.lower():
                rules['specifications'].append('Error messages displayed in red')
            if 'required' in context.lower():
                rules['specifications'].append('Required field validation')
        
        elif feature == 'payment':
            if 'green' in context.lower() and 'pay now' in context.lower():
                rules['specifications'].append('Pay Now button should be green')
        
        return rules
    
    def _generate_positive_test_cases(self, feature: str, feature_info: Dict[str, Any], start_id: int) -> List[Dict[str, Any]]:
        """Generate positive test cases for a feature"""
        test_cases = []
        
        if feature == 'discount_code':
            test_cases.append({
                'test_id': f'TC-{start_id:03d}',
                'feature': 'Discount Code',
                'test_scenario': 'Apply valid discount code SAVE15',
                'expected_result': 'Total price is reduced by 15%',
                'grounded_in': ', '.join(feature_info['source_docs']),
                'test_type': 'positive',
                'steps': [
                    'Add items to cart',
                    'Navigate to checkout',
                    'Enter discount code "SAVE15"',
                    'Click apply',
                    'Verify 15% discount is applied'
                ]
            })
        
        elif feature == 'cart':
            test_cases.append({
                'test_id': f'TC-{start_id:03d}',
                'feature': 'Shopping Cart',
                'test_scenario': 'Add items to cart and update quantities',
                'expected_result': 'Cart updates correctly with new quantities and totals',
                'grounded_in': ', '.join(feature_info['source_docs']),
                'test_type': 'positive',
                'steps': [
                    'Click "Add to Cart" for multiple items',
                    'Verify items appear in cart',
                    'Update item quantities',
                    'Verify total price updates correctly'
                ]
            })
        
        elif feature == 'form_validation':
            test_cases.append({
                'test_id': f'TC-{start_id:03d}',
                'feature': 'Form Validation',
                'test_scenario': 'Submit form with valid data',
                'expected_result': 'Form submits successfully without errors',
                'grounded_in': ', '.join(feature_info['source_docs']),
                'test_type': 'positive',
                'steps': [
                    'Fill all required fields with valid data',
                    'Enter valid email format',
                    'Click submit',
                    'Verify successful submission'
                ]
            })
        
        return test_cases
    
    def _generate_negative_test_cases(self, feature: str, feature_info: Dict[str, Any], start_id: int) -> List[Dict[str, Any]]:
        """Generate negative test cases for a feature"""
        test_cases = []
        
        if feature == 'discount_code':
            test_cases.append({
                'test_id': f'TC-{start_id:03d}',
                'feature': 'Discount Code',
                'test_scenario': 'Apply invalid discount code',
                'expected_result': 'Error message displayed, no discount applied',
                'grounded_in': ', '.join(feature_info['source_docs']),
                'test_type': 'negative',
                'steps': [
                    'Add items to cart',
                    'Navigate to checkout',
                    'Enter invalid discount code "INVALID"',
                    'Click apply',
                    'Verify error message appears'
                ]
            })
        
        elif feature == 'form_validation':
            test_cases.extend([
                {
                    'test_id': f'TC-{start_id:03d}',
                    'feature': 'Form Validation',
                    'test_scenario': 'Submit form with invalid email',
                    'expected_result': 'Email validation error displayed in red',
                    'grounded_in': ', '.join(feature_info['source_docs']),
                    'test_type': 'negative',
                    'steps': [
                        'Fill form with invalid email format',
                        'Click submit',
                        'Verify red error message for email field'
                    ]
                },
                {
                    'test_id': f'TC-{start_id+1:03d}',
                    'feature': 'Form Validation',
                    'test_scenario': 'Submit form with empty required fields',
                    'expected_result': 'Required field errors displayed',
                    'grounded_in': ', '.join(feature_info['source_docs']),
                    'test_type': 'negative',
                    'steps': [
                        'Leave required fields empty',
                        'Click submit',
                        'Verify required field error messages'
                    ]
                }
            ])
        
        return test_cases
    
    def _generate_generic_test_cases(self, query: str, context_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate generic test cases when specific features aren't detected"""
        sources = list(set([chunk['metadata']['source'] for chunk in context_chunks]))
        
        return [{
            'test_id': 'TC-001',
            'feature': 'General Functionality',
            'test_scenario': f'Test functionality related to: {query}',
            'expected_result': 'System behaves according to documentation specifications',
            'grounded_in': ', '.join(sources),
            'test_type': 'exploratory',
            'steps': [
                'Review relevant documentation',
                'Identify key functionality to test',
                'Execute test scenarios',
                'Verify expected behavior'
            ]
        }]