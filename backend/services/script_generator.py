from typing import Dict, Any, Optional
import re
import json
from bs4 import BeautifulSoup
from .knowledge_base import KnowledgeBase
from .llm_client import GeminiClient

class ScriptGenerator:
    """Generate Selenium test scripts from test cases using AI"""
    
    def __init__(self, knowledge_base: KnowledgeBase, llm_client: Optional[GeminiClient] = None):
        self.knowledge_base = knowledge_base
        self.llm_client = llm_client
    
    def generate_selenium_script(self, test_case: Dict[str, Any], html_content: str) -> str:
        """Generate Selenium Python script from test case and HTML using AI"""
        try:
            # Parse HTML to extract selectors and structure
            soup = BeautifulSoup(html_content, 'html.parser')
            selectors = self._extract_selectors(soup)
            html_structure = self._analyze_html_structure(soup)
            
            # Get additional context from knowledge base
            context = self._get_relevant_context(test_case)
            
            # Try Gemini-powered generation first
            if self.llm_client and self.llm_client.is_configured:
                try:
                    script = self._generate_ai_script(test_case, selectors, html_structure, context)
                    if script:
                        return script
                except Exception as ai_error:
                    print(f"AI script generation failed, falling back to template: {ai_error}")
            
            # Fallback to template-based generation
            script = self._generate_script_template(test_case, selectors, context)
            
            return script
            
        except Exception as e:
            raise Exception(f"Error generating Selenium script: {str(e)}")
    
    def _extract_selectors(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract useful selectors from HTML"""
        selectors = {}
        
        # Common elements to look for
        elements_to_find = {
            'add_to_cart_buttons': 'button[onclick*="addToCart"], .add-to-cart',
            'cart_items': '.cart-item, .item',
            'quantity_inputs': 'input[type="number"], input[name*="quantity"]',
            'discount_input': 'input[name*="discount"], input[id*="discount"], #discountCode',
            'apply_discount_btn': 'button[onclick*="discount"], #applyDiscount',
            'name_input': 'input[name="name"], #name, input[placeholder*="name"]',
            'email_input': 'input[name="email"], #email, input[type="email"]',
            'address_input': 'input[name="address"], #address, textarea[name="address"]',
            'shipping_options': 'input[name="shipping"], input[type="radio"][value*="shipping"]',
            'payment_options': 'input[name="payment"], input[type="radio"][value*="payment"]',
            'pay_button': 'button[onclick*="pay"], #payNow',
            'total_price': '.total, #total, .price-total',
            'error_messages': '.error, .error-message, .validation-error'
        }
        
        # Also look for buttons with specific text content
        pay_buttons = soup.find_all('button')
        for btn in pay_buttons:
            if 'pay now' in btn.get_text().lower():
                elements_to_find['pay_button'] = f"#{btn.get('id')}" if btn.get('id') else f".{btn.get('class')[0]}" if btn.get('class') else 'button'
                break
        
        for key, css_selector in elements_to_find.items():
            elements = soup.select(css_selector)
            if elements:
                element = elements[0]
                # Prefer ID, then name, then class, then tag
                if element.get('id'):
                    selectors[key] = f"#{element['id']}"
                elif element.get('name'):
                    selectors[key] = f"[name='{element['name']}']"
                elif element.get('class'):
                    selectors[key] = f".{element['class'][0]}"
                else:
                    selectors[key] = element.name
        
        return selectors
    
    def _analyze_html_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze HTML structure for AI context"""
        structure = {
            'forms': [],
            'buttons': [],
            'inputs': [],
            'interactive_elements': [],
            'key_sections': []
        }
        
        # Analyze forms
        forms = soup.find_all('form')
        for form in forms:
            form_info = {
                'id': form.get('id'),
                'class': form.get('class'),
                'action': form.get('action'),
                'method': form.get('method'),
                'inputs': []
            }
            
            # Get form inputs
            inputs = form.find_all(['input', 'select', 'textarea'])
            for inp in inputs:
                form_info['inputs'].append({
                    'type': inp.get('type'),
                    'name': inp.get('name'),
                    'id': inp.get('id'),
                    'placeholder': inp.get('placeholder'),
                    'required': inp.has_attr('required')
                })
            
            structure['forms'].append(form_info)
        
        # Analyze buttons
        buttons = soup.find_all('button')
        for btn in buttons:
            structure['buttons'].append({
                'text': btn.get_text(strip=True),
                'id': btn.get('id'),
                'class': btn.get('class'),
                'onclick': btn.get('onclick'),
                'type': btn.get('type')
            })
        
        # Analyze all inputs
        all_inputs = soup.find_all(['input', 'select', 'textarea'])
        for inp in all_inputs:
            structure['inputs'].append({
                'type': inp.get('type'),
                'name': inp.get('name'),
                'id': inp.get('id'),
                'placeholder': inp.get('placeholder'),
                'class': inp.get('class')
            })
        
        # Find key sections
        key_sections = soup.find_all(['div', 'section'], class_=re.compile(r'cart|checkout|payment|form|total'))
        for section in key_sections:
            structure['key_sections'].append({
                'tag': section.name,
                'id': section.get('id'),
                'class': section.get('class'),
                'text_preview': section.get_text(strip=True)[:100]
            })
        
        return structure
    
    def _generate_ai_script(self, test_case: Dict[str, Any], selectors: Dict[str, str], 
                           html_structure: Dict[str, Any], context: str) -> str:
        """Generate Selenium script using Gemini AI"""
        if not self.llm_client or not self.llm_client.is_configured:
            return None
        
        try:
            prompt = self._build_script_generation_prompt(test_case, selectors, html_structure, context)
            response = self.llm_client._model.generate_content(prompt)
            script_content = response.text or ""
            
            # Clean up the response
            script_content = self._clean_ai_response(script_content)
            
            # Validate the generated script
            if self._validate_generated_script(script_content):
                return script_content
            else:
                print("Generated script failed validation, falling back to template")
                return None
                
        except Exception as e:
            print(f"AI script generation error: {e}")
            return None
    
    def _build_script_generation_prompt(self, test_case: Dict[str, Any], selectors: Dict[str, str], 
                                      html_structure: Dict[str, Any], context: str) -> str:
        """Build prompt for AI script generation"""
        return f"""
You are a senior QA automation engineer. Generate a complete, production-ready Selenium Python script based on the test case and HTML structure provided.

TEST CASE DETAILS:
- Test ID: {test_case['test_id']}
- Feature: {test_case['feature']}
- Scenario: {test_case['test_scenario']}
- Expected Result: {test_case['expected_result']}
- Test Type: {test_case.get('test_type', 'positive')}
- Steps: {test_case.get('steps', [])}

AVAILABLE SELECTORS:
{json.dumps(selectors, indent=2)}

HTML STRUCTURE ANALYSIS:
{json.dumps(html_structure, indent=2)}

PROJECT DOCUMENTATION CONTEXT:
{context}

REQUIREMENTS:
1. Generate a complete Python class with proper imports
2. Include setup() method with Chrome WebDriver configuration (headless mode)
3. Include teardown() method for cleanup
4. Create specific test methods based on the test case steps
5. Use explicit waits (WebDriverWait) and proper error handling
6. Include assertions that verify the expected results
7. Add meaningful comments explaining each step
8. Use the most reliable selectors from the provided options (prefer ID > name > class > CSS)
9. Handle edge cases and potential timing issues with time.sleep() when needed
10. Include a run_test() method to execute all tests
11. Make the script executable with proper if __name__ == "__main__" block
12. Use try-except blocks for robust error handling
13. Include print statements for test progress and results (✓ for pass, ✗ for fail)
14. For discount tests: calculate expected totals and verify percentage discounts
15. For form validation: check for error messages and their styling (color)
16. For cart tests: verify item counts and total calculations
17. Update the file path in setup() to use a relative path like "file:///path/to/checkout.html"

SCRIPT STRUCTURE EXAMPLE:
```python
class Test{test_case['test_id'].replace('-', '_')}:
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def setup(self):
        # Chrome driver setup with headless mode
        
    def test_main_functionality(self):
        # Main test logic based on test case steps
        
    def teardown(self):
        # Cleanup
        
    def run_test(self):
        # Execute all tests with proper error handling
```

Generate ONLY the Python script code, no explanations or markdown formatting. Ensure the script is syntactically correct and executable.
"""
    
    def _clean_ai_response(self, script_content: str) -> str:
        """Clean up AI-generated script response"""
        # Remove markdown code blocks if present
        if script_content.startswith("```"):
            lines = script_content.split('\n')
            # Remove first line (```python or ```)
            lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            script_content = '\n'.join(lines)
        
        # Ensure proper indentation and formatting
        script_content = script_content.strip()
        
        return script_content
    
    def _validate_generated_script(self, script_content: str) -> bool:
        """Validate that the generated script has required components"""
        required_components = [
            'import',
            'selenium',
            'webdriver',
            'class Test',
            'def setup',
            'def teardown',
            'def test_',
            'if __name__ == "__main__"'
        ]
        
        script_lower = script_content.lower()
        
        for component in required_components:
            if component.lower() not in script_lower:
                print(f"Missing required component: {component}")
                return False
        
        # Check for basic Python syntax (simple validation)
        try:
            compile(script_content, '<string>', 'exec')
            return True
        except SyntaxError as e:
            print(f"Syntax error in generated script: {e}")
            return False
    
    def _get_relevant_context(self, test_case: Dict[str, Any]) -> str:
        """Get relevant context from knowledge base"""
        query = f"{test_case['feature']} {test_case['test_scenario']}"
        context_chunks = self.knowledge_base.query(query, n_results=5)
        
        context_parts = []
        for chunk in context_chunks:
            source = chunk['metadata'].get('source', 'Unknown')
            text = chunk['text']
            context_parts.append(f"[Source: {source}]\n{text}\n")
        
        return "\n".join(context_parts)
    
    def _generate_script_template(self, test_case: Dict[str, Any], selectors: Dict[str, str], context: str) -> str:
        """Generate the actual Selenium script"""
        feature = test_case['feature'].lower()
        test_type = test_case.get('test_type', 'positive')
        
        # Base script template
        script_parts = [
            self._get_script_header(test_case),
            self._get_setup_code(),
        ]
        
        # Feature-specific test logic
        if 'discount' in feature:
            script_parts.append(self._generate_discount_test(test_case, selectors, test_type))
        elif 'cart' in feature or 'shopping' in feature:
            script_parts.append(self._generate_cart_test(test_case, selectors, test_type))
        elif 'form' in feature or 'validation' in feature:
            script_parts.append(self._generate_form_test(test_case, selectors, test_type))
        elif 'payment' in feature:
            script_parts.append(self._generate_payment_test(test_case, selectors, test_type))
        else:
            script_parts.append(self._generate_generic_test(test_case, selectors))
        
        script_parts.append(self._get_teardown_code())
        
        return "\n".join(script_parts)
    
    def _get_script_header(self, test_case: Dict[str, Any]) -> str:
        """Generate script header with imports and test info"""
        return f'''"""
Test Case: {test_case['test_id']}
Feature: {test_case['feature']}
Scenario: {test_case['test_scenario']}
Expected Result: {test_case['expected_result']}
Grounded In: {test_case['grounded_in']}
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class Test{test_case['test_id'].replace('-', '_')}:
    def __init__(self):
        self.driver = None
        self.wait = None
    '''
    
    def _get_setup_code(self) -> str:
        """Generate setup code"""
        return '''
    def setup(self):
        """Setup Chrome driver and navigate to checkout page"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Remove for visible browser
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # Navigate to checkout page (update path as needed)
        self.driver.get("file:///path/to/checkout.html")
        time.sleep(2)
    '''
    
    def _generate_discount_test(self, test_case: Dict[str, Any], selectors: Dict[str, str], test_type: str) -> str:
        """Generate discount code test logic"""
        discount_input = selectors.get('discount_input', '#discountCode')
        apply_btn = selectors.get('apply_discount_btn', '#applyDiscount')
        total_price = selectors.get('total_price', '.total')
        
        if test_type == 'positive':
            return f'''
    def test_valid_discount_code(self):
        """Test applying valid discount code SAVE15"""
        try:
            # Add items to cart first
            add_to_cart_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "{selectors.get('add_to_cart_buttons', 'button')}")))
            add_to_cart_btn.click()
            time.sleep(1)
            
            # Get original total
            total_element = self.driver.find_element(By.CSS_SELECTOR, "{total_price}")
            original_total = float(total_element.text.replace('$', '').replace(',', ''))
            
            # Apply discount code
            discount_field = self.driver.find_element(By.CSS_SELECTOR, "{discount_input}")
            discount_field.clear()
            discount_field.send_keys("SAVE15")
            
            apply_button = self.driver.find_element(By.CSS_SELECTOR, "{apply_btn}")
            apply_button.click()
            time.sleep(2)
            
            # Verify discount applied (15% off)
            new_total = float(total_element.text.replace('$', '').replace(',', ''))
            expected_total = original_total * 0.85  # 15% discount
            
            assert abs(new_total - expected_total) < 0.01, f"Expected {{expected_total}}, got {{new_total}}"
            print("✓ Valid discount code test passed")
            
        except Exception as e:
            print(f"✗ Valid discount code test failed: {{e}}")
            raise
    '''
        else:
            return f'''
    def test_invalid_discount_code(self):
        """Test applying invalid discount code"""
        try:
            # Add items to cart first
            add_to_cart_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "{selectors.get('add_to_cart_buttons', 'button')}")))
            add_to_cart_btn.click()
            time.sleep(1)
            
            # Apply invalid discount code
            discount_field = self.driver.find_element(By.CSS_SELECTOR, "{discount_input}")
            discount_field.clear()
            discount_field.send_keys("INVALID")
            
            apply_button = self.driver.find_element(By.CSS_SELECTOR, "{apply_btn}")
            apply_button.click()
            time.sleep(2)
            
            # Verify error message appears
            error_elements = self.driver.find_elements(By.CSS_SELECTOR, "{selectors.get('error_messages', '.error')}")
            assert len(error_elements) > 0, "No error message displayed for invalid discount code"
            
            print("✓ Invalid discount code test passed")
            
        except Exception as e:
            print(f"✗ Invalid discount code test failed: {{e}}")
            raise
    '''
    
    def _generate_form_test(self, test_case: Dict[str, Any], selectors: Dict[str, str], test_type: str) -> str:
        """Generate form validation test logic"""
        name_input = selectors.get('name_input', '[name="name"]')
        email_input = selectors.get('email_input', '[name="email"]')
        
        if test_type == 'positive':
            return f'''
    def test_valid_form_submission(self):
        """Test form submission with valid data"""
        try:
            # Fill form with valid data
            name_field = self.driver.find_element(By.CSS_SELECTOR, "{name_input}")
            name_field.clear()
            name_field.send_keys("John Doe")
            
            email_field = self.driver.find_element(By.CSS_SELECTOR, "{email_input}")
            email_field.clear()
            email_field.send_keys("john.doe@example.com")
            
            # Fill address if present
            try:
                address_field = self.driver.find_element(By.CSS_SELECTOR, "{selectors.get('address_input', '[name=\"address\"]')}")
                address_field.clear()
                address_field.send_keys("123 Main St, City, State 12345")
            except NoSuchElementException:
                pass
            
            # Submit form
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "{selectors.get('pay_button', 'button[type=\"submit\"]')}")
            submit_btn.click()
            time.sleep(2)
            
            # Verify no error messages
            error_elements = self.driver.find_elements(By.CSS_SELECTOR, "{selectors.get('error_messages', '.error')}")
            visible_errors = [e for e in error_elements if e.is_displayed()]
            assert len(visible_errors) == 0, f"Unexpected error messages: {{[e.text for e in visible_errors]}}"
            
            print("✓ Valid form submission test passed")
            
        except Exception as e:
            print(f"✗ Valid form submission test failed: {{e}}")
            raise
    '''
        else:
            return f'''
    def test_invalid_email_validation(self):
        """Test form validation with invalid email"""
        try:
            # Fill form with invalid email
            name_field = self.driver.find_element(By.CSS_SELECTOR, "{name_input}")
            name_field.clear()
            name_field.send_keys("John Doe")
            
            email_field = self.driver.find_element(By.CSS_SELECTOR, "{email_input}")
            email_field.clear()
            email_field.send_keys("invalid-email")
            
            # Submit form
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "{selectors.get('pay_button', 'button[type=\"submit\"]')}")
            submit_btn.click()
            time.sleep(2)
            
            # Verify error message appears
            error_elements = self.driver.find_elements(By.CSS_SELECTOR, "{selectors.get('error_messages', '.error')}")
            visible_errors = [e for e in error_elements if e.is_displayed()]
            assert len(visible_errors) > 0, "No error message displayed for invalid email"
            
            # Check if error is red (if specified in documentation)
            error_color = visible_errors[0].value_of_css_property('color')
            print(f"Error message color: {{error_color}}")
            
            print("✓ Invalid email validation test passed")
            
        except Exception as e:
            print(f"✗ Invalid email validation test failed: {{e}}")
            raise
    '''
    
    def _generate_cart_test(self, test_case: Dict[str, Any], selectors: Dict[str, str], test_type: str) -> str:
        """Generate shopping cart test logic"""
        return f'''
    def test_cart_functionality(self):
        """Test adding items to cart and updating quantities"""
        try:
            # Add items to cart
            add_buttons = self.driver.find_elements(By.CSS_SELECTOR, "{selectors.get('add_to_cart_buttons', 'button')}")
            for i, button in enumerate(add_buttons[:2]):  # Add first 2 items
                button.click()
                time.sleep(1)
            
            # Verify items in cart
            cart_items = self.driver.find_elements(By.CSS_SELECTOR, "{selectors.get('cart_items', '.cart-item')}")
            assert len(cart_items) >= 2, f"Expected at least 2 items in cart, found {{len(cart_items)}}"
            
            # Update quantity if quantity inputs exist
            quantity_inputs = self.driver.find_elements(By.CSS_SELECTOR, "{selectors.get('quantity_inputs', 'input[type=\"number\"]')}")
            if quantity_inputs:
                quantity_inputs[0].clear()
                quantity_inputs[0].send_keys("3")
                time.sleep(1)
                
                # Verify total updates (basic check)
                total_element = self.driver.find_element(By.CSS_SELECTOR, "{selectors.get('total_price', '.total')}")
                assert total_element.is_displayed(), "Total price should be visible"
            
            print("✓ Cart functionality test passed")
            
        except Exception as e:
            print(f"✗ Cart functionality test failed: {{e}}")
            raise
    '''
    
    def _generate_payment_test(self, test_case: Dict[str, Any], selectors: Dict[str, str], test_type: str) -> str:
        """Generate payment test logic"""
        return f'''
    def test_payment_process(self):
        """Test payment method selection and processing"""
        try:
            # Select payment method
            payment_options = self.driver.find_elements(By.CSS_SELECTOR, "{selectors.get('payment_options', 'input[name=\"payment\"]')}")
            if payment_options:
                payment_options[0].click()  # Select first payment method
                time.sleep(1)
            
            # Fill required form fields
            name_field = self.driver.find_element(By.CSS_SELECTOR, "{selectors.get('name_input', '[name=\"name\"]')}")
            name_field.clear()
            name_field.send_keys("John Doe")
            
            email_field = self.driver.find_element(By.CSS_SELECTOR, "{selectors.get('email_input', '[name=\"email\"]')}")
            email_field.clear()
            email_field.send_keys("john.doe@example.com")
            
            # Click pay button
            pay_button = self.driver.find_element(By.CSS_SELECTOR, "{selectors.get('pay_button', '#payNow')}")
            
            # Verify button color if specified
            button_color = pay_button.value_of_css_property('background-color')
            print(f"Pay button color: {{button_color}}")
            
            pay_button.click()
            time.sleep(2)
            
            # Look for success message
            success_indicators = [
                "Payment Successful",
                "Order Complete",
                "Thank you"
            ]
            
            page_text = self.driver.page_source
            success_found = any(indicator in page_text for indicator in success_indicators)
            assert success_found, "No payment success indicator found"
            
            print("✓ Payment process test passed")
            
        except Exception as e:
            print(f"✗ Payment process test failed: {{e}}")
            raise
    '''
    
    def _generate_generic_test(self, test_case: Dict[str, Any], selectors: Dict[str, str]) -> str:
        """Generate generic test logic"""
        return f'''
    def test_general_functionality(self):
        """Test general page functionality"""
        try:
            # Verify page loads
            assert "checkout" in self.driver.title.lower() or "shop" in self.driver.title.lower(), "Page title doesn't indicate checkout page"
            
            # Verify key elements are present
            elements_to_check = [
                "{selectors.get('add_to_cart_buttons', 'button')}",
                "{selectors.get('name_input', '[name=\"name\"]')}",
                "{selectors.get('email_input', '[name=\"email\"]')}"
            ]
            
            for selector in elements_to_check:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    assert element.is_displayed(), f"Element {{selector}} is not visible"
                except NoSuchElementException:
                    print(f"Warning: Element {{selector}} not found")
            
            print("✓ General functionality test passed")
            
        except Exception as e:
            print(f"✗ General functionality test failed: {{e}}")
            raise
    '''
    
    def _get_teardown_code(self) -> str:
        """Generate teardown code"""
        return '''
    def teardown(self):
        """Clean up and close browser"""
        if self.driver:
            self.driver.quit()
    
    def run_test(self):
        """Run the complete test"""
        try:
            self.setup()
            
            # Run all test methods
            for method_name in dir(self):
                if method_name.startswith('test_'):
                    print(f"Running {method_name}...")
                    getattr(self, method_name)()
            
            print("\\n✓ All tests completed successfully!")
            
        except Exception as e:
            print(f"\\n✗ Test execution failed: {e}")
        finally:
            self.teardown()

# Run the test
if __name__ == "__main__":
    test = Test''' + '''()
    test.run_test()
'''