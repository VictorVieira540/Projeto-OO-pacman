import pygame
from menu import Menu
from player import Player
from ghost import Ghost
from maze import Maze
from score import Score

class Game:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.menu = Menu()
        self.maze = Maze()
        self.player = Player(400, 300)  # Posição inicial do Pacman
        self.ghosts = [
            Ghost(200, 200, "red"),
            Ghost(600, 200, "pink"),
            Ghost(200, 400, "blue"),
            Ghost(600, 400, "orange")
        ]
        self.score = Score()
        self.game_state = "menu"  # Estados possíveis: menu, playing, game_over
        self.load_sounds()
    
    def load_sounds(self) -> None:
        """Carrega os sons do jogo"""
        self.sounds = {
            "eat": pygame.mixer.Sound("assets/sounds/eating.mp3"),
            "death": pygame.mixer.Sound("assets/sounds/miss.mp3"),
            "ghost": pygame.mixer.Sound("assets/sounds/ghost-normal-move.mp3"),
            "ghost_vulnerable": pygame.mixer.Sound("assets/sounds/ghost-turn-to-blue.mp3"),
            "ghost_eaten": pygame.mixer.Sound("assets/sounds/eating-ghost.mp3"),
            "fruit": pygame.mixer.Sound("assets/sounds/eating-fruit.mp3")
        }
    
    def update(self) -> None:
        """Atualiza o estado do jogo"""
        if self.game_state == "menu":
            self.menu.update()
            if self.menu.start_game:
                self.game_state = "playing"
        elif self.game_state == "playing":
            self.player.update()
            for ghost in self.ghosts:
                ghost.update(self.player)
            
            # Verifica colisões
            self.check_collisions()
            
            # Verifica se o jogo acabou
            if self.player.lives <= 0:
                self.game_state = "game_over"
    
    def draw(self) -> None:
        """Desenha todos os elementos do jogo"""
        self.screen.fill((0, 0, 0))  # Fundo preto
        
        if self.game_state == "menu":
            self.menu.draw(self.screen)
        elif self.game_state == "playing":
            self.maze.draw(self.screen)
            self.player.draw(self.screen)
            for ghost in self.ghosts:
                ghost.draw(self.screen)
            self.score.draw(self.screen)
        elif self.game_state == "game_over":
            self.draw_game_over()
    
    def check_collisions(self) -> None:
        """Verifica colisões entre elementos do jogo"""
        # Colisão com fantasmas
        for ghost in self.ghosts:
            if self.player.rect.colliderect(ghost.rect):
                if ghost.is_vulnerable:
                    self.score.add_points(200)
                    ghost.reset_position()
                    self.sounds["ghost_eaten"].play()
                else:
                    self.player.lives -= 1
                    self.sounds["death"].play()
                    self.reset_positions()
        
        # Colisão com comida
        for food_rect, food_type in self.maze.food[:]:
            if self.player.rect.colliderect(food_rect):
                if food_type == "power":
                    self.score.add_points(50)
                    self.sounds["ghost_vulnerable"].play()
                    for ghost in self.ghosts:
                        ghost.make_vulnerable()
                else:
                    self.score.add_points(10)
                    self.sounds["eat"].play()
                self.maze.food.remove((food_rect, food_type))
    
    def reset_positions(self) -> None:
        """Reseta as posições dos personagens após uma morte"""
        self.player.reset_position()
        for ghost in self.ghosts:
            ghost.reset_position()
    
    def draw_game_over(self) -> None:
        """Desenha a tela de game over"""
        font = pygame.font.Font(None, 74)
        text = font.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(400, 300))
        self.screen.blit(text, text_rect)
        
        font = pygame.font.Font(None, 36)
        text = font.render("Pressione ESPAÇO para voltar ao menu", True, (255, 255, 255))
        text_rect = text.get_rect(center=(400, 400))
        self.screen.blit(text, text_rect) 