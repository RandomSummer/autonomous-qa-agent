#!/usr/bin/env python3
"""Fix the health check endpoint in frontend/app.py"""

# Read the backup file
with open('frontend/app.py.backup', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the incorrect endpoint
content = content.replace('call_api("/")', 'call_api("/api/health")')

# Write the fixed content
with open('frontend/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed health check endpoint: / -> /api/health")
