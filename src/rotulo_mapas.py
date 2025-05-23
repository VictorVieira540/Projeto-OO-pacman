import pygame
import numpy as np
import os
import json
from enum import Enum

class MapElement(Enum):
    CAMINHO = 0
    PAREDE = 1
    POWER_PELLET = 2
    PACMAN_SPAWN = 3
    GHOST_HOUSE = 4
    PELLET = 5

class MapEditor:
    def __init__(self):
        pygame.init()
        
        # Configurações da janela
        self.CELL_SIZE = 20  # Tamanho de cada célula
        self.GRID_WIDTH = 28  # Número de células na horizontal
        self.GRID_HEIGHT = 31  # Número de células na vertical
        self.WINDOW_WIDTH = self.GRID_WIDTH * self.CELL_SIZE
        self.WINDOW_HEIGHT = self.GRID_HEIGHT * self.CELL_SIZE  # Removida altura extra
        
        # Cores com transparência
        self.COLORS = {
            MapElement.CAMINHO: (0, 0, 0, 100),        # Preto semi-transparente
            MapElement.PAREDE: (0, 0, 255, 150),       # Azul semi-transparente
            MapElement.POWER_PELLET: (255, 255, 0, 150),  # Amarelo semi-transparente
            MapElement.PACMAN_SPAWN: (255, 165, 0, 150),  # Laranja semi-transparente
            MapElement.GHOST_HOUSE: (255, 0, 0, 150),     # Vermelho semi-transparente
            MapElement.PELLET: (255, 255, 255, 150)       # Branco semi-transparente
        }
        
        # Inicialização
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Editor de Mapa Pac-Man")
        
        # Configura os diretórios
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = os.path.join(self.base_dir, 'assets/mazes')
        
        # Cria a pasta assets se não existir
        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir)
            print(f"Pasta assets criada em: {self.assets_dir}")
        
        # Carrega a imagem de referência
        self.reference_img_path = os.path.join(self.assets_dir, '001.png')
        try:
            self.reference_img = pygame.image.load(self.reference_img_path)
            self.reference_img = pygame.transform.scale(
                self.reference_img,
                (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
            )
        except pygame.error:
            print(f"ATENÇÃO: Coloque a imagem '001.png' na pasta: {self.assets_dir}")
            self.reference_img = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            self.reference_img.fill((0, 0, 0))
        
        # Cria uma superfície para os elementos com transparência
        self.overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        
        # Matriz do mapa
        self.map_data = np.zeros((self.GRID_HEIGHT, self.GRID_WIDTH), dtype=int)
        
        # Estado atual
        self.current_element = MapElement.PAREDE
        self.is_drawing = False
        self.show_grid = True  # Toggle para mostrar/esconder grade
        
        # Fonte para texto
        self.font = pygame.font.Font(None, 24)

    def draw_grid(self):
        """Desenha a grade e elementos sobre o mapa"""
        # Limpa o overlay
        self.overlay.fill((0, 0, 0, 0))
        
        # Desenha os elementos
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                if self.map_data[y][x] != MapElement.CAMINHO.value:  # Só desenha se não for caminho
                    rect = pygame.Rect(
                        x * self.CELL_SIZE, 
                        y * self.CELL_SIZE, 
                        self.CELL_SIZE, 
                        self.CELL_SIZE
                    )
                    element = MapElement(self.map_data[y][x])
                    pygame.draw.rect(self.overlay, self.COLORS[element], rect)
        
        # Desenha a grade se ativada
        if self.show_grid:
            for x in range(0, self.WINDOW_WIDTH, self.CELL_SIZE):
                pygame.draw.line(self.overlay, (255, 255, 255, 50), (x, 0), (x, self.WINDOW_HEIGHT))
            for y in range(0, self.WINDOW_HEIGHT, self.CELL_SIZE):
                pygame.draw.line(self.overlay, (255, 255, 255, 50), (0, y), (self.WINDOW_WIDTH, y))

    def draw_ui(self):
        """Desenha a interface do usuário"""
        # Cria uma superfície para a UI
        ui_surface = pygame.Surface((self.WINDOW_WIDTH, 30), pygame.SRCALPHA)
        ui_surface.fill((0, 0, 0, 180))  # Fundo semi-transparente
        
        # Mostra o elemento atual
        text = self.font.render(
            f"Elemento: {self.current_element.name}", 
            True, 
            (255, 255, 255)
        )
        ui_surface.blit(text, (10, 5))
        
        # Instruções
        instructions = [
            "0-5: Mudar Elemento",
            "G: Grade",
            "S: Salvar",
            "L: Carregar",
            "C: Limpar"
        ]
        
        x_pos = self.WINDOW_WIDTH - 400
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, (255, 255, 255))
            ui_surface.blit(text, (x_pos + i * 80, 5))
        
        self.screen.blit(ui_surface, (0, 0))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    # Seleção de elementos
                    if event.key in [pygame.K_0, pygame.K_1, pygame.K_2, 
                                   pygame.K_3, pygame.K_4, pygame.K_5]:
                        element_num = int(event.unicode)
                        self.current_element = MapElement(element_num)
                    
                    # Comandos
                    elif event.key == pygame.K_s:
                        self.save_map()
                    elif event.key == pygame.K_l:
                        self.load_map()
                    elif event.key == pygame.K_c:
                        self.clear_map()
                    elif event.key == pygame.K_g:
                        self.show_grid = not self.show_grid
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.is_drawing = True
                    x, y = pygame.mouse.get_pos()
                    grid_x = x // self.CELL_SIZE
                    grid_y = y // self.CELL_SIZE
                    if 0 <= grid_x < self.GRID_WIDTH and 0 <= grid_y < self.GRID_HEIGHT:
                        self.map_data[grid_y][grid_x] = self.current_element.value
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.is_drawing = False
                
                elif event.type == pygame.MOUSEMOTION and self.is_drawing:
                    x, y = pygame.mouse.get_pos()
                    grid_x = x // self.CELL_SIZE
                    grid_y = y // self.CELL_SIZE
                    if 0 <= grid_x < self.GRID_WIDTH and 0 <= grid_y < self.GRID_HEIGHT:
                        self.map_data[grid_y][grid_x] = self.current_element.value

            # Desenha
            self.screen.blit(self.reference_img, (0, 0))  # Desenha o mapa de fundo
            self.draw_grid()  # Desenha a grade e elementos
            self.screen.blit(self.overlay, (0, 0))  # Sobrepõe os elementos
            self.draw_ui()  # Desenha a UI por último
            pygame.display.flip()

        pygame.quit()

    def save_map(self):
        """Salva o mapa em um arquivo"""
        data = {
            'map': self.map_data.tolist(),
            'width': self.GRID_WIDTH,
            'height': self.GRID_HEIGHT
        }
        
        save_path = os.path.join(self.assets_dir, 'map_data.json')
        with open(save_path, 'w') as f:
            json.dump(data, f)
        print(f"Mapa salvo em: {save_path}")

    def load_map(self):
        """Carrega o mapa de um arquivo"""
        load_path = os.path.join(self.assets_dir, 'map_data.json')
        try:
            with open(load_path, 'r') as f:
                data = json.load(f)
                self.map_data = np.array(data['map'])
                print(f"Mapa carregado de: {load_path}")
        except FileNotFoundError:
            print(f"Arquivo de mapa não encontrado em: {load_path}")

    def clear_map(self):
        """Limpa o mapa"""
        self.map_data.fill(MapElement.CAMINHO.value)

if __name__ == "__main__":
    editor = MapEditor()
    editor.run()