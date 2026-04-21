import re
import os

files = [
    './api/__init__.py',
    './scripts/run_full_pipeline.py',
    './src/utils.py',
    './test_all_cycles.py'
]

for filepath in files:
    if not os.path.exists(filepath):
        print(f"⚠️ Fichier non trouvé: {filepath}")
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Ajouter une nouvelle ligne à la fin
    if not content.endswith('\n'):
        content += '\n'
    
    # Supprimer les f inutiles
    content = re.sub(r"f'([^\'{]*?)'", r"'\1'", content)
    content = re.sub(r'f"([^\"{]*?)"', r'"\1"', content)
    
    # Ajouter 2 lignes vides avant les fonctions
    content = re.sub(r'(\n)(def |class )', r'\n\n\2', content)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f'✅ Corrigé: {filepath}')

print('\n✅ Fini ! Lance: flake8 .')