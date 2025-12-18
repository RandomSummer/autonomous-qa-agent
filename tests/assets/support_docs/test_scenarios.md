# E-Shop Test Scenarios

## Cart Management Test Scenarios

### Positive Test Cases
1. **Add Single Item to Cart**
   - Click "Add to Cart" for any product
   - Verify item appears in cart section
   - Verify cart total updates correctly

2. **Add Multiple Items to Cart**
   - Add different products to cart
   - Verify all items appear in cart
   - Verify total reflects sum of all items

3. **Update Item Quantity**
   - Add item to cart
   - Change quantity using number input
   - Verify total updates automatically

### Negative Test Cases
1. **Remove Item from Cart**
   - Add items to cart
   - Click remove button for an item
   - Verify item is removed and total updates

2. **Set Quantity to Zero**
   - Add item to cart
   - Set quantity to 0
   - Verify item is removed from cart

## Discount Code Test Scenarios

### Positive Test Cases
1. **Apply Valid Discount Code SAVE15**
   - Add items to cart (subtotal > $0)
   - Enter "SAVE15" in discount field
   - Click Apply
   - Verify 15% discount is applied
   - Verify total is reduced correctly

2. **Clear Discount Code**
   - Apply valid discount code
   - Clear the discount field
   - Click Apply
   - Verify discount is removed

### Negative Test Cases
1. **Apply Invalid Discount Code**
   - Enter invalid code (e.g., "INVALID")
   - Click Apply
   - Verify error message appears: "Invalid discount code"
   - Verify no discount is applied

2. **Apply Discount to Empty Cart**
   - Ensure cart is empty
   - Enter valid discount code
   - Verify appropriate handling (no effect or error)

## Form Validation Test Scenarios

### Positive Test Cases
1. **Submit Valid Form**
   - Fill all required fields with valid data
   - Name: "John Doe"
   - Email: "john.doe@example.com"
   - Address: "123 Main St, City, State 12345"
   - Select shipping and payment methods
   - Click "Pay Now"
   - Verify success message appears

### Negative Test Cases
1. **Submit Empty Required Fields**
   - Leave name field empty
   - Click "Pay Now"
   - Verify error message: "Name is required"
   - Verify error text is red

2. **Submit Invalid Email Format**
   - Enter invalid email: "invalid-email"
   - Click "Pay Now"
   - Verify error message: "Please enter a valid email address"
   - Verify error text is red

3. **Submit Empty Email Field**
   - Leave email field empty
   - Click "Pay Now"
   - Verify email validation error appears

4. **Submit Empty Address Field**
   - Leave address field empty
   - Click "Pay Now"
   - Verify error message: "Address is required"

## Shipping Method Test Scenarios

### Test Cases
1. **Select Standard Shipping**
   - Select "Standard (Free)" radio button
   - Verify no additional cost added to total
   - Verify total calculation is correct

2. **Select Express Shipping**
   - Select "Express ($10)" radio button
   - Verify $10 is added to total
   - Verify total calculation includes shipping cost

3. **Switch Between Shipping Methods**
   - Start with Standard shipping
   - Switch to Express shipping
   - Verify total updates to include $10 shipping
   - Switch back to Standard
   - Verify $10 shipping cost is removed

## Payment Method Test Scenarios

### Test Cases
1. **Select Credit Card Payment**
   - Select "Credit Card" radio button
   - Verify selection is registered
   - Complete order process

2. **Select PayPal Payment**
   - Select "PayPal" radio button
   - Verify selection is registered
   - Complete order process

## Integration Test Scenarios

### End-to-End Test Cases
1. **Complete Purchase Flow**
   - Add multiple items to cart
   - Update quantities
   - Apply valid discount code
   - Select Express shipping
   - Fill valid customer details
   - Select payment method
   - Submit order
   - Verify success message

2. **Complete Purchase with Standard Shipping**
   - Add items to cart
   - Apply SAVE15 discount
   - Select Standard shipping (free)
   - Fill valid customer details
   - Submit order
   - Verify final total calculation

## Edge Cases and Boundary Tests

### Edge Cases
1. **Maximum Quantity Test**
   - Set item quantity to very high number (e.g., 999)
   - Verify system handles large quantities
   - Verify total calculation accuracy

2. **Special Characters in Form Fields**
   - Enter special characters in name field
   - Enter international characters
   - Verify proper handling

3. **Long Address Text**
   - Enter very long address (>500 characters)
   - Verify system handles long text
   - Verify form submission works

### Browser Compatibility Tests
1. **Cross-Browser Testing**
   - Test on Chrome, Firefox, Safari, Edge
   - Verify consistent behavior
   - Verify styling consistency

2. **Mobile Responsiveness**
   - Test on mobile devices
   - Verify touch interactions work
   - Verify layout adapts properly

## Performance Test Scenarios

### Performance Tests
1. **Cart Update Performance**
   - Add many items to cart quickly
   - Verify responsive updates
   - Verify no UI lag

2. **Form Validation Performance**
   - Test real-time email validation
   - Verify immediate feedback
   - Verify no performance issues

## Security Test Scenarios

### Security Tests
1. **Input Sanitization**
   - Enter HTML/JavaScript in form fields
   - Verify proper sanitization
   - Verify no script execution

2. **Form Submission Security**
   - Test form submission with malicious data
   - Verify proper validation
   - Verify secure handling