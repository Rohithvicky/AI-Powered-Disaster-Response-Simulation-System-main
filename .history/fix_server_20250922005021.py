import re

# Read the server.py file
with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Read the clean rescue function
with open('clean_rescue_function.py', 'r', encoding='utf-8') as f:
    clean_rescue = f.read()

# Find and replace the _check_rescues function
pattern = r'def _check_rescues\(self\):.*?(?=def \w+\(self\)|$)'
replacement = clean_rescue.strip()

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write the fixed content
with open('server.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Rescue function replaced successfully')
