import pygame
import os
from .utils import Direction

class SpriteManager:
    """Gerenciador de sprites para o jogo Pac-Man"""
    
    def __init__(self):
        self._sprites = {}
        self._sprite_size = 16
        self._load_all_sprites()
    
    def _load_sprite(self, path):
        """Carrega um sprite individual"""
        try:
            if not os.path.exists(path):
                print(f"Aviso: Sprite não encontrado em {path}")
                return self._create_default_sprite()
                
            sprite = pygame.image.load(path)
            # Redimensiona para o tamanho correto se necessário
            if sprite.get_size() != (self._sprite_size, self._sprite_size):
                sprite = pygame.transform.scale(sprite, (self._sprite_size, self._sprite_size))
            return sprite
        except (pygame.error, FileNotFoundError) as e:
            print(f"Erro ao carregar sprite {path}: {e}")
            return self._create_default_sprite()
    
    def _create_default_sprite(self):
        """Cria um sprite padrão quando o original não é encontrado"""
        sprite = pygame.Surface((self._sprite_size, self._sprite_size))
        sprite.fill((255, 0, 255))  # Magenta para indicar sprite faltando
        return sprite
    
    def _load_all_sprites(self):
        """Carrega todos os sprites do jogo"""
        # Usa a pasta organized que tem todos os sprites
        assets_path = "assets/sprites"
        
        # Sprites do Pac-Man
        pacman_path = f"{assets_path}/pacman"
        self._sprites['pacman'] = {
            'closed': self._load_sprite(f"{pacman_path}/pac-fechado.png"),
            'right': self._load_sprite(f"{pacman_path}/pac-dir.png"),
            'right_open': self._load_sprite(f"{pacman_path}/pac-dir-ab.png"),
            'left': self._load_sprite(f"{pacman_path}/pac-esq.png"),
            'left_open': self._load_sprite(f"{pacman_path}/pac-esq-ab.png"),
            'up': self._load_sprite(f"{pacman_path}/pac-cima.png"),
            'up_open': self._load_sprite(f"{pacman_path}/pac-cima-ab.png"),
            'down': self._load_sprite(f"{pacman_path}/pac-baixo.png"),
            'down_closed': self._load_sprite(f"{pacman_path}/pac-baixo-fechado.png")
        }
        
        # Sprites dos fantasmas
        ghost_colors = ['red', 'pink', 'blue', 'yellow']
        
        for color in ghost_colors:
            ghost_path = f"{assets_path}/ghosts/{color}"
            self._sprites[f'ghost_{color}'] = {}
            
            # Carrega todos os sprites de direção para cada fantasma
            for direction in ['up', 'down', 'left', 'right']:
                for frame in ['1', '2']:
                    direction_map = {
                        'up': 'cima',
                        'down': 'baixo', 
                        'left': 'esq',
                        'right': 'dir'
                    }
                    
                    sprite_file = f"{ghost_path}/{color}-{direction_map[direction]}-{frame}.png"
                    self._sprites[f'ghost_{color}'][f'{direction}_{frame}'] = self._load_sprite(sprite_file)
        
        # Sprites de fantasmas vulneráveis
        vulnerable_path = f"{assets_path}/ghosts/vulnerable"
        self._sprites['ghost_vulnerable'] = {
            'blue_1': self._load_sprite(f"{vulnerable_path}/vulnerable-blue-1.png"),
            'blue_2': self._load_sprite(f"{vulnerable_path}/vulnerable-blue-2.png"),
            'white_1': self._load_sprite(f"{vulnerable_path}/vunerable-white-1.png"),
            'white_2': self._load_sprite(f"{vulnerable_path}/vulnerable-white-2.png")
        }
        
        # Sprite de fruta para power-up
        self._sprites['fruit'] = self._load_sprite(f"{assets_path}/itens/fruit.png")
        
        # Sprites de pellets (criar proceduralmente)
        self._sprites['pellet'] = {
            'normal': self._create_pellet_sprite(2, (255, 255, 255)),
            'power_up': self._create_power_up_sprite()
        }
        
        print(f"Sprites carregados: Pac-Man={len(self._sprites['pacman'])}, Fantasmas={len(ghost_colors)}")
    
    def _create_pellet_sprite(self, radius, color):
        """Cria sprite de pellet proceduralmente"""
        sprite = pygame.Surface((self._sprite_size, self._sprite_size), pygame.SRCALPHA)
        center = self._sprite_size // 2
        pygame.draw.circle(sprite, color, (center, center), radius)
        return sprite
    
    def _create_power_up_sprite(self):
        """Cria sprite de power-up usando o sprite de fruta"""
        return self._sprites.get('fruit', self._create_default_sprite())
    
    def get_pacman_sprite(self, direction, animation_frame):
        """Retorna sprite do Pac-Man baseado na direção e frame de animação"""
        # Animação simples: alterna entre aberto e fechado
        is_open = (animation_frame // 10) % 2 == 0
        
        if direction == Direction.RIGHT:
            return self._sprites['pacman']['right_open'] if is_open else self._sprites['pacman']['right']
        elif direction == Direction.LEFT:
            return self._sprites['pacman']['left_open'] if is_open else self._sprites['pacman']['left']
        elif direction == Direction.UP:
            return self._sprites['pacman']['up_open'] if is_open else self._sprites['pacman']['up']
        elif direction == Direction.DOWN:
            return self._sprites['pacman']['down_closed'] if not is_open else self._sprites['pacman']['down']
        else:
            return self._sprites['pacman']['closed']
    
    def get_ghost_sprite(self, ghost_type, direction, animation_frame, state="normal"):
        """Retorna sprite do fantasma baseado no tipo, direção, frame e estado"""
        if state == "vulnerable":
            # Animação de vulnerabilidade alternando entre azul e branco
            timer = animation_frame // 15
            if timer % 4 < 2:
                return self._sprites['ghost_vulnerable']['blue_1'] if timer % 2 == 0 else self._sprites['ghost_vulnerable']['blue_2']
            else:
                return self._sprites['ghost_vulnerable']['white_1'] if timer % 2 == 0 else self._sprites['ghost_vulnerable']['white_2']
        
        # Mapear types para cores corretas
        color_map = {
            "red": "red",
            "pink": "pink", 
            "cyan": "blue",  # Cyan usa sprites azuis
            "orange": "yellow"  # Orange usa sprites amarelos
        }
        
        color = color_map.get(ghost_type, "red")
        ghost_sprites = self._sprites.get(f'ghost_{color}', self._sprites['ghost_red'])
        
        # Escolhe direção
        direction_map = {
            Direction.UP: 'up',
            Direction.DOWN: 'down',
            Direction.LEFT: 'left',
            Direction.RIGHT: 'right'
        }
        
        dir_name = direction_map.get(direction, 'up')
        
        # Animação alternando entre frame 1 e 2
        frame = '1' if (animation_frame // 20) % 2 == 0 else '2'
        
        sprite_key = f'{dir_name}_{frame}'
        return ghost_sprites.get(sprite_key, ghost_sprites.get('up_1', self._sprites['ghost_red']['up_1']))
    
    def get_pellet_sprite(self, pellet_type, animation_frame=0):
        """Retorna sprite do pellet"""
        if pellet_type == "power_up":
            # Power-up pisca
            if (animation_frame // 15) % 2 == 0:
                return self._sprites['pellet']['power_up']
            else:
                # Retorna sprite transparente para efeito de piscar
                transparent = pygame.Surface((self._sprite_size, self._sprite_size), pygame.SRCALPHA)
                return transparent
        else:
            return self._sprites['pellet']['normal']
    
    @property
    def sprite_size(self):
        """Retorna o tamanho dos sprites"""
        return self._sprite_size

# Instância global do gerenciador de sprites
sprite_manager = SpriteManager() 