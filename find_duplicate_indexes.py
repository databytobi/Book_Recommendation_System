# find_duplicate_indexes.py
import os
import re

models_dir = "apps/api/app/models"

for filename in os.listdir(models_dir):
    if filename.endswith('.py'):
        filepath = os.path.join(models_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Find columns with index=True
        columns = re.findall(r'(\w+)\s*=\s*Column\([^)]*index=True[^)]*\)', content)
        
        # Find explicit indexes in __table_args__
        indexes = re.findall(r"Index\(\s*'ix_[^']*'\s*,\s*'(\w+)'", content)
        
        # Check for duplicates
        duplicates = set(columns) & set(indexes)
        if duplicates:
            print(f"📁 {filename}: Duplicate indexes on: {', '.join(duplicates)}")