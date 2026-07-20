"""Rename platform -> platcore across all relevant files."""
import os
import glob

# 1. Update platcore/__init__.py docstring
with open('platcore/__init__.py', 'r') as f:
    content = f.read()
content = content.replace('platform — Platform Layer', 'platcore — Platform Layer')
with open('platcore/__init__.py', 'w') as f:
    f.write(content)

# 2. Update all test files to use platcore.foundation instead of platform.foundation
for test_file in glob.glob('tests/**/*.py', recursive=True):
    with open(test_file, 'r') as f:
        content = f.read()
    if 'platform.foundation' in content:
        content = content.replace('platform.foundation', 'platcore.foundation')
        with open(test_file, 'w') as f:
            f.write(content)
        print(f'Updated: {test_file}')

# 3. Also update platcore/foundation source files that reference platform.foundation
for src_file in glob.glob('platcore/**/*.py', recursive=True):
    with open(src_file, 'r') as f:
        content = f.read()
    if 'platform.foundation.exceptions' in content:
        content = content.replace('platform.foundation.exceptions', 'platcore.foundation.exceptions')
        with open(src_file, 'w') as f:
            f.write(content)
        print(f'Updated src: {src_file}')

# 4. Check for any other remaining references
remaining = []
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root, f)
            with open(fp, 'r') as fh:
                content = fh.read()
            if 'platform.foundation' in content and 'platcore' not in content:
                remaining.append(fp)

if remaining:
    print(f"\nWARNING: remaining references to platform.foundation in: {remaining}")
else:
    print("\nNo remaining references to platform.foundation")

print('Done')

