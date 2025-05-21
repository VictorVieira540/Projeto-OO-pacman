import pygame
import os

class Menu:
    def __init__(self) -> None:
        self.start_game = False
        self.show_high_scores = False
        self.music_volume = 0.5
        self.sfx_volume = 0.5
        self.selected_option = 0
        self.options = ["Iniciar Jogo", "Recordes", "Configurações", "Sair"]
        self.load_sounds()
    
    def load_sounds(self) -> None:
        """Carrega os sons do menu"""
        pygame.mixer.music.load("assets/sounds/start-music.mp3")
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(-1)  # Loop infinito
    
    def update(self) -> None:
        """Atualiza o estado do menu"""
        keys = pygame.key.get_pressed()
        
        # Navegação no menu
        if keys[pygame.K_UP]:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif keys[pygame.K_DOWN]:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        
        # Seleção de opção
        if keys[pygame.K_RETURN]:
            if self.options[self.selected_option] == "Iniciar Jogo":
                self.start_game = True
            elif self.options[self.selected_option] == "Recordes":
                self.show_high_scores = True
            elif self.options[self.selected_option] == "Sair":
                pygame.quit()
                exit()
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o menu na tela"""
        screen.fill((0, 0, 0))
        
        # Título
        font = pygame.font.Font(None, 74)
        title = font.render("PACMAN", True, (255, 255, 0))
        screen.blit(title, (300, 100))
        
        # Opções do menu
        font = pygame.font.Font(None, 36)
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            text = font.render(option, True, color)
            screen.blit(text, (350, 250 + i * 50))
        
        # Instruções
        font = pygame.font.Font(None, 24)
        text = font.render("Use as setas para navegar e ENTER para selecionar", True, (255, 255, 255))
        screen.blit(text, (250, 500))
    
    def draw_settings(self, screen: pygame.Surface) -> None:
        """Desenha a tela de configurações"""
        screen.fill((0, 0, 0))
        
        font = pygame.font.Font(None, 36)
        
        # Título
        title = font.render("Configurações", True, (255, 255, 255))
        screen.blit(title, (350, 50))
        
        # Volume da música
        text = font.render(f"Música: {int(self.music_volume * 100)}%", True, (255, 255, 255))
        screen.blit(text, (300, 200))
        
        # Volume dos efeitos sonoros
        text = font.render(f"Efeitos: {int(self.sfx_volume * 100)}%", True, (255, 255, 255))
        screen.blit(text, (300, 300))
        
        # Instruções
        text = font.render("Use ← e → para ajustar o volume", True, (255, 255, 255))
        screen.blit(text, (300, 400))
        text = font.render("Pressione ESPAÇO para voltar", True, (255, 255, 255))
        screen.blit(text, (300, 450))
    
    def update_settings(self) -> None:
        """Atualiza as configurações"""
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            if self.selected_option == 0:
                self.music_volume = max(0, self.music_volume - 0.1)
                pygame.mixer.music.set_volume(self.music_volume)
            else:
                self.sfx_volume = max(0, self.sfx_volume - 0.1)
        elif keys[pygame.K_RIGHT]:
            if self.selected_option == 0:
                self.music_volume = min(1, self.music_volume + 0.1)
                pygame.mixer.music.set_volume(self.music_volume)
            else:
                self.sfx_volume = min(1, self.sfx_volume + 0.1) 