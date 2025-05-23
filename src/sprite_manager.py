import pygame
import os

class SpriteManager:
    """
    Classe responsável por gerenciar os sprites do jogo.
    
    Esta classe carrega a spritesheet principal e fornece métodos para extrair
    sprites individuais baseados em coordenadas e dimensões específicas.
    """
    
    def __init__(self) -> None:
        self.sprites = {}
        self.load_sprites()
    
    def load_sprites(self) -> None:
        """Carrega todos os sprites do jogo"""
        # Carrega o spritesheet
        spritesheet = pygame.image.load("assets/sprites/spritesheet.png")
        
        # Pac-Man (3 frames por direção, 16x16 cada)
        self.sprites["pacman"] = {
            "right": [
                spritesheet.subsurface((0, 0, 16, 16)),   # boca fechada
                spritesheet.subsurface((16, 0, 16, 16)),  # meio aberta
                spritesheet.subsurface((32, 0, 16, 16)),  # aberta
            ],
            "up": [
                spritesheet.subsurface((0, 16, 16, 16)),
                spritesheet.subsurface((16, 16, 16, 16)),
                spritesheet.subsurface((32, 16, 16, 16)),
            ],
            "left": [
                spritesheet.subsurface((0, 32, 16, 16)),
                spritesheet.subsurface((16, 32, 16, 16)),
                spritesheet.subsurface((32, 32, 16, 16)),
            ],
            "down": [
                spritesheet.subsurface((0, 48, 16, 16)),
                spritesheet.subsurface((16, 48, 16, 16)),
                spritesheet.subsurface((32, 48, 16, 16)),
            ],
        }
        
        # Fantasmas (2 frames por cor, 16x16 cada)
        ghost_colors = ["red", "pink", "blue", "orange"]
        ghost_y = 64
        for i, color in enumerate(ghost_colors):
            right_frames = [spritesheet.subsurface((i*32, ghost_y, 16, 16)), spritesheet.subsurface((i*32+16, ghost_y, 16, 16))]
            left_frames = [spritesheet.subsurface((i*32, ghost_y+16, 16, 16)), spritesheet.subsurface((i*32+16, ghost_y+16, 16, 16))]
            self.sprites[f"ghost_{color}"] = {
                "right": right_frames,
                "left": left_frames,
                "up": right_frames,   # Usando os mesmos frames de 'right' para 'up'
                "down": left_frames   # Usando os mesmos frames de 'left' para 'down'
            }
        
        # Fantasma vulnerável (azul)
        self.sprites["ghost_vulnerable"] = [
            spritesheet.subsurface((0, 80, 16, 16)),
            spritesheet.subsurface((16, 80, 16, 16)),
        ]
        # Olhos dos fantasmas
        self.sprites["ghost_eyes"] = [
            spritesheet.subsurface((32, 80, 16, 16)),
            spritesheet.subsurface((48, 80, 16, 16)),
        ]
        
        # Frutas (exemplo: cereja)
        self.sprites["fruit"] = [spritesheet.subsurface((0, 96, 16, 16))]
        
        # Pellets
        self.sprites["food"] = {
            "normal": spritesheet.subsurface((0, 112, 8, 8)),
            "power": spritesheet.subsurface((8, 112, 8, 8)),
        }
    
    def get_sprite(self, entity: str, direction: str = None, frame: int = 0) -> pygame.Surface:
        """Retorna um sprite específico"""
        if entity == "food":
            return self.sprites[entity][direction]  # direction aqui é o tipo da comida (normal/power)
        elif direction:
            return self.sprites[entity][direction][frame]
        return self.sprites[entity]
    
    def scale_sprite(self, sprite: pygame.Surface, scale: float) -> pygame.Surface:
        """Redimensiona um sprite"""
        return pygame.transform.scale(sprite, (int(sprite.get_width() * scale), int(sprite.get_height() * scale)))
    
    def load_spritesheet(self):
        """Carrega a imagem da spritesheet principal."""
        spritesheet_path = os.path.join(self.game_directory, 'assets', 'sprites', 'spritesheet.png')
        try:
            self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
            print(f"Spritesheet carregada com sucesso: {spritesheet_path}")
        except pygame.error as e:
            print(f"Erro ao carregar spritesheet: {e}")
            self.spritesheet = None
    
    def load_sprite_set(self, name, coordinates):
        """
        Carrega um conjunto de sprites e armazena com um nome específico.
        
        Args:
            name (str): Nome do conjunto de sprites (ex: 'pacman_right', 'ghost_blue')
            coordinates (list): Lista de tuplas (x, y, width, height) para cada sprite
            
        Returns:
            list: Lista de sprites recortados
        """
        sprite_set = []
        for coord in coordinates:
            x, y, width, height = coord
            sprite = self.get_sprite(x, y, width, height)
            if sprite:
                sprite_set.append(sprite)
                
        # Armazena o conjunto para uso posterior
        self.sprites[name] = sprite_set
        return sprite_set
    
    def get_pacman_sprites(self):
        """
        Exemplo de método para carregar os sprites do Pac-Man.
        Você precisará ajustar as coordenadas com base na sua spritesheet específica.
        
        Returns:
            dict: Dicionário com os sprites do Pac-Man em diferentes direções
        """
        # Estas coordenadas são apenas exemplos - você precisa ajustá-las!
        # Formato: (x, y, largura, altura)
        
        # Pacman direita (3 frames: boca aberta, meio aberta, fechada)
        right = self.load_sprite_set('pacman_right', [
            (23, 23, 9, 13),    # Exemplo: boca aberta
            (3, 23, 12, 13),   # Exemplo: boca meio aberta
            (43, 3, 13, 13)    # Exemplo: boca fechada
        ])
        
        # Pacman esquerda
        left = self.load_sprite_set('pacman_left', [
            (27, 3, 9, 13),   # Exemplo: boca aberta 
            (4, 3, 12, 13),  # Exemplo: boca meio aberta
            (43, 3, 13, 13)   # Exemplo: boca fechada
        ])
        
        # Pacman cima
        up = self.load_sprite_set('pacman_up', [
           (23, 47, 13, 9),   # Exemplo: boca aberta
            (3, 44, 13, 12),  # Exemplo: boca meio aberta 
            (43, 3, 13, 13)   # Exemplo: boca fechada
        ])
        
        # Pacman baixo
        down = self.load_sprite_set('pacman_down', [
           (23, 62, 13, 9),   # Exemplo: boca aberta
            (3, 63, 13, 12),  # Exemplo: boca meio aberta
            (43, 3, 13, 13)   # Exemplo: boca fechada
        ])
        
        return {
            'right': right,
            'left': left,
            'up': up,
            'down': down
        }
    
    def get_ghost_sprites(self, color):
        """
        Exemplo de método para carregar os sprites dos fantasmas.
        
        Args:
            color (str): Cor do fantasma ('red', 'pink', 'blue', 'orange')
            
        Returns:
            dict: Dicionário com os sprites do fantasma
        """
        # Estas coordenadas são apenas exemplos - você precisa ajustá-las!
        # O ajuste depende da estrutura da sua spritesheet
        
        y_offset = 0
        if color == 'red':
            y_offset = 64
        elif color == 'pink':
            y_offset = 80
        elif color == 'blue':
            y_offset = 96
        elif color == 'orange':
            y_offset = 112
        
        # Fantasma direita (2 frames de animação)
        right = self.load_sprite_set(f'ghost_{color}_right', [
            (0, y_offset, 16, 16),
            (16, y_offset, 16, 16)
        ])
        
        # Fantasma esquerda (2 frames)
        left = self.load_sprite_set(f'ghost_{color}_left', [
            (32, y_offset, 16, 16),
            (48, y_offset, 16, 16)
        ])
        
        # Fantasma para cima (2 frames)
        up = self.load_sprite_set(f'ghost_{color}_up', [
            (64, y_offset, 16, 16),
            (80, y_offset, 16, 16)
        ])
        
        # Fantasma para baixo (2 frames)
        down = self.load_sprite_set(f'ghost_{color}_down', [
            (96, y_offset, 16, 16),
            (112, y_offset, 16, 16)
        ])
        
        # Fantasma vulnerável (azul)
        vulnerable = self.load_sprite_set('ghost_vulnerable', [
            (0, 128, 16, 16),
            (16, 128, 16, 16)
        ])
        
        # Fantasma vulnerável piscando (branco e azul)
        flashing = self.load_sprite_set('ghost_flashing', [
            (32, 128, 16, 16),
            (48, 128, 16, 16)
        ])
        
        # Olhos (quando o fantasma está voltando para casa)
        eyes = {
            'right': self.get_sprite(0, 144, 16, 16),
            'left': self.get_sprite(16, 144, 16, 16),
            'up': self.get_sprite(32, 144, 16, 16),
            'down': self.get_sprite(48, 144, 16, 16)
        }
        
        return {
            'right': right,
            'left': left,
            'up': up,
            'down': down,
            'vulnerable': vulnerable,
            'flashing': flashing,
            'eyes': eyes
        }
    
    def get_fruit_sprites(self):
        """
        Carrega os sprites das frutas.
        
        Returns:
            dict: Dicionário com os sprites das frutas
        """
        # Estas coordenadas são apenas exemplos - você precisa ajustá-las!
        fruits = {
            'cherry': self.get_sprite(0, 160, 16, 16),
            'strawberry': self.get_sprite(16, 160, 16, 16),
            'orange': self.get_sprite(32, 160, 16, 16),
            'apple': self.get_sprite(48, 160, 16, 16),
            'melon': self.get_sprite(0, 176, 16, 16),
            'galaxian': self.get_sprite(16, 176, 16, 16),
            'bell': self.get_sprite(32, 176, 16, 16),
            'key': self.get_sprite(48, 176, 16, 16)
        }
        
        return fruits
    
    def get_pellet_sprites(self):
        """
        Carrega os sprites dos pellets (bolinhas normais e energizantes).
        
        Returns:
            dict: Dicionário com os sprites dos pellets
        """
        # Estas coordenadas são apenas exemplos - você precisa ajustá-las!
        pellets = {
            'small': self.get_sprite(0, 192, 8, 8),
            'power': self.get_sprite(8, 192, 8, 8)
        }
        
        return pellets