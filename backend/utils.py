import re

def extract_python_code(text):
    code_blocks = re.findall(r'```python\n(.*?)```', text, re.DOTALL)
    return "\n\n".join(code_blocks)

def extract_json_object(text):
    code_blocks = re.findall(r'```json\n(.*?)```', text, re.DOTALL)
    return "\n\n".join(code_blocks)
