import pygame
from typing import List, Tuple
from sprite_manager import SpriteManager
import random
from PIL import Image


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
        # Carregue a imagem do labirinto
        img = Image.open('assets/mazes/001.png').convert('RGB')
        largura, altura = img.size

        # Defina as cores de referência (ajuste conforme necessário)
        cor_parede = (0, 255, 0)   # azul claro (parede)
        cor_caminho = (0, 0, 0)      # preto (caminho)
        cor_especial = (0, 255, 0)   # verde (área especial)

        # Inicialize a matriz do mapa
        mapa = []

        for y in range(altura):
            linha = []
            for x in range(largura):
                pixel = img.getpixel((x, y))
                if pixel == cor_parede:
                    linha.append(1)
                elif pixel == cor_especial:
                    linha.append(2)
                else:
                    linha.append(0)
            mapa.append(linha)

        # Exemplo: imprimir parte do mapa
        for linha in mapa[:10]:
            print(linha[:20])
    
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