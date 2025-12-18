# E-Shop Product Specifications

## Discount Code System

### Valid Discount Codes
- **SAVE15**: Applies a 15% discount to the total order amount
- Discount codes are case-insensitive
- Only one discount code can be applied per order
- Discount is applied to subtotal before shipping costs

### Discount Code Validation Rules
- Invalid codes should display an error message: "Invalid discount code"
- Empty discount code field should clear any applied discount
- Discount should be recalculated when cart contents change

## Product Catalog

### Available Products
1. **Wireless Headphones** - $29.99
   - High-quality bluetooth headphones
   - Product ID: 1

2. **Smart Watch** - $49.99
   - Fitness tracking smartwatch
   - Product ID: 2

3. **Phone Case** - $19.99
   - Protective phone case
   - Product ID: 3

### Cart Functionality
- Users can add multiple quantities of the same product
- Quantity can be updated using number input fields
- Minimum quantity is 1
- Items can be removed from cart individually
- Cart total updates automatically when quantities change

## Shipping Options

### Standard Shipping
- Cost: Free ($0.00)
- Default selection
- Delivery time: 5-7 business days

### Express Shipping
- Cost: $10.00
- Delivery time: 1-2 business days
- Additional cost added to order total

## Payment Methods

### Supported Payment Options
1. **Credit Card** (default selection)
   - Accepts major credit cards
   - Secure payment processing

2. **PayPal**
   - Alternative payment method
   - Redirects to PayPal for processing

## Order Processing

### Successful Order Requirements
- Cart must contain at least one item
- All required fields must be completed
- Valid email address format required
- Payment method must be selected
- Shipping method must be selected

### Success Confirmation
- Display "Payment Successful!" message
- Show confirmation text: "Thank you for your order. You will receive a confirmation email shortly."
- Hide checkout form after successful submission

## Business Rules

### Pricing Calculations
1. Subtotal = Sum of (item price × quantity) for all cart items
2. Discount amount = Subtotal × discount percentage (if applicable)
3. Shipping cost = Based on selected shipping method
4. Final Total = Subtotal - Discount + Shipping Cost

### Error Handling
- Display appropriate error messages for validation failures
- Prevent form submission if validation fails
- Clear error messages when issues are resolved