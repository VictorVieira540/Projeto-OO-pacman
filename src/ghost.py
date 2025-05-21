import pygame
import random
from typing import Tuple
from sprite_manager import SpriteManager

class Ghost:
    def __init__(self, x: int, y: int, color: str) -> None:
        self.x = x
        self.y = y
        self.color = color
        self.speed = 4
        self.direction = random.choice(["up", "down", "left", "right"])
        self.initial_position = (x, y)
        self.rect = pygame.Rect(x, y, 30, 30)
        self.sprite_manager = SpriteManager()
        self.is_vulnerable = False
        self.vulnerable_timer = 0
    
    def update(self, player: 'Player') -> None:
        """Atualiza a posição do fantasma"""
        # Movimento aleatório com tendência a seguir o jogador
        if random.random() < 0.7:  # 70% de chance de seguir o jogador
            self.follow_player(player)
        else:
            self.random_movement()
        
        # Atualiza o retângulo de colisão
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Mantém o fantasma dentro da tela
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())
        self.x = self.rect.x
        self.y = self.rect.y
        
        # Atualiza o timer de vulnerabilidade
        if self.is_vulnerable:
            self.vulnerable_timer -= 1
            if self.vulnerable_timer <= 0:
                self.is_vulnerable = False
    
    def follow_player(self, player: 'Player') -> None:
        """Faz o fantasma seguir o jogador"""
        dx = player.x - self.x
        dy = player.y - self.y
        
        # Escolhe a direção com maior diferença
        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"
        
        # Move na direção escolhida
        if self.direction == "right":
            self.x += self.speed
        elif self.direction == "left":
            self.x -= self.speed
        elif self.direction == "down":
            self.y += self.speed
        elif self.direction == "up":
            self.y -= self.speed
    
    def random_movement(self) -> None:
        """Faz o fantasma se mover aleatoriamente"""
        if random.random() < 0.1:  # 10% de chance de mudar de direção
            self.direction = random.choice(["up", "down", "left", "right"])
        
        # Move na direção atual
        if self.direction == "right":
            self.x += self.speed
        elif self.direction == "left":
            self.x -= self.speed
        elif self.direction == "down":
            self.y += self.speed
        elif self.direction == "up":
            self.y -= self.speed
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o fantasma na tela"""
        if self.is_vulnerable:
            sprite = self.sprite_manager.get_sprite("ghost_blue", self.direction)
        else:
            sprite = self.sprite_manager.get_sprite(f"ghost_{self.color}", self.direction)
        sprite = self.sprite_manager.scale_sprite(sprite, 0.9375)  # 30/32 = 0.9375
        screen.blit(sprite, (self.x, self.y))
    
    def reset_position(self) -> None:
        """Reseta a posição do fantasma para a posição inicial"""
        self.x, self.y = self.initial_position
        self.rect.x = self.x
        self.rect.y = self.y
        self.is_vulnerable = False
        self.vulnerable_timer = 0
    
    def make_vulnerable(self, duration: int = 300) -> None:
        """Torna o fantasma vulnerável por um determinado tempo"""
        self.is_vulnerable = True
        self.vulnerable_timer = duration 