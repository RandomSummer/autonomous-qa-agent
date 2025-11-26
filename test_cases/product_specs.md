# Checkout Discount Feature

- Supported discount code: SAVE15
- Discount value: 15% off the subtotal of cart items.
- The code is valid only for orders above $50.
- The code can be used once per order.

# Validation Rules

- If discount code is empty, show message: "Please enter a discount code."
- If discount code is invalid, show message: "Discount code not recognized."
- If discount code is valid but order total is below $50, show message:
  "Discount applies only to orders above $50."
- If discount is applied successfully, show message:
  "Discount applied: 15% off."
