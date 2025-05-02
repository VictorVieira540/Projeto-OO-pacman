import pygame
import os
import sys
from sprite_manager import SpriteManager

# Inicializa o Pygame
pygame.init()

# Configurações da janela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Visualizador de Sprites Pac-Man")

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

# Obtém o diretório do jogo (o diretório onde está este script)
game_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cria o gerenciador de sprites
sprite_manager = SpriteManager(game_directory)

# Fator de escala para melhor visualização
SCALE_FACTOR = 2.0

def draw_sprite_set(sprite_set, x, y, label):
    """Desenha um conjunto de sprites horizontalmente com um rótulo."""
    font = pygame.font.SysFont('Arial', 16)
    text = font.render(label, True, WHITE)
    screen.blit(text, (x, y - 20))
    
    if not sprite_set:
        text_error = font.render("Sprites não encontrados!", True, (255, 0, 0))
        screen.blit(text_error, (x, y))
        return
    
    for i, sprite in enumerate(sprite_set):
        scaled_sprite = sprite_manager.scale_sprite(sprite, SCALE_FACTOR)
        if scaled_sprite:
            screen.blit(scaled_sprite, (x + i * (scaled_sprite.get_width() + 10), y))

def draw_sprite(sprite, x, y, label):
    """Desenha um único sprite com um rótulo."""
    font = pygame.font.SysFont('Arial', 16)
    text = font.render(label, True, WHITE)
    screen.blit(text, (x, y - 20))
    
    if sprite:
        scaled_sprite = sprite_manager.scale_sprite(sprite, SCALE_FACTOR)
        if scaled_sprite:
            screen.blit(scaled_sprite, (x, y))
    else:
        text_error = font.render("Sprite não encontrado!", True, (255, 0, 0))
        screen.blit(text_error, (x, y))

def main():
    """Função principal."""
    clock = pygame.time.Clock()
    running = True
    
    # Carrega os sprites
    pacman_sprites = sprite_manager.get_pacman_sprites()
    ghost_red = sprite_manager.get_ghost_sprites('red')
    ghost_pink = sprite_manager.get_ghost_sprites('pink')
    ghost_blue = sprite_manager.get_ghost_sprites('blue')
    ghost_orange = sprite_manager.get_ghost_sprites('orange')
    fruit_sprites = sprite_manager.get_fruit_sprites()
    pellet_sprites = sprite_manager.get_pellet_sprites()
    
    while running:
        # Gerencia eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Limpa a tela
        screen.fill(BLACK)
        
        # Desenha uma grade para melhor visualização
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)
        
        # Informações sobre a visualização
        font = pygame.font.SysFont('Arial', 24)
        title = font.render("Visualizador de Sprites do Pac-Man", True, WHITE)
        screen.blit(title, (20, 20))
        
        instruction = pygame.font.SysFont('Arial', 16)
        instr_text = instruction.render("Pressione ESC para sair", True, WHITE)
        screen.blit(instr_text, (20, 50))
        
        # Desenha os sprites do Pac-Man
        y_pos = 100
        draw_sprite_set(pacman_sprites.get('right', []), 50, y_pos, "Pac-Man (Direita)")
        draw_sprite_set(pacman_sprites.get('left', []), 50, y_pos + 70, "Pac-Man (Esquerda)")
        draw_sprite_set(pacman_sprites.get('up', []), 50, y_pos + 140, "Pac-Man (Cima)")
        draw_sprite_set(pacman_sprites.get('down', []), 50, y_pos + 210, "Pac-Man (Baixo)")
        
        # Desenha fantasmas
        draw_sprite_set(ghost_red.get('right', []), 400, y_pos, "Fantasma Vermelho (Direita)")
        draw_sprite_set(ghost_red.get('left', []), 400, y_pos + 70, "Fantasma Vermelho (Esquerda)")
        
        draw_sprite_set(ghost_pink.get('right', []), 400, y_pos + 140, "Fantasma Rosa (Direita)")
        draw_sprite_set(ghost_blue.get('right', []), 400, y_pos + 210, "Fantasma Azul (Direita)")
        draw_sprite_set(ghost_orange.get('right', []), 400, y_pos + 280, "Fantasma Laranja (Direita)")
        
        # Fantasmas especiais (vulneráveis)
        y_ghost_special = y_pos + 350
        draw_sprite_set(ghost_red.get('vulnerable', []), 50, y_ghost_special, "Fantasma Vulnerável")
        draw_sprite_set(ghost_red.get('flashing', []), 250, y_ghost_special, "Fantasma Piscando")
        
        # Olhos dos fantasmas
        eyes = ghost_red.get('eyes', {})
        if eyes:
            draw_sprite(eyes.get('right'), 50, y_ghost_special + 70, "Olhos (Direita)")
            draw_sprite(eyes.get('left'), 150, y_ghost_special + 70, "Olhos (Esquerda)")
            draw_sprite(eyes.get('up'), 250, y_ghost_special + 70, "Olhos (Cima)")
            draw_sprite(eyes.get('down'), 350, y_ghost_special + 70, "Olhos (Baixo)")
        
        # Frutas
        fruit_x = 50
        fruit_y = y_ghost_special + 140
        if fruit_sprites:
            for i, (name, sprite) in enumerate(fruit_sprites.items()):
                col = i % 4
                row = i // 4
                draw_sprite(sprite, fruit_x + col * 100, fruit_y + row * 70, name.capitalize())
        
        # Pellets
        pellet_y = fruit_y + 140
        if pellet_sprites:
            draw_sprite(pellet_sprites.get('small'), 50, pellet_y, "Pellet Pequeno")
            draw_sprite(pellet_sprites.get('power'), 150, pellet_y, "Power Pellet")
        
        # Atualiza a tela
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()