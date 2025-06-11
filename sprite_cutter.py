#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ferramenta Visual de Recorte de Sprites - Pac-Man
Permite recortar sprites 16x16 do spritesheet de forma interativa com grade, zoom e salvamento.
"""

import pygame
import os
import sys
import json
from datetime import datetime

class SpriteCutter:
    def __init__(self):
        # Configurações da janela
        self.WINDOW_WIDTH = 1200
        self.WINDOW_HEIGHT = 800
        self.SPRITE_SIZE = 16
        
        # Inicializar pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Ferramenta de Recorte de Sprites - Pac-Man")
        self.clock = pygame.time.Clock()
        
        # Cores
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        self.DARK_GRAY = (64, 64, 64)
        
        # Estado da visualização
        self.zoom = 2.0
        self.min_zoom = 0.5
        self.max_zoom = 8.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Estado do movimento
        self.is_dragging = False
        self.last_mouse_pos = (0, 0)
        self.movement_speed = 5
        self.fast_movement_speed = 20
        self.pixel_movement_speed = 1  # Movimento pixel a pixel
        
        # Sistema de movimento preciso para seleção
        self.key_repeat_delay = 300  # ms antes de começar repetição
        self.key_repeat_rate = 50   # ms entre repetições
        self.pressed_keys = {}  # Controla timing das teclas pressionadas
        
        # Estado da grade
        self.show_grid = True
        self.grid_type = "sprite"  # "sprite" (16x16) ou "pixel" (1x1)
        self.grid_color = self.YELLOW
        self.pixel_grid_color = (100, 100, 100)  # Cinza para grade de pixels
        
        # Estado da seleção
        self.selection_rect = None
        self.selection_start = None
        
        # Spritesheet
        self.spritesheet = None
        self.spritesheet_path = "assets/sprites/spritesheet.png"
        
        # Diretório de saída
        self.output_dir = "assets/sprites/individual"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Lista de sprites salvos
        self.saved_sprites = []
        self.load_saved_sprites()
        
        # Interface
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Estado da interface
        self.show_help = True
        self.input_mode = False
        self.input_text = ""
        
        # Carregar spritesheet
        self.load_spritesheet()
    
    def load_spritesheet(self):
        """Carrega o spritesheet."""
        try:
            self.spritesheet = pygame.image.load(self.spritesheet_path).convert_alpha()
            print(f"Spritesheet carregado: {self.spritesheet_path}")
            print(f"Dimensões: {self.spritesheet.get_width()}x{self.spritesheet.get_height()}")
        except pygame.error as e:
            print(f"Erro ao carregar spritesheet: {e}")
            # Criar uma imagem de placeholder
            self.spritesheet = pygame.Surface((320, 240))
            self.spritesheet.fill(self.GRAY)
    
    def load_saved_sprites(self):
        """Carrega a lista de sprites já salvos."""
        try:
            if os.path.exists("saved_sprites.json"):
                with open("saved_sprites.json", "r", encoding="utf-8") as f:
                    self.saved_sprites = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar sprites salvos: {e}")
            self.saved_sprites = []
    
    def save_sprite_list(self):
        """Salva a lista de sprites."""
        try:
            with open("saved_sprites.json", "w", encoding="utf-8") as f:
                json.dump(self.saved_sprites, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar lista de sprites: {e}")
    
    def screen_to_sprite_coords(self, screen_x, screen_y):
        """Converte coordenadas da tela para coordenadas do sprite."""
        sprite_x = (screen_x - self.offset_x) / self.zoom
        sprite_y = (screen_y - self.offset_y) / self.zoom
        return int(sprite_x), int(sprite_y)
    
    def sprite_to_screen_coords(self, sprite_x, sprite_y):
        """Converte coordenadas do sprite para coordenadas da tela."""
        screen_x = sprite_x * self.zoom + self.offset_x
        screen_y = sprite_y * self.zoom + self.offset_y
        return int(screen_x), int(screen_y)
    
    def snap_to_grid(self, x, y):
        """Ajusta coordenadas para a grade."""
        if self.grid_type == "pixel":
            # Sem ajuste para grade de pixels
            return int(x), int(y)
        else:
            # Ajuste para grade de sprites 16x16
            grid_x = (x // self.SPRITE_SIZE) * self.SPRITE_SIZE
            grid_y = (y // self.SPRITE_SIZE) * self.SPRITE_SIZE
            return grid_x, grid_y
    
    def draw_spritesheet(self):
        """Desenha o spritesheet na tela."""
        if not self.spritesheet:
            return
        
        # Calcular tamanho escalado
        scaled_width = int(self.spritesheet.get_width() * self.zoom)
        scaled_height = int(self.spritesheet.get_height() * self.zoom)
        
        # Escalar spritesheet
        scaled_sprite = pygame.transform.scale(self.spritesheet, (scaled_width, scaled_height))
        
        # Desenhar spritesheet
        self.screen.blit(scaled_sprite, (self.offset_x, self.offset_y))
    
    def draw_grid(self):
        """Desenha a grade sobre o spritesheet."""
        if not self.show_grid or not self.spritesheet:
            return
        
        # Calcular limites visíveis
        sprite_width = self.spritesheet.get_width()
        sprite_height = self.spritesheet.get_height()
        
        if self.grid_type == "pixel":
            # Grade pixel a pixel (só visível com zoom alto)
            if self.zoom >= 3.0:  # Só mostrar grade de pixels com zoom suficiente
                self._draw_pixel_grid(sprite_width, sprite_height)
        else:
            # Grade de sprites 16x16
            self._draw_sprite_grid(sprite_width, sprite_height)
    
    def _draw_pixel_grid(self, sprite_width, sprite_height):
        """Desenha grade pixel a pixel."""
        # Calcular área visível
        screen_rect = pygame.Rect(0, 0, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        
        # Linhas verticais
        start_x = max(0, int(-self.offset_x / self.zoom))
        end_x = min(sprite_width, int((self.WINDOW_WIDTH - self.offset_x) / self.zoom) + 1)
        
        for x in range(start_x, end_x + 1):
            screen_x, screen_y1 = self.sprite_to_screen_coords(x, 0)
            screen_x, screen_y2 = self.sprite_to_screen_coords(x, sprite_height)
            
            if 0 <= screen_x <= self.WINDOW_WIDTH:
                pygame.draw.line(self.screen, self.pixel_grid_color, (screen_x, screen_y1), (screen_x, screen_y2), 1)
        
        # Linhas horizontais
        start_y = max(0, int(-self.offset_y / self.zoom))
        end_y = min(sprite_height, int((self.WINDOW_HEIGHT - self.offset_y) / self.zoom) + 1)
        
        for y in range(start_y, end_y + 1):
            screen_x1, screen_y = self.sprite_to_screen_coords(0, y)
            screen_x2, screen_y = self.sprite_to_screen_coords(sprite_width, y)
            
            if 0 <= screen_y <= self.WINDOW_HEIGHT:
                pygame.draw.line(self.screen, self.pixel_grid_color, (screen_x1, screen_y), (screen_x2, screen_y), 1)
    
    def _draw_sprite_grid(self, sprite_width, sprite_height):
        """Desenha grade de sprites 16x16."""
        # Desenhar linhas verticais
        for x in range(0, sprite_width + 1, self.SPRITE_SIZE):
            start_x, start_y = self.sprite_to_screen_coords(x, 0)
            end_x, end_y = self.sprite_to_screen_coords(x, sprite_height)
            
            if 0 <= start_x <= self.WINDOW_WIDTH:
                pygame.draw.line(self.screen, self.grid_color, (start_x, start_y), (end_x, end_y), 1)
        
        # Desenhar linhas horizontais
        for y in range(0, sprite_height + 1, self.SPRITE_SIZE):
            start_x, start_y = self.sprite_to_screen_coords(0, y)
            end_x, end_y = self.sprite_to_screen_coords(sprite_width, y)
            
            if 0 <= start_y <= self.WINDOW_HEIGHT:
                pygame.draw.line(self.screen, self.grid_color, (start_x, start_y), (end_x, end_y), 1)
    
    def draw_selection(self):
        """Desenha a seleção atual."""
        if not self.selection_rect:
            return
        
        # Converter para coordenadas da tela
        x, y = self.sprite_to_screen_coords(self.selection_rect[0], self.selection_rect[1])
        w = self.selection_rect[2] * self.zoom
        h = self.selection_rect[3] * self.zoom
        
        # Desenhar retângulo de seleção
        pygame.draw.rect(self.screen, self.RED, (x, y, w, h), 2)
        
        # Desenhar cantos
        corner_size = 6
        pygame.draw.rect(self.screen, self.RED, (x - corner_size//2, y - corner_size//2, corner_size, corner_size))
        pygame.draw.rect(self.screen, self.RED, (x + w - corner_size//2, y - corner_size//2, corner_size, corner_size))
        pygame.draw.rect(self.screen, self.RED, (x - corner_size//2, y + h - corner_size//2, corner_size, corner_size))
        pygame.draw.rect(self.screen, self.RED, (x + w - corner_size//2, y + h - corner_size//2, corner_size, corner_size))
    
    def draw_ui(self):
        """Desenha a interface do usuário."""
        # Painel de informações
        panel_height = 120
        panel_rect = pygame.Rect(0, self.WINDOW_HEIGHT - panel_height, self.WINDOW_WIDTH, panel_height)
        pygame.draw.rect(self.screen, self.DARK_GRAY, panel_rect)
        pygame.draw.line(self.screen, self.WHITE, (0, self.WINDOW_HEIGHT - panel_height), (self.WINDOW_WIDTH, self.WINDOW_HEIGHT - panel_height), 2)
        
        # Informações do zoom e posição
        mouse_x, mouse_y = pygame.mouse.get_pos()
        sprite_x, sprite_y = self.screen_to_sprite_coords(mouse_x, mouse_y)
        grid_x, grid_y = self.snap_to_grid(sprite_x, sprite_y)
        
        info_lines = [
            f"Zoom: {self.zoom:.1f}x | Posição: ({sprite_x}, {sprite_y}) | Grade: ({grid_x}, {grid_y})",
            f"Sprites salvos: {len(self.saved_sprites)} | Grade: {self.grid_type} | Saída: {self.output_dir}",
        ]
        
        if self.selection_rect:
            info_lines.append(f"Seleção: {self.selection_rect[2]}x{self.selection_rect[3]} em ({self.selection_rect[0]}, {self.selection_rect[1]})")
        
        if self.input_mode:
            info_lines.append(f"Nome do sprite: {self.input_text}_")
        else:
            # Mostrar modo atual
            grid_info = "Grade: 16x16 (sprites)" if self.grid_type == "sprite" else "Grade: 1x1 (pixels)"
            if self.grid_type == "pixel" and self.zoom < 3.0:
                grid_info += " [zoom baixo - grade oculta]"
            info_lines.append(grid_info)
        
        y_offset = self.WINDOW_HEIGHT - panel_height + 10
        for line in info_lines:
            text_surface = self.small_font.render(line, True, self.WHITE)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 20
        
        # Ajuda
        if self.show_help:
            help_panel_width = 300
            help_panel_rect = pygame.Rect(self.WINDOW_WIDTH - help_panel_width, 0, help_panel_width, 350)
            pygame.draw.rect(self.screen, self.DARK_GRAY, help_panel_rect)
            pygame.draw.rect(self.screen, self.WHITE, help_panel_rect, 2)
            
            help_lines = [
                "CONTROLES:",
                "",
                "Mouse:",
                "• Roda: Zoom in/out",
                "• Arrastar: Mover visualização",
                "• Clique: Selecionar 16x16",
                "",
                "Movimento:",
                "• WASD: Mover visualização",
                "• Setas: Mover seleção (1px/clique)",
                "• Setas (segurar): Movimento rápido",
                "• Shift/Ctrl: Modificam WASD apenas",
                "",
                "Grade:",
                "• G: Mostrar/ocultar grade",
                "• P: Alternar grade (sprite/pixel)",
                "",
                "Outras teclas:",
                "• Enter: Salvar seleção",
                "• C: Limpar seleção",
                "• Esc: Cancelar/Sair",
                "• H: Mostrar/ocultar ajuda",
                "• R: Resetar zoom/posição",
                "",
                "Para salvar:",
                "1. Clique em um sprite",
                "2. Digite o nome",
                "3. Pressione Enter",
                "Obs: Seleção permanece ativa"
            ]
            
            y_offset = 10
            for line in help_lines:
                if line == "CONTROLES:":
                    text_surface = self.font.render(line, True, self.YELLOW)
                elif line.startswith("•") or line.endswith(":"):
                    text_surface = self.small_font.render(line, True, self.WHITE)
                else:
                    text_surface = self.small_font.render(line, True, self.LIGHT_GRAY)
                
                self.screen.blit(text_surface, (self.WINDOW_WIDTH - help_panel_width + 10, y_offset))
                y_offset += 16
    
    def handle_mouse_click(self, pos):
        """Manipula cliques do mouse."""
        sprite_x, sprite_y = self.screen_to_sprite_coords(pos[0], pos[1])
        
        # Ajustar à grade
        grid_x, grid_y = self.snap_to_grid(sprite_x, sprite_y)
        
        # Verificar se está dentro do spritesheet
        if (0 <= grid_x < self.spritesheet.get_width() - self.SPRITE_SIZE and 
            0 <= grid_y < self.spritesheet.get_height() - self.SPRITE_SIZE):
            
            self.selection_rect = (grid_x, grid_y, self.SPRITE_SIZE, self.SPRITE_SIZE)
            print(f"Selecionado sprite em ({grid_x}, {grid_y}) - Modo: {self.grid_type}")
    
    def save_selected_sprite(self, name):
        """Salva o sprite selecionado."""
        if not self.selection_rect or not name.strip():
            return False
        
        try:
            # Extrair sprite
            sprite_rect = pygame.Rect(*self.selection_rect)
            sprite_surface = pygame.Surface((self.SPRITE_SIZE, self.SPRITE_SIZE), pygame.SRCALPHA)
            sprite_surface.blit(self.spritesheet, (0, 0), sprite_rect)
            
            # Salvar arquivo
            clean_name = name.strip().replace(" ", "_").lower()
            filename = f"{clean_name}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            pygame.image.save(sprite_surface, filepath)
            
            # Adicionar à lista
            sprite_info = {
                "name": clean_name,
                "filename": filename,
                "position": self.selection_rect[:2],
                "size": self.selection_rect[2:],
                "timestamp": datetime.now().isoformat()
            }
            
            self.saved_sprites.append(sprite_info)
            self.save_sprite_list()
            
            print(f"Sprite salvo: {filename} (seleção mantida)")
            return True
            
        except Exception as e:
            print(f"Erro ao salvar sprite: {e}")
            return False
    
    def handle_keyboard(self, keys):
        """Manipula entrada do teclado para movimento da visualização."""
        # Determinar velocidade baseada nos modificadores
        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            # Ctrl = movimento pixel a pixel
            speed = self.pixel_movement_speed
        elif keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            # Shift = movimento rápido
            speed = self.fast_movement_speed
        else:
            # Normal = movimento médio
            speed = self.movement_speed
        
        # WASD sempre move a visualização
        if keys[pygame.K_w]:
            self.offset_y += speed
        if keys[pygame.K_s]:
            self.offset_y -= speed
        if keys[pygame.K_a]:
            self.offset_x += speed
        if keys[pygame.K_d]:
            self.offset_x -= speed
        
        # Se não há seleção, setas também movem visualização
        if not self.selection_rect:
            if keys[pygame.K_UP]:
                self.offset_y += speed
            if keys[pygame.K_DOWN]:
                self.offset_y -= speed
            if keys[pygame.K_LEFT]:
                self.offset_x += speed
            if keys[pygame.K_RIGHT]:
                self.offset_x -= speed
    
    def handle_selection_arrow_key(self, key):
        """Manipula movimento preciso da seleção (1 pixel por clique)."""
        if not self.selection_rect:
            return
        
        # Movimento de 1 pixel sempre
        if key == pygame.K_UP:
            self.move_selection(0, -1)
        elif key == pygame.K_DOWN:
            self.move_selection(0, 1)
        elif key == pygame.K_LEFT:
            self.move_selection(-1, 0)
        elif key == pygame.K_RIGHT:
            self.move_selection(1, 0)
    
    def handle_selection_continuous_movement(self, keys):
        """Manipula movimento contínuo da seleção após delay."""
        current_time = pygame.time.get_ticks()
        
        for key, start_time in list(self.pressed_keys.items()):
            # Verificar se passou o delay inicial
            if current_time - start_time > self.key_repeat_delay:
                # Movimento contínuo mais rápido
                if (current_time - start_time) % self.key_repeat_rate < 16:  # ~60fps
                    if key == pygame.K_UP:
                        self.move_selection(0, -3)
                    elif key == pygame.K_DOWN:
                        self.move_selection(0, 3)
                    elif key == pygame.K_LEFT:
                        self.move_selection(-3, 0)
                    elif key == pygame.K_RIGHT:
                        self.move_selection(3, 0)
    
    def move_selection(self, dx, dy):
        """Move a seleção atual."""
        if not self.selection_rect:
            return
        
        x, y, w, h = self.selection_rect
        new_x = x + dx
        new_y = y + dy
        
        # Verificar limites do spritesheet
        if (0 <= new_x < self.spritesheet.get_width() - w and 
            0 <= new_y < self.spritesheet.get_height() - h):
            
            self.selection_rect = (new_x, new_y, w, h)
            # Não imprimir para movimento contínuo (muito spam)
            if abs(dx) <= 1 and abs(dy) <= 1:
                print(f"Seleção movida para ({new_x}, {new_y}) - Modo: {self.grid_type}")
    
    def reset_view(self):
        """Reseta zoom e posição."""
        self.zoom = 2.0
        self.offset_x = 50
        self.offset_y = 50
    
    def run(self):
        """Loop principal da aplicação."""
        running = True
        
        while running:
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if self.input_mode:
                        # Modo de entrada de texto
                        if event.key == pygame.K_RETURN:
                            self.save_selected_sprite(self.input_text)
                            # Manter seleção ativa após salvar
                            self.input_mode = False
                            self.input_text = ""
                        elif event.key == pygame.K_ESCAPE:
                            self.input_mode = False
                            self.input_text = ""
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            if event.unicode.isprintable():
                                self.input_text += event.unicode
                    else:
                        # Modo normal
                        if event.key == pygame.K_ESCAPE:
                            if self.selection_rect:
                                self.selection_rect = None
                            else:
                                running = False
                        elif event.key == pygame.K_g:
                            self.show_grid = not self.show_grid
                        elif event.key == pygame.K_p:
                            # Alternar tipo de grade
                            self.grid_type = "pixel" if self.grid_type == "sprite" else "sprite"
                            print(f"Tipo de grade: {self.grid_type}")
                        elif event.key == pygame.K_h:
                            self.show_help = not self.show_help
                        elif event.key == pygame.K_r:
                            self.reset_view()
                        elif event.key == pygame.K_c:
                            # Limpar seleção
                            self.selection_rect = None
                            print("Seleção limpa")
                        elif event.key == pygame.K_RETURN:
                            if self.selection_rect:
                                self.input_mode = True
                                self.input_text = ""
                        
                        # Movimento preciso da seleção com setas (1 pixel por clique)
                        elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                            if self.selection_rect:
                                self.handle_selection_arrow_key(event.key)
                                # Registrar tecla pressionada para repetição
                                self.pressed_keys[event.key] = pygame.time.get_ticks()
                
                elif event.type == pygame.KEYUP:
                    # Remover tecla do controle de repetição
                    if event.key in self.pressed_keys:
                        del self.pressed_keys[event.key]
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Botão esquerdo
                        if not self.input_mode:
                            self.handle_mouse_click(event.pos)
                        self.is_dragging = True
                        self.last_mouse_pos = event.pos
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Botão esquerdo
                        self.is_dragging = False
                
                elif event.type == pygame.MOUSEMOTION:
                    if self.is_dragging and not self.input_mode:
                        dx = event.pos[0] - self.last_mouse_pos[0]
                        dy = event.pos[1] - self.last_mouse_pos[1]
                        self.offset_x += dx
                        self.offset_y += dy
                        self.last_mouse_pos = event.pos
                
                elif event.type == pygame.MOUSEWHEEL:
                    # Zoom
                    old_zoom = self.zoom
                    if event.y > 0:  # Scroll up
                        self.zoom = min(self.zoom * 1.2, self.max_zoom)
                    else:  # Scroll down
                        self.zoom = max(self.zoom / 1.2, self.min_zoom)
                    
                    # Ajustar offset para manter o mouse centrado
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    zoom_factor = self.zoom / old_zoom
                    self.offset_x = mouse_x - (mouse_x - self.offset_x) * zoom_factor
                    self.offset_y = mouse_y - (mouse_y - self.offset_y) * zoom_factor
            
            # Movimento contínuo
            keys = pygame.key.get_pressed()
            if not self.input_mode:
                self.handle_keyboard(keys)
                # Movimento contínuo da seleção (após delay)
                if self.selection_rect:
                    self.handle_selection_continuous_movement(keys)
            
            # Renderização
            self.screen.fill(self.BLACK)
            
            self.draw_spritesheet()
            self.draw_grid()
            self.draw_selection()
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

def main():
    """Função principal."""
    print("=== Ferramenta Visual de Recorte de Sprites ===")
    print("Carregando...")
    
    # Verificar se o spritesheet existe
    if not os.path.exists("assets/sprites/spritesheet.png"):
        print("AVISO: Spritesheet não encontrado em assets/sprites/spritesheet.png")
        print("Certifique-se de que o arquivo existe ou será criada uma imagem de placeholder.")
    
    # Criar e executar a ferramenta
    try:
        cutter = SpriteCutter()
        cutter.run()
    except Exception as e:
        print(f"Erro ao executar a ferramenta: {e}")
        return
    
    print("Ferramenta encerrada.")

if __name__ == "__main__":
    main() 