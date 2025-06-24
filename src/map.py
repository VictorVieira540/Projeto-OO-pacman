import pygame
from .utils import Vector2D
from .sprite_manager import sprite_manager

class Map:
    def __init__(self, layout_data=None, cell_size=None):
        self._layout = layout_data if layout_data else []
        # Usa o tamanho dos sprites como cell_size padrão
        self._cell_size = cell_size if cell_size else sprite_manager.sprite_size
        self._width = 0
        self._height = 0

    @property
    def layout(self):
        return self._layout

    @property
    def cell_size(self):
        return self._cell_size

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def load_default_map(self):
        """Carrega um mapa padrão para o jogo"""
        # Layout do labirinto (1=parede, 0=caminho, 2=pellet, 3=power_up)
        # Ajustado para funcionar melhor com sprites 16x16
        self._layout = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 3, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 3, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 2, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 1, 2, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1],
            [1, 3, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 3, 1],
            [1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        
        self._height = len(self._layout)
        self._width = len(self._layout[0]) if self._layout else 0

    def load_map(self, map_file_path):
        """Carrega mapa de um arquivo (futuramente)"""
        print(f"Carregando mapa de {map_file_path}")
        # Por agora, carrega o mapa padrão
        self.load_default_map()

    def get_pellets(self):
        """Retorna lista de pellets baseada no layout do mapa"""
        pellets = []
        for row_idx, row in enumerate(self._layout):
            for col_idx, cell in enumerate(row):
                if cell == 2:  # Pellet normal
                    x = col_idx * self._cell_size + self._cell_size // 2
                    y = row_idx * self._cell_size + self._cell_size // 2
                    pellets.append({"position": Vector2D(x, y), "type": "normal", "value": 10})
                elif cell == 3:  # Power-up
                    x = col_idx * self._cell_size + self._cell_size // 2
                    y = row_idx * self._cell_size + self._cell_size // 2
                    pellets.append({"position": Vector2D(x, y), "type": "power_up", "value": 50})
        return pellets

    def get_spawn_position(self, entity_type="player"):
        """Retorna posição de spawn para diferentes entidades"""
        spawn_positions = {
            "player": Vector2D(1 * self._cell_size + self._cell_size // 2, 1 * self._cell_size + self._cell_size // 2),
            "ghost_red": Vector2D(17 * self._cell_size + self._cell_size // 2, 9 * self._cell_size + self._cell_size // 2),
            "ghost_pink": Vector2D(18 * self._cell_size + self._cell_size // 2, 9 * self._cell_size + self._cell_size // 2),
            "ghost_cyan": Vector2D(17 * self._cell_size + self._cell_size // 2, 10 * self._cell_size + self._cell_size // 2),
            "ghost_orange": Vector2D(18 * self._cell_size + self._cell_size // 2, 10 * self._cell_size + self._cell_size // 2)
        }
        return spawn_positions.get(entity_type, Vector2D(self._cell_size, self._cell_size))

    def draw(self, screen):
        """Desenha o mapa na tela"""
        for row_idx, row in enumerate(self._layout):
            for col_idx, cell in enumerate(row):
                x = col_idx * self._cell_size
                y = row_idx * self._cell_size
                rect = pygame.Rect(x, y, self._cell_size, self._cell_size)
                
                if cell == 1:  # Parede
                    # Desenho procedural das paredes (sem sprites disponíveis)
                    pygame.draw.rect(screen, (0, 0, 255), rect)  # Azul para paredes
                    # Adiciona borda mais escura para definição
                    pygame.draw.rect(screen, (0, 0, 200), rect, 1)
                elif cell == 0:  # Caminho vazio
                    pygame.draw.rect(screen, (0, 0, 0), rect)  # Preto para caminhos

    def is_wall(self, position: Vector2D):
        """Verifica se uma posição é uma parede"""
        # Converte posição do mundo para coordenadas da grade
        col = int(position.x // self._cell_size)
        row = int(position.y // self._cell_size)
        
        # Verifica limites
        if row < 0 or row >= self._height or col < 0 or col >= self._width:
            return True
        
        # Retorna True se for parede (1)
        return self._layout[row][col] == 1

    def is_valid_position(self, position: Vector2D, object_size=16):
        """Verifica se uma posição é válida considerando o tamanho do objeto"""
        # Verifica os 4 cantos do objeto com uma margem menor
        half_size = object_size // 2.25  
        corners = [
            Vector2D(position.x - half_size, position.y - half_size),
            Vector2D(position.x + half_size, position.y - half_size),
            Vector2D(position.x - half_size, position.y + half_size),
            Vector2D(position.x + half_size, position.y + half_size)
        ]
        
        for corner in corners:
            if self.is_wall(corner):
                return False
        return True

    def remove_pellet_at(self, position: Vector2D):
        """Remove um pellet na posição especificada"""
        col = int(position.x // self._cell_size)
        row = int(position.y // self._cell_size)
        
        if 0 <= row < self._height and 0 <= col < self._width:
            if self._layout[row][col] in [2, 3]:  # Se é pellet ou power-up
                self._layout[row][col] = 0  # Torna caminho vazio
                return True
        return False

    def count_pellets(self):
        """Conta quantos pellets restam no mapa"""
        count = 0
        for row in self._layout:
            for cell in row:
                if cell in [2, 3]:  # Pellet normal ou power-up
                    count += 1
        return count 