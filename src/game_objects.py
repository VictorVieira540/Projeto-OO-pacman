from abc import ABC, abstractmethod
import pygame
import math
import random
from .utils import Vector2D, Direction
from .sprite_manager import sprite_manager

class GameObject(ABC):
    def __init__(self, x, y, color, size):
        self._position = Vector2D(x, y)
        self._color = color
        self._size = size
        self._animation_frame = 0

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_position):
        if isinstance(new_position, tuple):
            self._position = Vector2D(new_position[0], new_position[1])
        elif isinstance(new_position, Vector2D):
            self._position = new_position
        else:
            raise TypeError("A posição deve ser uma tupla ou um Vector2D")

    @property
    def color(self):
        return self._color

    @property
    def size(self):
        return self._size

    @abstractmethod
    def draw(self, screen):
        pass

    @abstractmethod
    def update(self, delta_time):
        pass

    def get_rect(self):
        """Retorna um retângulo para detecção de colisão"""
        sprite_size = sprite_manager.sprite_size
        return pygame.Rect(
            self._position.x - sprite_size // 2,
            self._position.y - sprite_size // 2,
            sprite_size,
            sprite_size
        )

class MovableObject(GameObject):
    def __init__(self, x, y, color, size, speed, direction=Direction.NONE):
        super().__init__(x, y, color, size)
        self._speed = speed
        self._direction = direction
        self._next_direction = direction  # Direção que o jogador quer ir

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, new_speed):
        self._speed = new_speed

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, new_direction):
        if isinstance(new_direction, Direction):
            self._next_direction = new_direction
        elif isinstance(new_direction, tuple) and len(new_direction) == 2:
            for d in Direction:
                if d.value == new_direction:
                    self._next_direction = d
                    return
            raise ValueError(f"Tupla de direção inválida: {new_direction}")
        else:
            raise TypeError("A direção deve ser um enum Direction ou uma tupla (x, y)")

    def can_move(self, direction, game_map):
        """Verifica se pode se mover na direção especificada"""
        if direction == Direction.NONE:
            return False
        
        # Calcula a próxima posição
        next_pos = Vector2D(
            self._position.x + direction.value[0] * self._speed,
            self._position.y + direction.value[1] * self._speed
        )
        
        # Verifica colisão com paredes usando o tamanho do sprite
        return game_map.is_valid_position(next_pos, sprite_manager.sprite_size)

    def move(self, direction=None):
        """Move o objeto na direção especificada"""
        if direction is None:
            direction = self._direction
        
        if direction != Direction.NONE:
            self._position += Vector2D(
                direction.value[0] * self._speed,
                direction.value[1] * self._speed
            )

class Player(MovableObject):
    def __init__(self, x, y, color, size, speed, lives, score=0):
        super().__init__(x, y, color, size, speed)
        self._lives = lives
        self._score = score
        self._power_up_active = False
        self._power_up_timer = 0
        self._power_up_duration = 5000  # 5 segundos em millisegundos

    @property
    def lives(self):
        return self._lives

    @property
    def score(self):
        return self._score

    @property
    def power_up_active(self):
        return self._power_up_active

    @power_up_active.setter
    def power_up_active(self, status):
        self._power_up_active = status
        if status:
            self._power_up_timer = self._power_up_duration

    def eat_pellet(self, pellet_value):
        self._score += pellet_value

    def activate_power_up(self):
        """Ativa o power-up do jogador"""
        self._power_up_active = True
        self._power_up_timer = self._power_up_duration

    def lose_life(self):
        self._lives -= 1
        if self._lives < 0:
            self._lives = 0

    def draw(self, screen):
        # Usa sprites reais do Pac-Man
        sprite = sprite_manager.get_pacman_sprite(self._direction, self._animation_frame)
        
        # Calcula posição para centralizar o sprite
        sprite_size = sprite_manager.sprite_size
        x = int(self._position.x - sprite_size // 2)
        y = int(self._position.y - sprite_size // 2)
        
        # Efeito visual quando power-up está ativo
        if self._power_up_active:
            # Adiciona um brilho amarelo ao redor
            glow_surface = pygame.Surface((sprite_size + 4, sprite_size + 4), pygame.SRCALPHA)
            glow_color = (255, 255, 100, 100) if (self._animation_frame // 5) % 2 else (255, 255, 0, 150)
            pygame.draw.circle(glow_surface, glow_color, (sprite_size//2 + 2, sprite_size//2 + 2), sprite_size//2 + 2)
            screen.blit(glow_surface, (x - 2, y - 2))
        
        screen.blit(sprite, (x, y))

    def update(self, delta_time, game_map):
        # Atualiza timer do power-up
        if self._power_up_active:
            self._power_up_timer -= delta_time * 1000  # Converter para millisegundos
            if self._power_up_timer <= 0:
                self._power_up_active = False
                self._power_up_timer = 0

        # Tenta mudar de direção se uma nova direção foi solicitada
        if self._next_direction != self._direction:
            if self.can_move(self._next_direction, game_map):
                self._direction = self._next_direction
            else:
                # Se não pode mudar para a nova direção, tenta continuar na direção atual
                if not self.can_move(self._direction, game_map):
                    self._direction = Direction.NONE

        # Move na direção atual se possível
        if self.can_move(self._direction, game_map):
            self.move()
        else:
            # Se não pode mover, tenta a próxima direção solicitada
            if self._next_direction != self._direction and self.can_move(self._next_direction, game_map):
                self._direction = self._next_direction
                self.move()
            else:
                self._direction = Direction.NONE

        self._animation_frame += 1

class Ghost(MovableObject):
    def __init__(self, x, y, color, size, speed, initial_position, ghost_type="red"):
        super().__init__(x, y, color, size, speed)
        self._state = "normal"  # normal, vulnerable, eaten
        self._initial_position = Vector2D(initial_position.x if isinstance(initial_position, Vector2D) else initial_position[0],
                                        initial_position.y if isinstance(initial_position, Vector2D) else initial_position[1])
        self._ghost_type = ghost_type
        self._vulnerable_timer = 0
        self._target_position = Vector2D(0, 0)
        self._mode_timer = 0
        # Modo atual do fantasma:
        # - scatter: fantasma foge para os cantos do mapa
        # - chase: fantasma persegue o jogador com comportamento específico
        self._current_mode = "scatter"
        self._path_finding_timer = 0
        self._original_color = color

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state

    def set_vulnerable(self, duration=10000):
        """Torna o fantasma vulnerável por um tempo determinado"""
        self._state = "vulnerable"
        self._vulnerable_timer = duration
        self._speed = max(1, self._speed - 1)  # Reduz velocidade quando vulnerável, mas mantém um mínimo de 1

    def get_target_position(self, player_position, other_ghosts=None):
        """Calcula a posição alvo baseada no tipo de fantasma e modo atual"""
        if self._current_mode == "scatter":
            # Modo scatter: vai para cantos específicos
            scatter_targets = {
                "red": Vector2D(500, 50),      # Canto superior direito
                "pink": Vector2D(50, 50),       # Canto superior esquerdo
                "cyan": Vector2D(500, 450),     # Canto inferior direito
                "orange": Vector2D(50, 450)     # Canto inferior esquerdo
            }
            return scatter_targets.get(self._ghost_type, self._initial_position)
        
        elif self._current_mode == "chase":
            # Modo chase: persegue o jogador com comportamentos diferentes
            if self._ghost_type == "red":
                # Fantasma vermelho: persegue diretamente
                return player_position.copy()
                
            elif self._ghost_type == "pink":
                # Fantasma rosa: mira 4 células à frente do jogador
                # TODO: Implementar lógica baseada na direção do jogador
                return player_position.copy()
                
            elif self._ghost_type == "cyan":
                # Fantasma ciano: comportamento mais complexo
                # Usa a posição do jogador e do fantasma vermelho
                if other_ghosts:
                    red_ghost = next((g for g in other_ghosts if g._ghost_type == "red"), None)
                    if red_ghost:
                        # Calcula ponto intermediário entre jogador e fantasma vermelho
                        mid_point = Vector2D(
                            (player_position.x + red_ghost.position.x) / 2,
                            (player_position.y + red_ghost.position.y) / 2
                        )
                        return mid_point
                return player_position.copy()
                
            else:  # orange
                # Fantasma laranja: alterna entre perseguir e fugir
                distance = self._position.distance_to(player_position)
                if distance > 100:  # Se estiver longe, persegue
                    return player_position.copy()
                else:  # Se estiver perto, foge para o canto
                    return Vector2D(50, 450)  # Canto inferior esquerdo

        return self._initial_position.copy()

    def choose_direction(self, game_map, target_position):
        """Escolhe a melhor direção para se mover em direção ao alvo"""
        possible_directions = []
        
        # Testa cada direção possível
        for direction in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
            if self.can_move(direction, game_map):
                # Calcula onde estaria se movesse nesta direção
                test_pos = Vector2D(
                    self._position.x + direction.value[0] * self._speed,
                    self._position.y + direction.value[1] * self._speed
                )
                distance = test_pos.distance_to(target_position)
                possible_directions.append((direction, distance))
        
        if not possible_directions:
            return Direction.NONE
        
        if self._state == "vulnerable":
            # Quando vulnerável, escolhe a direção que o afasta mais do alvo
            return max(possible_directions, key=lambda x: x[1])[0]
        else:
            # Escolhe a direção que o aproxima mais do alvo
            return min(possible_directions, key=lambda x: x[1])[0]

    def update_mode(self, delta_time):
        """Atualiza o modo do fantasma (scatter/chase)"""
        self._mode_timer += delta_time * 1000
        
        # Alterna entre modos a cada 10 segundos
        if self._mode_timer > 10000:
            self._current_mode = "chase" if self._current_mode == "scatter" else "scatter"
            self._mode_timer = 0

    def reset_position(self):
        self._position = self._initial_position.copy()
        self._state = "normal"
        self._speed = 1.5  # Velocidade padrão (ajustada para combinar com a inicialização)
        self._vulnerable_timer = 0

    def draw(self, screen):
        # Usa sprites reais dos fantasmas
        sprite = sprite_manager.get_ghost_sprite(
            self._ghost_type, 
            self._direction, 
            self._animation_frame, 
            self._state
        )
        
        # Calcula posição para centralizar o sprite
        sprite_size = sprite_manager.sprite_size
        x = int(self._position.x - sprite_size // 2)
        y = int(self._position.y - sprite_size // 2)
        
        screen.blit(sprite, (x, y))

    def update(self, delta_time, player_position=None, game_map=None, other_ghosts=None):
        # Atualiza timer de vulnerabilidade
        if self._state == "vulnerable":
            self._vulnerable_timer -= delta_time * 1000
            if self._vulnerable_timer <= 0:
                self._state = "normal"
                self._speed = 4  # Restaura velocidade normal

        # Atualiza modo
        self.update_mode(delta_time)

        if player_position and game_map:
            # Calcula posição alvo
            target = self.get_target_position(player_position, other_ghosts)
            
            # Escolhe direção a cada intervalo
            self._path_finding_timer += delta_time * 1000
            if self._path_finding_timer > 500:  # Muda direção a cada 500ms
                new_direction = self.choose_direction(game_map, target)
                if new_direction != Direction.NONE:
                    self._direction = new_direction
                self._path_finding_timer = 0

            # Move
            if self.can_move(self._direction, game_map):
                self.move()
            else:
                # Se não pode mover, escolhe nova direção imediatamente
                self._direction = self.choose_direction(game_map, target)

        self._animation_frame += 1

class Pellet(GameObject):
    def __init__(self, x, y, color, size, pellet_type="normal", value=10):
        super().__init__(x, y, color, size)
        self._type = pellet_type
        self._value = value

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value

    def be_eaten(self):
        return self._value

    def draw(self, screen):
        # Usa sprites reais dos pellets
        sprite = sprite_manager.get_pellet_sprite(self._type, self._animation_frame)
        
        # Calcula posição para centralizar o sprite
        sprite_size = sprite_manager.sprite_size
        x = int(self._position.x - sprite_size // 2)
        y = int(self._position.y - sprite_size // 2)
        
        screen.blit(sprite, (x, y))

    def update(self, delta_time):
        self._animation_frame += 1