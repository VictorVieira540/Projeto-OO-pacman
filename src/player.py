import pygame
from typing import Tuple
from sprite_manager import SpriteManager

class Player:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.speed = 5
        self.direction = "right"
        self.lives = 3
        self.initial_position = (x, y)
        self.rect = pygame.Rect(x, y, 30, 30)
        self.sprite_manager = SpriteManager()
        self.animation_frame = 0
        self.animation_timer = 0
    
    def update(self) -> None:
        """Atualiza a posição do Pacman baseado nas teclas pressionadas"""
        keys = pygame.key.get_pressed()
        
        # Movimento horizontal
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.direction = "left"
        elif keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.direction = "right"
        
        # Movimento vertical
        if keys[pygame.K_UP]:
            self.y -= self.speed
            self.direction = "up"
        elif keys[pygame.K_DOWN]:
            self.y += self.speed
            self.direction = "down"
        
        # Atualiza o retângulo de colisão
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Mantém o Pacman dentro da tela
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())
        self.x = self.rect.x
        self.y = self.rect.y
        
        # Atualiza a animação
        self.animation_timer += 1
        if self.animation_timer >= 5:  # Ajuste este valor para controlar a velocidade da animação
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o Pacman na tela"""
        sprite = self.sprite_manager.get_sprite("pacman", self.direction, self.animation_frame)
        sprite = self.sprite_manager.scale_sprite(sprite, 0.9375)  # 30/32 = 0.9375
        screen.blit(sprite, (self.x, self.y))
    
    def reset_position(self) -> None:
        """Reseta a posição do Pacman para a posição inicial"""
        self.x, self.y = self.initial_position
        self.rect.x = self.x
        self.rect.y = self.y 