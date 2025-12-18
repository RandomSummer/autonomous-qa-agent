"""
Sample Generated Test Script - Discount Code Validation
Test Case: TC-001
Feature: Discount Code
Scenario: Apply valid discount code SAVE15
Expected Result: Total price is reduced by 15%
"""

import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException


class TestTC_001:
    def __init__(self):
        self.driver = None
        self.wait = None

    # ---------- helpers ----------
    def _find_checkout_file(self) -> Path:
        """
        Try common locations for checkout.html.
        Prefer tests/assets/checkout.html based on your repo structure.
        """
        script_dir = Path(__file__).resolve().parent

        candidates = [
            script_dir / "assets" / "checkout.html",          # tests/assets/checkout.html (recommended)
            script_dir / "checkout.html",                     # tests/checkout.html
            script_dir.parent / "tests" / "assets" / "checkout.html",
            script_dir.parent / "tests" / "checkout.html",
            script_dir.parent / "checkout.html",              # repo_root/checkout.html (if you keep it there)
        ]

        for p in candidates:
            if p.exists():
                return p.resolve()

        raise FileNotFoundError(
            "checkout.html not found. Tried:\n" + "\n".join(str(p) for p in candidates)
        )

    def _get_total_value(self) -> float:
        text = self.driver.find_element(By.ID, "total").text  # e.g., "Total: $29.99"
        text = text.replace("Total:", "").replace("$", "").replace(",", "").strip()
        return float(text)

    # ---------- lifecycle ----------
    def setup(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")  # optional

        # Only add these on Linux/mac. On Windows they can cause instability.
        if os.name != "nt":
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)

        checkout_file = self._find_checkout_file()
        self.driver.get(checkout_file.as_uri())

        # Fail fast if page didn't load correctly
        self.wait.until(EC.presence_of_element_located((By.ID, "discountCode")))
        self.wait.until(EC.presence_of_element_located((By.ID, "total")))

    # ---------- tests ----------
    def test_valid_discount_code(self):
        try:
            # Click first Add to Cart button
            add_to_cart_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick*='addToCart']"))
            )
            add_to_cart_btn.click()

            # Wait until total updates from 0.00
            self.wait.until(lambda d: self._get_total_value() > 0.0)
            original_total = self._get_total_value()

            # Apply valid discount
            discount_field = self.wait.until(EC.element_to_be_clickable((By.ID, "discountCode")))
            discount_field.clear()
            discount_field.send_keys("SAVE15")

            apply_button = self.driver.find_element(By.ID, "applyDiscount")
            apply_button.click()

            expected_total = round(original_total * 0.85, 2)

            # Wait until total reflects discount (may update async)
            self.wait.until(lambda d: abs(self._get_total_value() - expected_total) < 0.01)

            new_total = self._get_total_value()
            assert abs(new_total - expected_total) < 0.01, f"Expected {expected_total}, got {new_total}"
            print("✓ Valid discount code test passed")

        except Exception as e:
            print(f"✗ Valid discount code test failed: {e}")
            raise

    def test_invalid_discount_code(self):
        try:
            discount_field = self.wait.until(EC.element_to_be_clickable((By.ID, "discountCode")))
            discount_field.clear()
            discount_field.send_keys("INVALID")

            self.driver.find_element(By.ID, "applyDiscount").click()

            # Wait for error to be visible
            err = self.wait.until(EC.visibility_of_element_located((By.ID, "discountError")))
            assert "Invalid discount code" in err.text, f"Unexpected error text: {err.text!r}"
            print("✓ Invalid discount code test passed")

        except Exception as e:
            print(f"✗ Invalid discount code test failed: {e}")
            raise

    def teardown(self):
        if self.driver:
            try:
                self.driver.quit()
            except WebDriverException:
                # If Chrome already crashed/disconnected, don't throw during cleanup
                pass

    def run_test(self):
        try:
            self.setup()

            print("Running test_valid_discount_code...")
            self.test_valid_discount_code()

            print("Running test_invalid_discount_code...")
            self.test_invalid_discount_code()

            print("\n✓ All tests completed successfully!")

        except Exception as e:
            print(f"\n✗ Test execution failed: {e}")
        finally:
            self.teardown()


if __name__ == "__main__":
    TestTC_001().run_test()
