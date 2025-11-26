"""
Test script for Document Parser
Creates sample files and tests parsing functionality
"""

from pathlib import Path
from backend.services.document_parser import document_parser

# Create test directory
test_dir = Path("test_documents")
test_dir.mkdir(exist_ok=True)

print("🧪 Testing Document Parser\n")
print("=" * 60)

# Test 1: Markdown file
print("\n📝 Test 1: Parsing Markdown")
md_content = """# Product Specifications

## Discount Code Feature
- The discount code **SAVE15** applies a 15% discount
- The discount code **SAVE20** applies a 20% discount
- Invalid codes should show an error message

## Shipping Options
- Standard shipping is **free**
- Express shipping costs **$10**
"""

md_file = test_dir / "product_specs.md"
md_file.write_text(md_content)

result = document_parser.parse_file(md_file)
if result['success']:
    print("✓ Markdown parsed successfully")
    print(f"  Filename: {result['metadata']['filename']}")
    print(f"  Size: {result['metadata']['file_size']} bytes")
    print(f"  Content preview: {result['content'][:100]}...")
else:
    print(f"✗ Failed: {result['error']}")

# Test 2: Text file
print("\n📄 Test 2: Parsing Text")
txt_content = """UI/UX Guidelines

Form Validation:
- Error messages must be displayed in red text
- Required fields should have a red asterisk
- Success messages should be green

Button Styles:
- Primary buttons should be green
- Cancel buttons should be gray
"""

txt_file = test_dir / "ui_ux_guide.txt"
txt_file.write_text(txt_content)

result = document_parser.parse_file(txt_file)
if result['success']:
    print("✓ Text file parsed successfully")
    print(f"  Content length: {len(result['content'])} characters")
else:
    print(f"✗ Failed: {result['error']}")

# Test 3: JSON file
print("\n📋 Test 3: Parsing JSON")
json_content = """{
  "endpoints": {
    "apply_coupon": {
      "method": "POST",
      "path": "/api/apply_coupon",
      "parameters": {
        "code": "string",
        "cart_total": "number"
      },
      "response": {
        "discount_amount": "number",
        "new_total": "number"
      }
    },
    "submit_order": {
      "method": "POST",
      "path": "/api/submit_order",
      "parameters": {
        "name": "string",
        "email": "string",
        "address": "string"
      }
    }
  }
}"""

json_file = test_dir / "api_endpoints.json"
json_file.write_text(json_content)

result = document_parser.parse_file(json_file)
if result['success']:
    print("✓ JSON parsed successfully")
    print(f"  Content preview:\n{result['content'][:200]}...")
else:
    print(f"✗ Failed: {result['error']}")

# Test 4: HTML file
print("\n🌐 Test 4: Parsing HTML")
html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Checkout Page</title>
</head>
<body>
    <form id="checkout-form">
        <input type="text" id="name" name="name" placeholder="Full Name" required>
        <input type="email" id="email" name="email" placeholder="Email" required>
        <input type="text" id="discount-code" name="discount_code" placeholder="Discount Code">
        <button type="submit" id="pay-btn">Pay Now</button>
    </form>
</body>
</html>"""

html_file = test_dir / "checkout.html"
html_file.write_text(html_content)

result = document_parser.parse_file(html_file)
if result['success']:
    print("✓ HTML parsed successfully")
    print(f"  Extracted structure:\n{result['content'][:300]}...")
else:
    print(f"✗ Failed: {result['error']}")

# Test 5: Batch parsing
print("\n📦 Test 5: Batch Parsing Multiple Files")
all_files = [md_file, txt_file, json_file, html_file]
batch_result = document_parser.parse_multiple_files(all_files)

print(f"✓ Batch processing complete")
print(f"  Total files: {batch_result['total']}")
print(f"  Successful: {batch_result['successful']}")
print(f"  Failed: {batch_result['failed']}")

# Test 6: Unsupported file type
print("\n❌ Test 6: Unsupported File Type")
unsupported_file = test_dir / "test.xyz"
unsupported_file.write_text("test content")

result = document_parser.parse_file(unsupported_file)
if not result['success']:
    print(f"✓ Correctly rejected: {result['error']}")
else:
    print("✗ Should have failed for unsupported type")

print("\n" + "=" * 60)
print("✅ All parser tests completed!\n")

print("📁 Test files created in:", test_dir.absolute())
print("💡 You can inspect these files to see what the parser extracts")