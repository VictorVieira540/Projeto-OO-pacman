import pygame
from typing import List, Tuple
from sprite_manager import SpriteManager
import random

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
        # Cria as paredes do labirinto
        # Paredes horizontais
        for x in range(0, 800, self.wall_size):
            self.walls.append(pygame.Rect(x, 0, self.wall_size, self.wall_size))
            self.walls.append(pygame.Rect(x, 560, self.wall_size, self.wall_size))
        
        # Paredes verticais
        for y in range(0, 600, self.wall_size):
            self.walls.append(pygame.Rect(0, y, self.wall_size, self.wall_size))
            self.walls.append(pygame.Rect(760, y, self.wall_size, self.wall_size))
        
        # Paredes internas
        self.walls.extend([
            pygame.Rect(200, 200, self.wall_size, self.wall_size),
            pygame.Rect(240, 200, self.wall_size, self.wall_size),
            pygame.Rect(280, 200, self.wall_size, self.wall_size),
            pygame.Rect(320, 200, self.wall_size, self.wall_size),
            pygame.Rect(360, 200, self.wall_size, self.wall_size),
            pygame.Rect(400, 200, self.wall_size, self.wall_size),
            pygame.Rect(440, 200, self.wall_size, self.wall_size),
            pygame.Rect(480, 200, self.wall_size, self.wall_size),
            pygame.Rect(520, 200, self.wall_size, self.wall_size),
            pygame.Rect(560, 200, self.wall_size, self.wall_size),
            
            pygame.Rect(200, 400, self.wall_size, self.wall_size),
            pygame.Rect(240, 400, self.wall_size, self.wall_size),
            pygame.Rect(280, 400, self.wall_size, self.wall_size),
            pygame.Rect(320, 400, self.wall_size, self.wall_size),
            pygame.Rect(360, 400, self.wall_size, self.wall_size),
            pygame.Rect(400, 400, self.wall_size, self.wall_size),
            pygame.Rect(440, 400, self.wall_size, self.wall_size),
            pygame.Rect(480, 400, self.wall_size, self.wall_size),
            pygame.Rect(520, 400, self.wall_size, self.wall_size),
            pygame.Rect(560, 400, self.wall_size, self.wall_size),
        ])
        
        # Cria a comida
        for x in range(50, 750, 50):
            for y in range(50, 550, 50):
                # Verifica se a posição não está ocupada por uma parede
                food_rect = pygame.Rect(x, y, self.food_size, self.food_size)
                if not any(food_rect.colliderect(wall) for wall in self.walls):
                    # 10% de chance de ser uma comida especial
                    food_type = "power" if random.random() < 0.1 else "normal"
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