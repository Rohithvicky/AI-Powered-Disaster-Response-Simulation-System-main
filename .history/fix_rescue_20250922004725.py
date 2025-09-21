import re

# Read the server.py file
with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Read the rescue fix
with open('rescue_fix.py', 'r', encoding='utf-8') as f:
    rescue_fix = f.read()

# Find the _check_rescues function and replace it
pattern = r'def _check_rescues\(self\):.*?(?=def \w+\(self\)|$)'
replacement = rescue_fix.strip()

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write the fixed content
with open('server.py', 'w') as f:
    f.write(new_content)

print('Rescue function replaced successfully')
