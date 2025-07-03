import pygame
import json
import os
from typing import Dict, Any, List, Tuple
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# Constantes do editor
CELL_SIZE = 20
GRID_WIDTH = 35
GRID_HEIGHT = 25
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE + 200  # Espaço extra para UI
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 100

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Tipos de células
EMPTY = 0
WALL = 1
PELLET = 2
POWER_UP = 3
PLAYER_SPAWN = 4
GHOST_RED = 5
GHOST_PINK = 6
GHOST_CYAN = 7
GHOST_ORANGE = 8

# Defina um valor especial para o tipo 'Preencher conectados'
FILL_CONNECTED = -1

# Cores para cada tipo
CELL_COLORS = {
    EMPTY: WHITE,
    WALL: BLACK,
    PELLET: YELLOW,
    POWER_UP: GREEN,
    PLAYER_SPAWN: BLUE,
    GHOST_RED: RED,
    GHOST_PINK: PINK,
    GHOST_CYAN: CYAN,
    GHOST_ORANGE: ORANGE
}

# Nomes dos tipos
CELL_NAMES = {
    FILL_CONNECTED: "Preencher conectados",
    EMPTY: "Vazio",
    WALL: "Parede",
    PELLET: "Pellet", 
    POWER_UP: "Power-up",
    PLAYER_SPAWN: "Jogador",
    GHOST_RED: "Fantasma Vermelho",
    GHOST_PINK: "Fantasma Rosa",
    GHOST_CYAN: "Fantasma Ciano",
    GHOST_ORANGE: "Fantasma Laranja"
}

class MapEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Editor de Mapas Pac-Man")
        
        self.scale = 1.0
        self.update_fonts()
        
        # Grid do mapa
        self.grid = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Tipo de célula selecionada
        self.selected_type = WALL
        
        # Estado do mouse
        self.mouse_down = False
        
        # Metadados do mapa
        self.map_metadata = {
            "name": "Novo Mapa",
            "difficulty": 200,
            "description": "Mapa criado no editor"
        }
        
        # Arquivo atualmente carregado (para controle de sobrescrita)
        self.current_file = None
        
        # Inicializar tkinter para dialogs
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Adicione um atributo para controlar o modo de preenchimento de pellets conectados
        self.fill_connected_mode = False
        
    def update_fonts(self):
        font_size = int(24 * self.scale)
        small_font_size = int(18 * self.scale)
        self.font = pygame.font.Font(None, max(12, font_size))
        self.small_font = pygame.font.Font(None, max(8, small_font_size))

    def get_cell_at_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        x, y = pos
        cell_size = int(CELL_SIZE * self.scale)
        grid_x = x // cell_size
        grid_y = y // cell_size
        return grid_x, grid_y
    
    def is_valid_cell(self, x: int, y: int) -> bool:
        """Verifica se as coordenadas são válidas"""
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT
    
    def draw_grid(self):
        cell_size = int(CELL_SIZE * self.scale)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                color = CELL_COLORS[self.grid[y][x]]
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, GRAY, rect, 1)
                if self.grid[y][x] == PLAYER_SPAWN:
                    center = (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2)
                    pygame.draw.circle(self.screen, WHITE, center, int(6 * self.scale))
                elif self.grid[y][x] in [GHOST_RED, GHOST_PINK, GHOST_CYAN, GHOST_ORANGE]:
                    center = (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2)
                    pygame.draw.circle(self.screen, WHITE, center, int(4 * self.scale))
    
    def draw_ui(self):
        cell_size = int(CELL_SIZE * self.scale)
        ui_x = GRID_WIDTH * cell_size + int(10 * self.scale)
        # Título
        title = self.font.render("Editor de Mapas", True, BLACK)
        self.screen.blit(title, (ui_x, int(10 * self.scale)))
        map_name = self.small_font.render(f"Mapa: {self.map_metadata['name']}", True, BLACK)
        self.screen.blit(map_name, (ui_x, int(30 * self.scale)))
        if self.current_file:
            import os
            file_status = self.small_font.render(f"Editando: {os.path.basename(self.current_file)}", True, (100, 100, 100))
            self.screen.blit(file_status, (ui_x, int(45 * self.scale)))
        selected_text = self.font.render("Selecionado:", True, BLACK)
        self.screen.blit(selected_text, (ui_x, int(65 * self.scale)))
        selected_name = self.small_font.render(CELL_NAMES[self.selected_type], True, BLACK)
        self.screen.blit(selected_name, (ui_x, int(90 * self.scale)))
        color_rect = pygame.Rect(ui_x, int(110 * self.scale), int(30 * self.scale), int(20 * self.scale))
        color = CELL_COLORS.get(self.selected_type, GRAY)
        pygame.draw.rect(self.screen, color, color_rect)
        pygame.draw.rect(self.screen, BLACK, color_rect, 2)
        y_offset = int(145 * self.scale)
        self.screen.blit(self.font.render("Tipos (0-9):", True, BLACK), (ui_x, y_offset))
        for i, (cell_type, name) in enumerate(CELL_NAMES.items()):
            y = y_offset + int(25 * self.scale) + i * int(20 * self.scale)
            if cell_type == FILL_CONNECTED:
                key_text = "-: Preencher conectados"
            else:
                key_text = f"{i}: {name}"
            color = BLACK if cell_type != self.selected_type else RED
            text = self.small_font.render(key_text, True, color)
            self.screen.blit(text, (ui_x, y))
        controls_y = y_offset + int(25 * self.scale) + len(CELL_NAMES) * int(20 * self.scale) + int(20 * self.scale)
        controls = [
            "Controles:",
            "Click: Colocar/Remover",
            "Arrastar: Pintar",
            "N: Novo mapa",
            "S: Salvar",
            "L: Carregar/Editar", 
            "M: Metadados",
            "C: Limpar tudo",
            "P: Auto-preencher pellets",
            "B: Gerar bordas",
            "-: Preencher conectados"
        ]
        for i, control in enumerate(controls):
            color = BLACK if i == 0 else GRAY
            font = self.font if i == 0 else self.small_font
            text = font.render(control, True, color)
            self.screen.blit(text, (ui_x, controls_y + i * int(18 * self.scale)))
        mouse_pos = pygame.mouse.get_pos()
        grid_x, grid_y = self.get_cell_at_pos(mouse_pos)
        if self.is_valid_cell(grid_x, grid_y):
            coord_text = self.small_font.render(f"Mouse: ({grid_x}, {grid_y})", True, BLACK)
            self.screen.blit(coord_text, (ui_x, controls_y + len(controls)*int(18 * self.scale) + int(20 * self.scale)))

    def handle_click(self, pos: Tuple[int, int], button: int):
        """Manipula cliques do mouse"""
        x, y = self.get_cell_at_pos(pos)
        
        if not self.is_valid_cell(x, y):
            return
            
        if button == 1:  # Botão esquerdo - colocar
            if self.selected_type == FILL_CONNECTED:
                self.fill_connected_pellets(x, y)
                print("Preenchimento de pellets conectados concluído.")
                return
            # Limpar spawns únicos se necessário
            if self.selected_type in [PLAYER_SPAWN, GHOST_RED, GHOST_PINK, GHOST_CYAN, GHOST_ORANGE]:
                self.clear_spawn_type(self.selected_type)
            self.grid[y][x] = self.selected_type
            
        elif button == 3:  # Botão direito - remover
            self.grid[y][x] = EMPTY
    
    def clear_spawn_type(self, spawn_type: int):
        """Remove todos os spawns do tipo especificado"""
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] == spawn_type:
                    self.grid[y][x] = EMPTY
    
    def save_map(self):
        """Salva o mapa no formato JSON"""
        try:
            # --- NOVO: Validação de spawns obrigatórios ---
            required_spawns = {
                "Jogador": PLAYER_SPAWN,
                "Fantasma Vermelho": GHOST_RED,
                "Fantasma Rosa": GHOST_PINK,
                "Fantasma Ciano": GHOST_CYAN,
                "Fantasma Laranja": GHOST_ORANGE
            }
            missing = []
            for name, cell_type in required_spawns.items():
                found = False
                for y in range(GRID_HEIGHT):
                    for x in range(GRID_WIDTH):
                        if self.grid[y][x] == cell_type:
                            found = True
                            break
                    if found:
                        break
                if not found:
                    missing.append(name)
            if missing:
                messagebox.showerror("Erro ao salvar", f"Faltando os seguintes spawns obrigatórios:\n- " + "\n- ".join(missing))
                return
            # --- FIM NOVO ---

            filename = None
            
            # Se há um arquivo carregado, perguntar ao usuário o que fazer
            if self.current_file:
                import os
                current_name = os.path.basename(self.current_file)
                
                choice = messagebox.askyesnocancel(
                    "Salvar Mapa",
                    f"Você está editando '{current_name}'.\n\n"
                    f"Sim = Sobrescrever arquivo original\n"
                    f"Não = Salvar como novo arquivo\n"
                    f"Cancelar = Cancelar operação"
                )
                
                if choice is None:  # Cancelar
                    return
                elif choice:  # Sim - Sobrescrever
                    filename = self.current_file
                else:  # Não - Salvar como novo
                    # Sugerir nome baseado no original
                    base_name = os.path.splitext(current_name)[0]
                    suggested_name = f"{base_name}_editado.json"
                    
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".json",
                        filetypes=[("JSON files", "*.json")],
                        initialdir="assets/maps/",
                        initialfile=suggested_name
                    )
            else:
                # Novo mapa - sempre pedir local
                filename = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json")],
                    initialdir="assets/maps/"
                )
            
            if not filename:
                return
            
            # Encontrar spawn points
            spawn_positions = {}
            
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    cell = self.grid[y][x]
                    if cell == PLAYER_SPAWN:
                        spawn_positions["player"] = {"x": x, "y": y}
                    elif cell == GHOST_RED:
                        spawn_positions["ghost_red"] = {"x": x, "y": y}
                    elif cell == GHOST_PINK:
                        spawn_positions["ghost_pink"] = {"x": x, "y": y}
                    elif cell == GHOST_CYAN:
                        spawn_positions["ghost_cyan"] = {"x": x, "y": y}
                    elif cell == GHOST_ORANGE:
                        spawn_positions["ghost_orange"] = {"x": x, "y": y}
            
            # Converter grid para formato do jogo
            layout = []
            for y in range(GRID_HEIGHT):
                row = []
                for x in range(GRID_WIDTH):
                    cell = self.grid[y][x]
                    if cell in [PLAYER_SPAWN, GHOST_RED, GHOST_PINK, GHOST_CYAN, GHOST_ORANGE]:
                        row.append(EMPTY)  # Spawns não ficam no layout
                    else:
                        row.append(cell)
                layout.append(row)
            
            # Criar estrutura do mapa
            map_data = {
                "metadata": self.map_metadata,
                "spawn_positions": spawn_positions,
                "layout": layout
            }
            
            # Salvar arquivo
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(map_data, f, indent=2, ensure_ascii=False)
            
            # Atualizar arquivo atual se foi salvo como novo
            if filename != self.current_file:
                self.current_file = filename
                action = "salvo como novo arquivo"
            else:
                action = "sobrescrito"
            
            import os
            filename_display = os.path.basename(filename)
            messagebox.showinfo("Sucesso", f"Mapa {action}:\n{filename_display}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
    
    def load_map(self):
        """Carrega um mapa existente"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")],
                initialdir="assets/maps/"
            )
            
            if not filename:
                return
            
            with open(filename, 'r', encoding='utf-8') as f:
                map_data = json.load(f)
            
            # Carregar metadados
            metadata = map_data.get("metadata", {})
            self.map_metadata["name"] = metadata.get("name", "Mapa Carregado")
            self.map_metadata["difficulty"] = metadata.get("difficulty", 50)
            self.map_metadata["description"] = metadata.get("description", "Mapa carregado do arquivo")
            
            # Limpar grid
            self.grid = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
            
            # Carregar layout
            layout = map_data.get("layout", [])
            map_height = len(layout)
            map_width = len(layout[0]) if layout else 0
            
            for y, row in enumerate(layout):
                if y >= GRID_HEIGHT:
                    break
                for x, cell in enumerate(row):
                    if x >= GRID_WIDTH:
                        break
                    self.grid[y][x] = cell
            
            # Carregar spawn positions
            spawns = map_data.get("spawn_positions", {})
            spawn_map = {
                "player": PLAYER_SPAWN,
                "ghost_red": GHOST_RED,
                "ghost_pink": GHOST_PINK,
                "ghost_cyan": GHOST_CYAN,
                "ghost_orange": GHOST_ORANGE
            }
            
            for spawn_name, spawn_type in spawn_map.items():
                if spawn_name in spawns:
                    pos = spawns[spawn_name]
                    x, y = pos["x"], pos["y"]
                    if self.is_valid_cell(x, y):
                        self.grid[y][x] = spawn_type
            
            # Mensagem detalhada de sucesso
            info_msg = f"Mapa carregado com sucesso!\n\n"
            info_msg += f"Nome: {self.map_metadata['name']}\n"
            info_msg += f"Dificuldade: {self.map_metadata['difficulty']}\n"
            info_msg += f"Tamanho original: {map_width}x{map_height}\n"
            info_msg += f"Spawns encontrados: {len(spawns)}\n"
            info_msg += f"\nAgora você pode editar e salvar as alterações!"
            
            # Armazenar arquivo atual para controle de sobrescrita
            self.current_file = filename
            
            messagebox.showinfo("Mapa Carregado", info_msg)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar mapa:\n{str(e)}\n\nVerifique se o arquivo tem o formato correto.")
    
    def edit_metadata(self):
        """Edita os metadados do mapa"""
        try:
            name = simpledialog.askstring("Nome do Mapa", "Nome:", initialvalue=self.map_metadata["name"])
            if name:
                self.map_metadata["name"] = name
            
            difficulty = simpledialog.askinteger("Dificuldade", "Dificuldade (0-200):", 
                                               initialvalue=self.map_metadata["difficulty"], 
                                               minvalue=0, maxvalue=200)
            if difficulty is not None:
                self.map_metadata["difficulty"] = difficulty
            
            description = simpledialog.askstring("Descrição", "Descrição:", 
                                                initialvalue=self.map_metadata["description"])
            if description:
                self.map_metadata["description"] = description
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar metadados: {str(e)}")
    
    def clear_map(self):
        """Limpa todo o mapa"""
        if messagebox.askyesno("Confirmar", "Limpar todo o mapa?"):
            self.grid = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    def new_map(self):
        """Cria um novo mapa (limpa tudo e reseta metadados)"""
        if messagebox.askyesno("Novo Mapa", "Criar um novo mapa? Isso vai limpar tudo."):
            self.grid = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
            self.map_metadata = {
                "name": "Novo Mapa",
                "difficulty": 50,
                "description": "Mapa criado no editor"
            }
            self.current_file = None  # Resetar arquivo atual
            messagebox.showinfo("Sucesso", "Novo mapa criado! Use 'M' para editar metadados.")
    
    def auto_fill_pellets(self):
        """Preenche automaticamente espaços vazios com pellets"""
        count = 0
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] == EMPTY:
                    self.grid[y][x] = PELLET
                    count += 1
        
        if count > 0:
            messagebox.showinfo("Sucesso", f"{count} pellets adicionados automaticamente!")
        else:
            messagebox.showinfo("Info", "Nenhum espaço vazio encontrado para colocar pellets.")
    
    def generate_borders(self):
        """Gera bordas automáticas ao redor do mapa"""
        count = 0
        
        # Bordas horizontais (primeira e última linha)
        for x in range(GRID_WIDTH):
            if self.grid[0][x] != WALL:
                self.grid[0][x] = WALL
                count += 1
            if self.grid[GRID_HEIGHT-1][x] != WALL:
                self.grid[GRID_HEIGHT-1][x] = WALL
                count += 1
        
        # Bordas verticais (primeira e última coluna)
        for y in range(GRID_HEIGHT):
            if self.grid[y][0] != WALL:
                self.grid[y][0] = WALL
                count += 1
            if self.grid[y][GRID_WIDTH-1] != WALL:
                self.grid[y][GRID_WIDTH-1] = WALL
                count += 1
        
        messagebox.showinfo("Sucesso", f"Bordas geradas! {count} paredes adicionadas.")
    
    def fill_connected_pellets(self, start_x, start_y):
        """Preenche com pellets todas as células conectadas a partir de (start_x, start_y)"""
        visited = set()
        stack = [(start_x, start_y)]
        while stack:
            x, y = stack.pop()
            if not self.is_valid_cell(x, y):
                continue
            if (x, y) in visited:
                continue
            if self.grid[y][x] != EMPTY:
                continue
            self.grid[y][x] = PELLET
            visited.add((x, y))
            # Adiciona vizinhos (4 direções)
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x + dx, y + dy
                if self.is_valid_cell(nx, ny) and (nx, ny) not in visited:
                    if self.grid[ny][nx] == EMPTY:
                        stack.append((nx, ny))
    
    def run(self):
        """Loop principal do editor"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    # Selecionar tipo de célula (0-9)
                    if pygame.K_0 <= event.key <= pygame.K_9:
                        type_index = event.key - pygame.K_0
                        if type_index < len(CELL_NAMES):
                            self.selected_type = list(CELL_NAMES.keys())[type_index]
                    
                    # Atalhos
                    elif event.key == pygame.K_s:
                        self.save_map()
                    elif event.key == pygame.K_l:
                        self.load_map()
                    elif event.key == pygame.K_m:
                        self.edit_metadata()
                    elif event.key == pygame.K_c:
                        self.clear_map()
                    elif event.key == pygame.K_n:
                        self.new_map()
                    elif event.key == pygame.K_p:
                        self.auto_fill_pellets()
                    elif event.key == pygame.K_b:
                        self.generate_borders()
                    elif event.key == pygame.K_MINUS:
                        self.selected_type = FILL_CONNECTED
                        print("Tipo 'Preencher conectados' selecionado. Clique em uma célula vazia para preencher.")
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_down = True
                    self.handle_click(event.pos, event.button)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_down = False
                
                elif event.type == pygame.MOUSEMOTION and self.mouse_down:
                    # Permitir arrastar para pintar
                    self.handle_click(event.pos, 1)
                
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    window_width, window_height = self.screen.get_size()
                    scale_x = (window_width - 200) / (GRID_WIDTH * CELL_SIZE)
                    scale_y = (window_height - 100) / (GRID_HEIGHT * CELL_SIZE)
                    self.scale = max(0.5, min(scale_x, scale_y, 2.0))
                    self.update_fonts()
            
            # Desenhar tudo
            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_ui()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

def main():
    # Criar diretório de mapas se não existir
    os.makedirs("assets/maps", exist_ok=True)
    
    editor = MapEditor()
    print("=== Editor de Mapas Pac-Man ===")
    print("Controles:")
    print("- Use as teclas 0-9 para selecionar o tipo de célula")
    print("- Click esquerdo: Colocar elemento")
    print("- Click direito: Remover elemento")
    print("- Arrastar: Pintar múltiplas células")
    print("- N: Novo mapa")
    print("- S: Salvar mapa")
    print("- L: Carregar/Editar mapa existente")
    print("- M: Editar metadados")
    print("- C: Limpar tudo")
    print("- P: Auto-preencher pellets")
    print("- B: Gerar bordas")
    print()
    print("Tipos:")
    for i, name in enumerate(CELL_NAMES.values()):
        print(f"{i}: {name}")
    
    editor.run()

if __name__ == "__main__":
    main()