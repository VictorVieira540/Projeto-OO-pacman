#!/usr/bin/env python3
"""
Exemplo de uso do sistema de carregamento de mapas JSON do Pac-Man

Este script demonstra como:
1. Carregar diferentes mapas JSON
2. Validar mapas
3. Criar novos mapas
4. Gerenciar layouts personalizados
"""

import sys
import os
import json

# Adiciona o diretório pai ao path para importar módulos do jogo
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.map import Map
from src.utils import Vector2D

def listar_mapas_disponiveis():
    """Lista todos os mapas JSON disponíveis"""
    print("=== MAPAS DISPONÍVEIS ===")
    
    maps_dir = "assets/maps"
    if not os.path.exists(maps_dir):
        print("Diretório de mapas não encontrado!")
        return []
    
    mapas = []
    for arquivo in os.listdir(maps_dir):
        if arquivo.endswith('.json'):
            caminho = os.path.join(maps_dir, arquivo)
            mapas.append(caminho)
            
            # Carrega metadados do mapa
            try:
                with open(caminho, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                metadata = data.get('metadata', {})
                print(f"📁 {arquivo}")
                print(f"   Nome: {metadata.get('name', 'Sem nome')}")
                print(f"   Descrição: {metadata.get('description', 'Sem descrição')}")
                print(f"   Dimensões: {metadata.get('width', '?')}x{metadata.get('height', '?')}")
                print(f"   Dificuldade: {metadata.get('difficulty', 50)}/200")
                print(f"   Autor: {metadata.get('author', 'Desconhecido')}")
                print()
            except Exception as e:
                print(f"❌ {arquivo} - Erro ao ler: {e}")
                print()
    
    return mapas

def testar_carregamento_mapa(caminho_mapa):
    """Testa o carregamento de um mapa específico"""
    print(f"=== TESTANDO MAPA: {caminho_mapa} ===")
    
    try:
        # Carrega o mapa
        mapa = Map(map_file_path=caminho_mapa)
        
        # Exibe informações
        print(f"✅ Mapa carregado com sucesso!")
        print(f"Nome: {mapa.metadata.get('name', 'Sem nome')}")
        print(f"Dimensões: {mapa.width}x{mapa.height}")
        print(f"Cell Size: {mapa.cell_size}")
        print(f"Total de células: {mapa.width * mapa.height}")
        
        # Conta elementos do mapa
        paredes = 0
        pellets = 0
        power_ups = 0
        caminhos = 0
        
        for linha in mapa.layout:
            for celula in linha:
                if celula == 0:
                    caminhos += 1
                elif celula == 1:
                    paredes += 1
                elif celula == 2:
                    pellets += 1
                elif celula == 3:
                    power_ups += 1
        
        print(f"Paredes: {paredes}")
        print(f"Pellets normais: {pellets}")
        print(f"Power-ups: {power_ups}")
        print(f"Caminhos vazios: {caminhos}")
        
        # Testa posições de spawn
        print(f"\nPosições de spawn:")
        spawn_types = ["player", "ghost_red", "ghost_pink", "ghost_cyan", "ghost_orange"]
        for spawn_type in spawn_types:
            pos = mapa.get_spawn_position(spawn_type)
            print(f"  {spawn_type}: ({pos.x}, {pos.y})")
        
        # Testa contagem de pellets
        total_pellets = mapa.count_pellets()
        print(f"\nTotal de pellets contados: {total_pellets}")
        
        # Testa sistema de dificuldade
        difficulty = mapa.difficulty
        print(f"\nSistema de Dificuldade:")
        print(f"  Nível: {difficulty}/200")
        
        # Simula configuração de fantasma
        if difficulty <= 24:
            categoria = "MUITO FÁCIL"
        elif difficulty <= 49:
            categoria = "FÁCIL+"
        elif difficulty <= 74:
            categoria = "MÉDIO"
        elif difficulty <= 99:
            categoria = "MÉDIO+"
        elif difficulty <= 124:
            categoria = "DIFÍCIL"
        elif difficulty <= 149:
            categoria = "DIFÍCIL+"
        elif difficulty <= 174:
            categoria = "MUITO DIFÍCIL"
        else:
            categoria = "EXTREMO"
            
        print(f"  Categoria: {categoria}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar mapa: {e}")
        return False

def criar_mapa_exemplo():
    """Cria um mapa de exemplo em JSON"""
    print("=== CRIANDO MAPA DE EXEMPLO ===")
    
    # Mapa simples 10x10
    layout_exemplo = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 1, 2, 2, 2, 1],
        [1, 3, 1, 2, 2, 1, 2, 1, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 1, 1, 0, 0, 1, 1, 2, 1],
        [1, 2, 1, 0, 0, 0, 0, 1, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 3, 1, 2, 2, 1, 2, 1, 2, 1],
        [1, 2, 2, 2, 2, 1, 2, 2, 2, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    
    mapa_data = {
        "metadata": {
            "name": "Mapa Exemplo Criado por Script",
            "version": "1.0",
            "author": "Script de Exemplo",
            "description": "Mapa 10x10 criado automaticamente",
            "cell_size": 16,
            "width": 10,
            "height": 10,
            "difficulty": 75
        },
        "legend": {
            "0": "caminho_vazio",
            "1": "parede",
            "2": "pellet_normal", 
            "3": "power_up"
        },
        "spawn_positions": {
            "player": {"x": 1, "y": 1},
            "ghost_red": {"x": 5, "y": 4},
            "ghost_pink": {"x": 5, "y": 5},
            "ghost_cyan": {"x": 4, "y": 5},
            "ghost_orange": {"x": 6, "y": 5}
        },
        "layout": layout_exemplo
    }
    
    # Salva o mapa
    caminho_saida = "assets/maps/exemplo_script.json"
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    
    try:
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(mapa_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Mapa salvo em: {caminho_saida}")
        
        # Testa o carregamento
        if testar_carregamento_mapa(caminho_saida):
            print("✅ Mapa criado e testado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao salvar mapa: {e}")

def validar_mapa_json(caminho_mapa):
    """Valida a estrutura de um mapa JSON"""
    print(f"=== VALIDANDO MAPA: {caminho_mapa} ===")
    
    try:
        with open(caminho_mapa, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validações básicas
        erros = []
        
        # Verifica campos obrigatórios
        if 'layout' not in data:
            erros.append("Campo 'layout' obrigatório ausente")
        
        # Valida layout
        if 'layout' in data:
            layout = data['layout']
            if not isinstance(layout, list) or len(layout) == 0:
                erros.append("Layout deve ser uma lista não-vazia")
            else:
                # Verifica consistência das linhas
                largura_esperada = len(layout[0])
                for i, linha in enumerate(layout):
                    if len(linha) != largura_esperada:
                        erros.append(f"Linha {i} tem {len(linha)} elementos, esperado {largura_esperada}")
                    
                    # Verifica valores válidos
                    for j, celula in enumerate(linha):
                        if not isinstance(celula, int) or celula < 0 or celula > 3:
                            erros.append(f"Valor inválido na posição ({i}, {j}): {celula}")
        
        # Verifica metadados
        if 'metadata' in data:
            metadata = data['metadata']
            if 'width' in metadata and 'layout' in data:
                if metadata['width'] != len(data['layout'][0]):
                    erros.append("Largura nos metadados não confere com layout")
            if 'height' in metadata and 'layout' in data:
                if metadata['height'] != len(data['layout']):
                    erros.append("Altura nos metadados não confere com layout")
        
        # Verifica spawn positions
        if 'spawn_positions' in data:
            spawn_data = data['spawn_positions']
            required_spawns = ['player', 'ghost_red', 'ghost_pink', 'ghost_cyan', 'ghost_orange']
            for spawn_type in required_spawns:
                if spawn_type not in spawn_data:
                    erros.append(f"Posição de spawn ausente: {spawn_type}")
                else:
                    pos = spawn_data[spawn_type]
                    if not isinstance(pos, dict) or 'x' not in pos or 'y' not in pos:
                        erros.append(f"Posição de spawn inválida para {spawn_type}")
        
        # Resultado da validação
        if erros:
            print("❌ MAPA INVÁLIDO!")
            for erro in erros:
                print(f"   • {erro}")
            return False
        else:
            print("✅ MAPA VÁLIDO!")
            return True
            
    except json.JSONDecodeError as e:
        print(f"❌ Erro JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal do exemplo"""
    print("🎮 SISTEMA DE CARREGAMENTO DE MAPAS PAC-MAN")
    print("=" * 50)
    
    # 1. Lista mapas disponíveis
    mapas = listar_mapas_disponiveis()
    
    if not mapas:
        print("Nenhum mapa encontrado. Criando mapa de exemplo...")
        criar_mapa_exemplo()
        mapas = listar_mapas_disponiveis()
    
    # 2. Testa carregamento de cada mapa
    print("\n" + "=" * 50)
    for mapa in mapas:
        print()
        testar_carregamento_mapa(mapa)
        validar_mapa_json(mapa)
    
    # 3. Cria mapa de exemplo
    print("\n" + "=" * 50)
    criar_mapa_exemplo()
    
    print("\n✅ Exemplo concluído!")
    print("\nDicas para criar seus próprios mapas:")
    print("• 0 = caminho vazio")
    print("• 1 = parede") 
    print("• 2 = pellet normal")
    print("• 3 = power-up")
    print("• Certifique-se de que todas as linhas tenham o mesmo tamanho")
    print("• Defina posições de spawn para todos os personagens")
    print("• Adicione metadados informativos")

if __name__ == "__main__":
    main() 