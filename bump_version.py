#!/usr/bin/env python3
"""
Script para atualizar a versão do plugin em todos os arquivos necessários
Uso: python bump_version.py 1.2.2
"""

import sys
import re
import os
from pathlib import Path

def update_version_in_file(file_path, old_version, new_version):
    """Atualiza a versão em um arquivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Diferentes padrões de versão dependendo do arquivo
        if file_path.name == 'setup.py':
            pattern = r"version='[\d\.]+',"
            replacement = f"version='{new_version}',"
        elif file_path.name == 'pyproject.toml':
            pattern = r'version = "[\d\.]+"'
            replacement = f'version = "{new_version}"'
        elif file_path.name == '__init__.py':
            pattern = r'__version__ = ["\'][\d\.]+["\']'
            replacement = f'__version__ = "{new_version}"'
        elif file_path.name == 'CHANGELOG.md':
            # Adiciona nova seção no changelog
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('## ['):
                    lines.insert(i, f'## [{new_version}] - TBD')
                    lines.insert(i+1, '')
                    lines.insert(i+2, '### Added')
                    lines.insert(i+3, '- ')
                    lines.insert(i+4, '')
                    lines.insert(i+5, '### Fixed')
                    lines.insert(i+6, '- ')
                    lines.insert(i+7, '')
                    lines.insert(i+8, '### Changed')
                    lines.insert(i+9, '- ')
                    lines.insert(i+10, '')
                    break
            content = '\n'.join(lines)
            replacement = None
        else:
            return False
        
        if replacement:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
        elif file_path.name == 'CHANGELOG.md':
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
    except Exception as e:
        print(f"Erro ao atualizar {file_path}: {e}")
        return False
    
    return False

def main():
    if len(sys.argv) != 2:
        print("Uso: python bump_version.py <nova_versao>")
        print("Exemplo: python bump_version.py 1.2.2")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Validar formato da versão
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print("Formato de versão inválido. Use x.y.z (exemplo: 1.2.2)")
        sys.exit(1)
    
    # Arquivos para atualizar
    files_to_update = [
        Path('setup.py'),
        Path('pyproject.toml'),
        Path('netbox_maintenance_device/__init__.py'),
        Path('CHANGELOG.md'),
    ]
    
    current_version = None
    updated_files = []
    
    # Detectar versão atual do setup.py
    setup_file = Path('setup.py')
    if setup_file.exists():
        with open(setup_file, 'r') as f:
            content = f.read()
            match = re.search(r"version='([\d\.]+)'", content)
            if match:
                current_version = match.group(1)
    
    print(f"Atualizando versão de {current_version} para {new_version}")
    print("-" * 50)
    
    # Atualizar cada arquivo
    for file_path in files_to_update:
        if file_path.exists():
            if update_version_in_file(file_path, current_version, new_version):
                print(f"✅ {file_path}")
                updated_files.append(str(file_path))
            else:
                print(f"❌ {file_path}")
        else:
            print(f"⚠️  {file_path} (não encontrado)")
    
    print("-" * 50)
    print(f"Versão atualizada para {new_version}")
    print(f"Arquivos atualizados: {len(updated_files)}")
    
    if updated_files:
        print("\nPróximos passos:")
        print("1. Revisar as mudanças")
        print("2. Atualizar o CHANGELOG.md com as mudanças específicas")
        print("3. Fazer commit das mudanças")
        print("4. Criar tag: git tag v" + new_version)
        print("5. Push: git push origin main --tags")

if __name__ == "__main__":
    main()