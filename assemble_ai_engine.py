"""
Script to assemble the complete ai_engine.py
"""

with open('ai_engine.py', 'r', encoding='utf-8') as f:
    orig_lines = f.readlines()

# Locate PERFECT_ANSWERS
start_idx = None
for i, line in enumerate(orig_lines):
    if line.strip().startswith('PERFECT_ANSWERS = {'):
        start_idx = i
        break

if start_idx is None:
    raise ValueError("PERFECT_ANSWERS not found in ai_engine.py")

eval_section = ''.join(orig_lines[start_idx:])

# Now import the base code from scratch/build_new_ai_engine.py
with open('scratch/build_new_ai_engine.py', 'r', encoding='utf-8') as f:
    builder_content = f.read()

# Extract code variable string
# The file starts with code = '''...'''
start_token = "code = '''"
end_token = "print('Base code length:'"
part1 = builder_content.split(start_token)[1]
base_code = part1.split(end_token)[0].rstrip().rstrip("'''")

full_code = base_code.strip() + "\n\n" + eval_section

# Write to ai_engine.py
with open('ai_engine.py', 'w', encoding='utf-8') as f:
    f.write(full_code)

print("ai_engine.py successfully updated. New line count:", len(full_code.splitlines()))
