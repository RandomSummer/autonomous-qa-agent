#!/usr/bin/env bash
set -euo pipefail

echo "Starting Autonomous QA Agent via start_app.py..."
echo

# Always run from script directory (project root)
cd "$(dirname "$0")"

# Check start_app.py exists
[[ -f "start_app.py" ]] || { echo "❌ start_app.py not found. Run this from the project root."; exit 1; }

# Pick Python from local venv if available
PYTHON="python3"
if [[ -x ".venv/bin/python" ]]; then PYTHON=".venv/bin/python"; fi
if [[ -x "venv/bin/python"  ]]; then PYTHON="venv/bin/python";  fi

echo "Using Python: $PYTHON"
echo

"$PYTHON" "start_app.py"
