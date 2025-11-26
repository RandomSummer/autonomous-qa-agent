import sys
sys.path.insert(0, '.')
from backend.models import ScriptGenerationRequest
import inspect

sig = inspect.signature(ScriptGenerationRequest.__init__)
print('Current model signature:')
print(sig)
print('\nFields:')
for name, field in ScriptGenerationRequest.model_fields.items():
    print(f'  {name}: {field.annotation}')
