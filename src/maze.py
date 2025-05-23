import pygame
from typing import List, Tuple
from sprite_manager import SpriteManager
import json
import os
from enum import Enum


class MapElement(Enum):
    CAMINHO = 0
    PAREDE = 1
    POWER_PELLET = 2
    PACMAN_SPAWN = 3
    GHOST_HOUSE = 4
    PELLET = 5


class Maze:
    def __init__(self) -> None:
        self.wall_color = (0, 0, 255)  # Azul
        self.wall_size = 40
        self.food_size = 10
        self.walls: List[pygame.Rect] = []
        self.food: List[Tuple[pygame.Rect, str]] = []  # (rect, tipo)
        self.sprite_manager = SpriteManager()
        self.create_maze()
    
    def create_maze(self) -> None:
        """Cria o labirinto e a comida"""
        # Carrega o arquivo do mapa
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        map_path = os.path.join(base_dir, 'assets/mazes/map_data.json')
        
        try:
            with open(map_path, 'r') as f:
                data = json.load(f)
                mapa = data['map']
        except FileNotFoundError:
            print(f"Arquivo de mapa não encontrado em: {map_path}")
            return
        
        # Cria as paredes e comidas baseado no mapa
        for y in range(len(mapa)):
            for x in range(len(mapa[0])):
                elemento = mapa[y][x]
                pos_x = x * self.wall_size
                pos_y = y * self.wall_size
                
                if elemento == MapElement.PAREDE.value:
                    # Cria parede
                    wall = pygame.Rect(pos_x, pos_y, self.wall_size, self.wall_size)
                    self.walls.append(wall)
                elif elemento in [MapElement.POWER_PELLET.value, MapElement.PELLET.value]:
                    # Cria comida
                    food_x = pos_x + (self.wall_size - self.food_size) // 2
                    food_y = pos_y + (self.wall_size - self.food_size) // 2
                    food_rect = pygame.Rect(food_x, food_y, self.food_size, self.food_size)
                    food_type = "special" if elemento == MapElement.POWER_PELLET.value else "normal"
                    self.food.append((food_rect, food_type))
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o labirinto e a comida"""
        # Desenha as paredes
        for wall in self.walls:
            pygame.draw.rect(screen, self.wall_color, wall)
        
        # Desenha a comida
        for food_rect, food_type in self.food:
            sprite = self.sprite_manager.get_sprite("food", food_type)
            sprite = self.sprite_manager.scale_sprite(sprite, 0.625)  # 10/16 = 0.625
            screen.blit(sprite, (food_rect.x, food_rect.y))
    
    def check_wall_collision(self, rect: pygame.Rect) -> bool:
        """Verifica se um retângulo colidiu com alguma parede"""
        return any(rect.colliderect(wall) for wall in self.walls) 