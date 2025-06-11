#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Organizador de Sprites - Pac-Man
Organiza automaticamente os sprites extraídos em pastas por categoria.
"""

import os
import shutil
from pathlib import Path

def create_folder_structure(base_path):
    """Cria a estrutura de pastas para organização."""
    folders = [
        "pacman",
        "ghosts/red",
        "ghosts/pink", 
        "ghosts/blue",
        "ghosts/yellow",
        "ghosts/vulnerable",
        "powerups",
        "misc"
    ]
    
    created_folders = []
    for folder in folders:
        folder_path = Path(base_path) / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        created_folders.append(str(folder_path))
        print(f"📁 Pasta criada: {folder}")
    
    return created_folders

def categorize_sprite(filename):
    """Determina a categoria de um sprite baseado no nome do arquivo."""
    filename_lower = filename.lower()
    
    # Pac-Man
    if filename_lower.startswith('pac-'):
        return "pacman"
    
    # Fantasmas por cor
    elif filename_lower.startswith('red-'):
        return "ghosts/red"
    elif filename_lower.startswith('pink-'):
        return "ghosts/pink"
    elif filename_lower.startswith('blue-'):
        return "ghosts/blue"
    elif filename_lower.startswith('yellow-'):
        return "ghosts/yellow"
    
    # Estados especiais
    elif 'vulnerable' in filename_lower or 'vunerable' in filename_lower:
        return "ghosts/vulnerable"
    
    # Power-ups e itens
    elif any(word in filename_lower for word in ['pellet', 'fruit', 'cherry', 'strawberry', 'power']):
        return "powerups"
    
    # Outros
    else:
        return "misc"

def organize_sprites(source_dir, organized_dir):
    """Organiza os sprites nas pastas apropriadas."""
    source_path = Path(source_dir)
    organized_path = Path(organized_dir)
    
    if not source_path.exists():
        print(f"❌ Pasta fonte não encontrada: {source_dir}")
        return False
    
    # Criar estrutura de pastas
    print("🗂️  Criando estrutura de pastas...")
    create_folder_structure(organized_path)
    
    # Obter todos os arquivos PNG
    sprite_files = list(source_path.glob("*.png"))
    
    if not sprite_files:
        print(f"❌ Nenhum sprite PNG encontrado em: {source_dir}")
        return False
    
    print(f"\n📦 Organizando {len(sprite_files)} sprites...")
    
    # Contadores por categoria
    stats = {}
    
    # Mover cada sprite para a pasta apropriada
    for sprite_file in sprite_files:
        category = categorize_sprite(sprite_file.name)
        target_dir = organized_path / category
        target_file = target_dir / sprite_file.name
        
        try:
            # Copiar arquivo
            shutil.copy2(sprite_file, target_file)
            print(f"✅ {sprite_file.name} → {category}/")
            
            # Atualizar estatísticas
            stats[category] = stats.get(category, 0) + 1
            
        except Exception as e:
            print(f"❌ Erro ao mover {sprite_file.name}: {e}")
    
    # Mostrar estatísticas
    print(f"\n📊 Estatísticas da organização:")
    total_moved = 0
    for category, count in sorted(stats.items()):
        print(f"   {category}: {count} sprites")
        total_moved += count
    
    print(f"\n🎉 Total organizado: {total_moved} sprites")
    return True

def create_index_file(organized_dir):
    """Cria um arquivo índice com a organização dos sprites."""
    organized_path = Path(organized_dir)
    index_file = organized_path / "INDICE_SPRITES.md"
    
    content = [
        "# Índice de Sprites Organizados - Pac-Man\n",
        f"Organização criada automaticamente em: {organized_path}\n",
        "## Estrutura de Pastas\n"
    ]
    
    # Percorrer pastas e listar arquivos
    for root, dirs, files in os.walk(organized_path):
        root_path = Path(root)
        relative_path = root_path.relative_to(organized_path)
        
        if relative_path != Path(".") and files:
            # Adicionar cabeçalho da pasta
            folder_name = str(relative_path).replace("/", " / ").replace("\\", " / ")
            content.append(f"### 📁 {folder_name}\n")
            
            # Listar arquivos PNG
            png_files = [f for f in files if f.endswith('.png')]
            if png_files:
                for png_file in sorted(png_files):
                    content.append(f"- `{png_file}`\n")
                content.append("\n")
    
    # Adicionar estatísticas
    content.extend([
        "## Estatísticas\n",
        f"- **Total de pastas**: {len([d for d in organized_path.rglob('*') if d.is_dir()])}\n",
        f"- **Total de sprites**: {len(list(organized_path.rglob('*.png')))}\n",
        "\n## Como Usar\n",
        "```python\n",
        "# Exemplo de carregamento\n",
        "pacman_sprite = pygame.image.load('sprites_organized/pacman/pac-dir.png')\n",
        "red_ghost = pygame.image.load('sprites_organized/ghosts/red/red-cima-1.png')\n",
        "```\n"
    ])
    
    # Escrever arquivo
    try:
        with open(index_file, 'w', encoding='utf-8') as f:
            f.writelines(content)
        print(f"📄 Índice criado: {index_file}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar índice: {e}")
        return False

def main():
    """Função principal."""
    print("🎮 === Organizador de Sprites - Pac-Man ===\n")
    
    # Caminhos
    source_dir = "assets/sprites/individual"
    organized_dir = "assets/sprites/organized"
    
    # Verificar se existe pasta fonte
    if not os.path.exists(source_dir):
        print(f"❌ Pasta de sprites não encontrada: {source_dir}")
        print("Certifique-se de que você extraiu os sprites primeiro.")
        return
    
    # Confirmar organização
    print(f"📂 Pasta fonte: {source_dir}")
    print(f"📂 Pasta destino: {organized_dir}")
    
    try:
        choice = input("\nDeseja organizar os sprites? (s/n): ").lower().strip()
        
        if choice in ['s', 'sim', 'y', 'yes']:
            print("\n🚀 Iniciando organização...")
            
            # Organizar sprites
            if organize_sprites(source_dir, organized_dir):
                # Criar índice
                create_index_file(organized_dir)
                
                print(f"\n✅ Organização concluída!")
                print(f"📁 Sprites organizados em: {organized_dir}")
                print("📄 Veja o arquivo INDICE_SPRITES.md para detalhes")
                
                # Perguntar se quer manter originais
                keep_original = input("\nManter sprites originais? (s/n): ").lower().strip()
                if keep_original not in ['s', 'sim', 'y', 'yes']:
                    try:
                        import shutil
                        shutil.rmtree(source_dir)
                        print(f"🗑️  Pasta original removida: {source_dir}")
                    except Exception as e:
                        print(f"❌ Erro ao remover pasta original: {e}")
            else:
                print("❌ Falha na organização.")
        else:
            print("Organização cancelada.")
    
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main() 