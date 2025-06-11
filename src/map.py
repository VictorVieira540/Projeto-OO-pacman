from .utils import Vector2D

class Map:
    def __init__(self, layout_data, cell_size):
        self._layout = layout_data  # Encapsulamento: matriz 2D do labirinto
        self._cell_size = cell_size

    @property
    def layout(self):
        return self._layout

    @property
    def cell_size(self):
        return self._cell_size

    def load_map(self, map_file_path):
        # Simula o carregamento de um arquivo de mapa
        # Em um jogo real, isso leria um arquivo de texto ou JSON
        print(f"Carregando mapa de {map_file_path}")
        # Exemplo de layout simples (0=caminho, 1=parede)
        self._layout = [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1]
        ]

    def draw(self, screen):
        # Implementação de desenho para o mapa (paredes e caminhos)
        # (Requer Pygame para ser funcional)
        print("Desenhando o Mapa")
        for r_idx, row in enumerate(self._layout):
            for c_idx, cell in enumerate(row):
                if cell == 1: # Parede
                    print(f"  Desenhando parede em ({c_idx * self._cell_size}, {r_idx * self._cell_size})")
                else: # Caminho
                    print(f"  Desenhando caminho em ({c_idx * self._cell_size}, {r_idx * self._cell_size})")

    def is_wall(self, position: Vector2D):
        # Verifica se uma posição (em coordenadas de célula) é uma parede
        row = int(position.y / self._cell_size)
        col = int(position.x / self._cell_size)
        if 0 <= row < len(self._layout) and 0 <= col < len(self._layout[0]):
            return self._layout[row][col] == 1
        return True # Fora dos limites é considerado parede


