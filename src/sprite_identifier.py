import pygame
import os
import sys

# Inicializa o Pygame
pygame.init()

# Configurações da janela
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Identificador de Sprites - Pac-Man")

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
GREEN = (0, 255, 0)

# Obtém o diretório do jogo
game_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spritesheet_path = os.path.join(game_directory, 'assets', 'sprites', 'spritesheet.png')

# Carrega a spritesheet
try:
    spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
    print(f"Spritesheet carregada com sucesso: {spritesheet_path}")
    spritesheet_width = spritesheet.get_width()
    spritesheet_height = spritesheet.get_height()
except pygame.error as e:
    print(f"Erro ao carregar spritesheet: {e}")
    pygame.quit()
    sys.exit()

# Variáveis para seleção e zoom
zoom_factor = 2.0
scroll_x = 0
scroll_y = 0
selection_start = None
selection_end = None
selections = []  # Lista para guardar seleções anteriores
current_name = ""  # Nome do sprite atual
show_grid = True
grid_size =  1 # Tamanho da grade em pixels

# Fontes
font = pygame.font.SysFont('Arial', 16)
font_title = pygame.font.SysFont('Arial', 24)

def draw_grid(surface, offset_x, offset_y, size):
    """Desenha uma grade na superfície."""
    if not show_grid:
        return
        
    width = surface.get_width()
    height = surface.get_height()
    
    # Desenha linhas verticais
    for x in range(0, width, size):
        x_pos = x - (offset_x % size)
        pygame.draw.line(surface, (50, 50, 50), (x_pos, 0), (x_pos, height), 1)
    
    # Desenha linhas horizontais
    for y in range(0, height, size):
        y_pos = y - (offset_y % size)
        pygame.draw.line(surface, (50, 50, 50), (0, y_pos), (width, y_pos), 1)

def draw_zoomed_spritesheet(surface, image, zoom, pos_x, pos_y):
    """Desenha a spritesheet com zoom."""
    new_width = int(image.get_width() * zoom)
    new_height = int(image.get_height() * zoom)
    zoomed_image = pygame.transform.scale(image, (new_width, new_height))
    
    # Área onde será exibida a spritesheet
    display_area = pygame.Rect(0, 70, SCREEN_WIDTH, SCREEN_HEIGHT - 200)
    
    # Calcula a área visível da spritesheet
    view_rect = pygame.Rect(pos_x, pos_y, display_area.width, display_area.height)
    
    # Desenha a parte visível da spritesheet
    surface.blit(zoomed_image, display_area.topleft, view_rect)
    
    return display_area

def get_image_coordinates(screen_x, screen_y, zoom, offset_x, offset_y, display_area):
    """Converte coordenadas da tela para coordenadas na imagem original."""
    if not display_area.collidepoint(screen_x, screen_y):
        return None
        
    # Coordenadas relativas à área de exibição
    rel_x = screen_x - display_area.x
    rel_y = screen_y - display_area.y
    
    # Converte para coordenadas na imagem original
    img_x = int((rel_x + offset_x) / zoom)
    img_y = int((rel_y + offset_y) / zoom)
    
    return img_x, img_y

def add_selection(start, end, name=""):
    """Adiciona uma seleção à lista."""
    if start and end:
        # Garante que start sempre seja o ponto superior esquerdo
        x1, y1 = min(start[0], end[0]), min(start[1], end[1])
        x2, y2 = max(start[0], end[0]), max(start[1], end[1])
        
        width = x2 - x1
        height = y2 - y1
        
        selections.append({
            'x': x1,
            'y': y1,
            'width': width,
            'height': height,
            'name': name
        })
        
        # Retorna a seleção formatada para copiar
        return f"({x1}, {y1}, {width}, {height})"
    return None

def export_selections():
    """Exporta as seleções para um arquivo Python."""
    if not selections:
        return False
        
    output_path = os.path.join(game_directory, 'src', 'sprite_coordinates.py')
    
    try:
        with open(output_path, 'w') as f:
            f.write("# Coordenadas dos sprites (x, y, largura, altura)\n\n")
            
            # Agrupa as seleções por nome (prefixo antes do primeiro '_')
            groups = {}
            for sel in selections:
                name = sel['name']
                prefix = name.split('_')[0] if '_' in name else 'misc'
                
                if prefix not in groups:
                    groups[prefix] = []
                
                groups[prefix].append(sel)
            
            # Escreve cada grupo
            for group_name, group_selections in groups.items():
                f.write(f"{group_name}_sprites = {{\n")
                
                # Subgrupos (usando o segundo nível do nome, se existir)
                subgroups = {}
                for sel in group_selections:
                    name_parts = sel['name'].split('_')
                    if len(name_parts) > 1:
                        subgroup = name_parts[1]
                        if subgroup not in subgroups:
                            subgroups[subgroup] = []
                        subgroups[subgroup].append(sel)
                    else:
                        if 'misc' not in subgroups:
                            subgroups['misc'] = []
                        subgroups['misc'].append(sel)
                
                # Escreve cada subgrupo
                for subgroup_name, subgroup_selections in subgroups.items():
                    if subgroup_name == 'misc' and len(subgroups) > 1:
                        continue  # Pula 'misc' se houver outros subgrupos
                        
                    # Se houver subgrupos válidos, criar uma estrutura aninhada
                    if subgroup_name != 'misc':
                        f.write(f"    '{subgroup_name}': [\n")
                        
                    # Escreve cada seleção
                    for sel in subgroup_selections:
                        coord_str = f"({sel['x']}, {sel['y']}, {sel['width']}, {sel['height']})"
                        
                        if subgroup_name != 'misc':
                            f.write(f"        {coord_str},  # {sel['name']}\n")
                        else:
                            key = sel['name'] if sel['name'] else f"sprite_{sel['x']}_{sel['y']}"
                            f.write(f"    '{key}': {coord_str},\n")
                    
                    if subgroup_name != 'misc':
                        f.write("    ],\n")
                
                f.write("}\n\n")
            
            # Escreve uma lista de todas as coordenadas
            f.write("# Lista completa de todas as coordenadas\n")
            f.write("all_sprites = [\n")
            for sel in selections:
                name = sel['name'] if sel['name'] else f"sprite_{sel['x']}_{sel['y']}"
                f.write(f"    ({sel['x']}, {sel['y']}, {sel['width']}, {sel['height']}),  # {name}\n")
            f.write("]\n")
            
        print(f"Coordenadas exportadas para: {output_path}")
        return True
    except Exception as e:
        print(f"Erro ao exportar coordenadas: {e}")
        return False

def main():
    """Função principal."""
    global scroll_x, scroll_y, zoom_factor, selection_start, selection_end, current_name, show_grid, grid_size
    
    clock = pygame.time.Clock()
    running = True
    dragging = False
    selecting = False
    typing = False
    
    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Gerencia eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if typing:
                        typing = False
                        current_name = ""
                    else:
                        running = False
                        
                elif event.key == pygame.K_RETURN:
                    if typing and selection_start and selection_end:
                        selection_text = add_selection(selection_start, selection_end, current_name)
                        print(f"Seleção adicionada: {selection_text} - Nome: {current_name}")
                        selection_start = None
                        selection_end = None
                        current_name = ""
                        typing = False
                        
                elif event.key == pygame.K_BACKSPACE:
                    if typing:
                        current_name = current_name[:-1]
                        
                elif event.key == pygame.K_g:
                    show_grid = not show_grid
                    
                elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                    grid_size = min(64, grid_size * 2)
                    
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    grid_size = max(1, grid_size // 2)
                    
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if export_selections():
                        print("Coordenadas salvas com sucesso!")
                    
                elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Desfaz a última seleção
                    if selections:
                        selections.pop()
                        print("Última seleção removida!")
                
                elif typing:
                    current_name += event.unicode
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo
                    if not typing:
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            selecting = True
                            display_area = draw_zoomed_spritesheet(screen, spritesheet, zoom_factor, scroll_x, scroll_y)
                            selection_start = get_image_coordinates(mouse_x, mouse_y, zoom_factor, scroll_x, scroll_y, display_area)
                        else:
                            dragging = True
                            drag_start_x, drag_start_y = mouse_x, mouse_y
                
                elif event.button == 4:  # Roda do mouse para cima
                    zoom_factor = min(10.0, zoom_factor * 1.1)
                    
                elif event.button == 5:  # Roda do mouse para baixo
                    zoom_factor = max(0.1, zoom_factor / 1.1)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Botão esquerdo
                    if selecting:
                        selecting = False
                        display_area = draw_zoomed_spritesheet(screen, spritesheet, zoom_factor, scroll_x, scroll_y)
                        selection_end = get_image_coordinates(mouse_x, mouse_y, zoom_factor, scroll_x, scroll_y, display_area)
                        
                        if selection_start and selection_end:
                            typing = True
                    
                    dragging = False
        
        # Atualiza a posição de rolagem durante o arrasto
        if dragging:
            scroll_x -= (mouse_x - drag_start_x) / 2
            scroll_y -= (mouse_y - drag_start_y) / 2
            scroll_x = max(0, min(scroll_x, spritesheet_width * zoom_factor - SCREEN_WIDTH))
            scroll_y = max(0, min(scroll_y, spritesheet_height * zoom_factor - SCREEN_HEIGHT + 200))
            drag_start_x, drag_start_y = mouse_x, mouse_y
        
        # Limpa a tela
        screen.fill(BLACK)
        
        # Desenha a spritesheet com zoom
        display_area = draw_zoomed_spritesheet(screen, spritesheet, zoom_factor, scroll_x, scroll_y)
        
        # Desenha a grade
        draw_grid(screen, int(scroll_x), int(scroll_y), int(grid_size * zoom_factor))
        
        # Mostra as coordenadas do mouse na imagem
        img_coords = get_image_coordinates(mouse_x, mouse_y, zoom_factor, scroll_x, scroll_y, display_area)
        if img_coords:
            coord_text = f"Posição: ({img_coords[0]}, {img_coords[1]})"
            text_surface = font.render(coord_text, True, WHITE)
            screen.blit(text_surface, (20, 30))
        
        # Desenha a seleção atual
        if selection_start and (selecting or selection_end):
            end_pos = selection_end if selection_end else img_coords
            
            if end_pos:
                start_screen_x = int((selection_start[0] * zoom_factor - scroll_x) + display_area.x)
                start_screen_y = int((selection_start[1] * zoom_factor - scroll_y) + display_area.y)
                
                end_screen_x = int((end_pos[0] * zoom_factor - scroll_x) + display_area.x)
                end_screen_y = int((end_pos[1] * zoom_factor - scroll_y) + display_area.y)
                
                select_rect = pygame.Rect(
                    min(start_screen_x, end_screen_x),
                    min(start_screen_y, end_screen_y),
                    abs(end_screen_x - start_screen_x),
                    abs(end_screen_y - start_screen_y)
                )
                
                pygame.draw.rect(screen, BLUE, select_rect, 2)
                
                # Mostra as dimensões da seleção
                width = abs(end_pos[0] - selection_start[0])
                height = abs(end_pos[1] - selection_start[1])
                
                sel_text = f"Seleção: ({min(selection_start[0], end_pos[0])}, {min(selection_start[1], end_pos[1])}, {width}, {height})"
                sel_surface = font.render(sel_text, True, WHITE)
                screen.blit(sel_surface, (20, 50))
        
        # Desenha seleções anteriores
        for sel in selections:
            rect_x = int((sel['x'] * zoom_factor - scroll_x) + display_area.x)
            rect_y = int((sel['y'] * zoom_factor - scroll_y) + display_area.y)
            rect_w = int(sel['width'] * zoom_factor)
            rect_h = int(sel['height'] * zoom_factor)
            
            pygame.draw.rect(screen, GREEN, (rect_x, rect_y, rect_w, rect_h), 1)
            
            # Exibe o nome da seleção
            if sel['name']:
                name_surface = font.render(sel['name'], True, GREEN)
                screen.blit(name_surface, (rect_x, rect_y - 20))
        
        # Desenha a interface
        pygame.draw.rect(screen, (30, 30, 30), (0, 0, SCREEN_WIDTH, 70))
        pygame.draw.rect(screen, (30, 30, 30), (0, SCREEN_HEIGHT - 130, SCREEN_WIDTH, 130))
        
        # Título
        title = font_title.render("Identificador de Sprites - Pac-Man", True, WHITE)
        screen.blit(title, (20, 10))
        
        # Instruções
        instructions = [
            "Shift+Clique para iniciar seleção | Ctrl+S para salvar | Ctrl+Z para desfazer | G para grade | +/- para tamanho da grade",
            f"Zoom: {zoom_factor:.1f}x | Total de seleções: {len(selections)} | Tamanho da grade: {grid_size}px"
        ]
        
        y_pos = SCREEN_HEIGHT - 120
        for instruction in instructions:
            instr_surface = font.render(instruction, True, WHITE)
            screen.blit(instr_surface, (20, y_pos))
            y_pos += 25
        
        # Campo de entrada para o nome do sprite
        if typing:
            pygame.draw.rect(screen, (50, 50, 50), (20, SCREEN_HEIGHT - 70, SCREEN_WIDTH - 40, 30))
            name_prompt = font.render("Digite o nome do sprite (e.g., pacman_right_1):", True, WHITE)
            screen.blit(name_prompt, (20, SCREEN_HEIGHT - 90))
            
            name_text = font.render(current_name, True, WHITE)
            screen.blit(name_text, (25, SCREEN_HEIGHT - 65))
            
            # Cursor piscante
            if pygame.time.get_ticks() % 1000 < 500:
                cursor_x = 25 + name_text.get_width()
                pygame.draw.line(screen, WHITE, (cursor_x, SCREEN_HEIGHT - 65), (cursor_x, SCREEN_HEIGHT - 45), 2)
        
        # Atualiza a tela
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()