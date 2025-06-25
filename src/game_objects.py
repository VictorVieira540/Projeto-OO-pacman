from abc import ABC, abstractmethod
import pygame
import math
import random
from .utils import Vector2D, Direction, AStar
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

    def can_move(self, direction, game_map, entity_type=None):
        """Verifica se pode se mover na direção especificada"""
        if direction == Direction.NONE:
            return False
        
        # Calcula a próxima posição
        next_pos = Vector2D(
            self._position.x + direction.value[0] * self._speed,
            self._position.y + direction.value[1] * self._speed
        )
        
        # Determina o tipo da entidade se não foi fornecido
        if entity_type is None:
            entity_type = "default"
        
        # Verifica colisão com paredes usando o tamanho do sprite e tipo específico
        return game_map.is_valid_position(next_pos, sprite_manager.sprite_size, entity_type)

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

    def can_move(self, direction, game_map, entity_type=None):
        """Sobrescreve para definir tipo como 'player'"""
        return super().can_move(direction, game_map, "player")

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
        # - patrol: fantasma patrulha rotas específicas no mapa
        # - chase: fantasma persegue o jogador com comportamento específico
        self._current_mode = "patrol"  # Começa em patrol
        self._path_finding_timer = 0
        self._original_color = color
        self._last_direction = Direction.NONE
        self._personality_timer = 0  # Timer para comportamentos específicos
        
        # Variáveis para A* pathfinding
        self._current_path = []  # Caminho atual calculado pelo A*
        self._path_index = 0     # Posição atual no caminho
        self._recalculate_path_timer = 0  # Timer para recalcular caminho
        self._use_astar = True   # Se deve usar A* ou sistema legado
        self._astar_frequency = 2000  # Recalcula caminho a cada 2 segundos (mais orgânico)
        self._last_target = None  # Último alvo calculado
        self._smooth_movement = True  # Ativa movimento suavizado
        
        # Variáveis para sistema de patrulhamento
        self._patrol_route = self._get_patrol_route()  # Rota de patrulha específica
        self._patrol_index = 0   # Índice atual na rota de patrulha
        self._patrol_timer = 0   # Timer para mudar waypoint de patrulha
        
        # Sistema de dificuldade progressiva
        self._base_speed = speed  # Velocidade original
        self._difficulty_multiplier = 1.0  # Multiplicador de dificuldade atual
        
        # Sistema de delay após ser comido
        self._is_in_spawn_delay = False  # Se está em delay no spawn
        self._spawn_delay_timer = 0      # Timer do delay (em ms)
        self._spawn_delay_duration = 5000  # 5 segundos de delay

    def can_move(self, direction, game_map, entity_type=None):
        """Sobrescreve para definir tipo como 'ghost'"""
        return super().can_move(direction, game_map, "ghost")

    def set_difficulty(self, difficulty_level):
        """
        Define a dificuldade do fantasma baseado no nível do mapa
        
        Args:
            difficulty_level: int - Nível de dificuldade do mapa (0-200)
        """
        # Converte nível de dificuldade (0-200) para fator (0.0-2.0)
        difficulty_factor = min(difficulty_level / 100.0, 2.0)
        
        # Calcula multiplicador de dificuldade baseado no nível do mapa
        # 0 = 1.0x, 100 = 2.0x, 200 = 3.0x - SISTEMA INTENSIFICADO!
        self._difficulty_multiplier = 1.0 + difficulty_factor
        
        # VELOCIDADE MANTIDA CONSTANTE - removido aumento de velocidade
        # A velocidade permanece igual durante todo o jogo
        self._speed = self._base_speed
        
        # Ajusta frequência A* para ser MUITO mais agressivo baseado na dificuldade do mapa
        timing_factor = 1.0 - (difficulty_factor * 0.4)  # Reduz até 80% dos timers
        self._astar_frequency = max(int(2000 * timing_factor), 200)  # Mínimo 200ms

    def update_difficulty(self, pellets_eaten_percentage):
        """
        MÉTODO LEGADO - Mantido para compatibilidade
        Agora não faz nada pois dificuldade é fixa baseada no mapa
        
        Args:
            pellets_eaten_percentage: float - Ignorado (compatibilidade)
        """
        # Não faz nada - dificuldade agora é fixa baseada no mapa
        pass

    def get_difficulty_adjusted_vulnerable_duration(self, base_duration=8000):
        """
        Retorna duração de vulnerabilidade ajustada pela dificuldade
        
        Args:
            base_duration: int - Duração base em ms
            
        Returns:
            int: Duração ajustada em ms
        """
        # Reduz duração de vulnerabilidade conforme dificuldade aumenta - MUITO MAIS INTENSO!
        reduction_factor = 1.0 - (self._difficulty_multiplier - 1.0) * 0.85  # Até 85% de redução (era 60%)
        adjusted_duration = int(base_duration * reduction_factor)
        return max(adjusted_duration, 1000)  # Mínimo 1 segundo (era 2 segundos)

    def get_difficulty_adjusted_mode_timing(self):
        """
        Retorna timings de modo ajustados pela dificuldade
        
        Returns:
            tuple: (patrol_duration_ms, chase_duration_ms)
        """
        # Com maior dificuldade, MUITO menos tempo em patrol, MUITO mais em chase
        base_patrol = 10000
        base_chase = 15000
        
        difficulty_factor = self._difficulty_multiplier - 1.0  # 0.0 a 2.0 (agora vai até 2.0!)
        
        # Reduz patrol e aumenta chase - MUITO MAIS AGRESSIVO!
        patrol_duration = int(base_patrol * (1.0 - difficulty_factor * 0.45))  # Até 90% menos patrol (era 40%)
        chase_duration = int(base_chase * (1.0 + difficulty_factor * 0.8))     # Até 160% mais chase (era 60%)
        
        # Limites mínimos e máximos - MAIS EXTREMOS!
        patrol_duration = max(patrol_duration, 2000)  # Mínimo 2s (era 5s)
        chase_duration = min(chase_duration, 40000)   # Máximo 40s (era 25s)
        
        return patrol_duration, chase_duration

    def _get_patrol_route(self):
        """
        Define rotas de patrulha mais orgânicas para cada tipo de fantasma
        
        Returns:
            List[Vector2D]: Lista de pontos que formam a rota de patrulha
        """
        # Rotas mais naturais e variadas para movimento orgânico
        
        if self._ghost_type == "red":
            # Fantasma vermelho: patrulha ampla e dominante
            return [
                Vector2D(280, 100),  # Centro superior
                Vector2D(420, 130),  # Direita superior diagonal
                Vector2D(480, 180),  # Direita lateral
                Vector2D(400, 220),  # Direita meio diagonal
                Vector2D(280, 200),  # Centro meio
                Vector2D(160, 220),  # Esquerda meio diagonal
                Vector2D(80, 180),   # Esquerda lateral
                Vector2D(140, 130),  # Esquerda superior diagonal
            ]
        elif self._ghost_type == "pink":
            # Fantasma rosa: movimento em S suave
            return [
                Vector2D(180, 140),  # Início S
                Vector2D(240, 120),  # Curva superior
                Vector2D(320, 140),  # Meio superior
                Vector2D(380, 180),  # Curva direita
                Vector2D(320, 220),  # Meio inferior
                Vector2D(240, 240),  # Curva inferior
                Vector2D(180, 220),  # Fim S
                Vector2D(140, 180),  # Volta início
            ]
        elif self._ghost_type == "cyan":
            # Fantasma ciano: patrulha tática em L
            return [
                Vector2D(300, 260),  # Base L
                Vector2D(450, 260),  # Horizontal direita
                Vector2D(480, 300),  # Canto L
                Vector2D(480, 340),  # Vertical baixo
                Vector2D(400, 350),  # Retorno horizontal
                Vector2D(280, 330),  # Centro baixo
                Vector2D(150, 320),  # Esquerda baixo
                Vector2D(120, 280),  # Subida esquerda
            ]
        else:  # orange
            # Fantasma laranja: movimento errático e imprevisível
            return [
                Vector2D(140, 160),  # Ponto 1
                Vector2D(220, 140),  # Subida diagonal
                Vector2D(300, 180),  # Centro direita
                Vector2D(380, 160),  # Direita
                Vector2D(420, 220),  # Descida direita
                Vector2D(340, 260),  # Centro baixo
                Vector2D(240, 240),  # Esquerda baixo
                Vector2D(160, 200),  # Subida esquerda
            ]

    def get_current_patrol_target(self):
        """
        Retorna o alvo atual da patrulha
        
        Returns:
            Vector2D: Posição alvo da patrulha
        """
        if not self._patrol_route:
            return self._initial_position.copy()
        
        return self._patrol_route[self._patrol_index % len(self._patrol_route)]

    def advance_patrol_waypoint(self):
        """
        Avança para o próximo waypoint da patrulha de forma mais orgânica
        
        Returns:
            bool: True se avançou para próximo waypoint
        """
        if not self._patrol_route:
            return False
        
        current_target = self.get_current_patrol_target()
        distance = self._position.distance_to(current_target)
        
        # Distância de tolerância variável por fantasma para movimento mais natural
        tolerance = {
            "red": 28,    # Vermelho: mais preciso
            "pink": 35,   # Rosa: mais solto
            "cyan": 30,   # Ciano: balanceado
            "orange": 40  # Laranja: mais errático
        }.get(self._ghost_type, 32)
        
        # Se chegou perto do waypoint atual, vai para o próximo
        if distance < tolerance:
            self._patrol_index = (self._patrol_index + 1) % len(self._patrol_route)
            return True
        
        return False

    def configure_astar(self, use_astar=True, frequency=1000):
        """
        Configura parâmetros do A* pathfinding
        
        Args:
            use_astar: bool - Se deve usar A*
            frequency: int - Frequência de recálculo em ms
        """
        self._use_astar = use_astar
        self._astar_frequency = frequency
        if not use_astar:
            # Limpa caminho se desabilitar A*
            self._current_path = []
            self._path_index = 0

    def get_astar_status(self):
        """
        Retorna informações sobre o status do A* pathfinding
        
        Returns:
            dict: Informações do A*
        """
        return {
            "enabled": self._use_astar,
            "path_length": len(self._current_path),
            "path_index": self._path_index,
            "frequency": self._astar_frequency,
            "ghost_type": self._ghost_type,
            "has_path": len(self._current_path) > 0,
            "difficulty_multiplier": self._difficulty_multiplier,
            "speed": self._speed  # Velocidade constante
        }

    def get_patrol_status(self):
        """
        Retorna informações sobre o status do patrulhamento
        
        Returns:
            dict: Informações da patrulha
        """
        return {
            "mode": self._current_mode,
            "route_length": len(self._patrol_route),
            "current_waypoint": self._patrol_index,
            "target_position": self.get_current_patrol_target(),
            "ghost_type": self._ghost_type,
            "distance_to_target": self._position.distance_to(self.get_current_patrol_target()) if self._patrol_route else 0
        }

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state

    @property
    def is_in_spawn_delay(self):
        """Retorna True se o fantasma está em delay no spawn"""
        return self._is_in_spawn_delay

    @property
    def spawn_delay_remaining(self):
        """Retorna o tempo restante do delay em segundos"""
        return max(0, self._spawn_delay_timer / 1000.0)

    def set_vulnerable(self, duration=8000):
        """Torna o fantasma vulnerável por um tempo determinado ajustado pela dificuldade"""
        self._state = "vulnerable"
        # Aplica duração ajustada pela dificuldade
        adjusted_duration = self.get_difficulty_adjusted_vulnerable_duration(duration)
        self._vulnerable_timer = adjusted_duration
        self._speed = max(1, self._speed - 1)  # Reduz velocidade quando vulnerável, mas mantém um mínimo de 1

    def get_target_position(self, player_position, player_direction=None, other_ghosts=None):
        """Calcula a posição alvo baseada no tipo de fantasma e modo atual"""
        if self._current_mode == "patrol":
            # Modo patrol: segue rota de patrulhamento específica
            return self.get_current_patrol_target()
        
        elif self._current_mode == "chase":
            # Modo chase: persegue o jogador com comportamentos diferentes
            if self._ghost_type == "red":
                # Fantasma vermelho: persegue diretamente (Blinky)
                return player_position.copy()
                
            elif self._ghost_type == "pink":
                # Fantasma rosa: mira 4 células à frente do jogador (Pinky)
                if player_direction:
                    # Calcula posição 4 células à frente do jogador
                    cell_size = 16  # Tamanho da célula
                    offset_x = player_direction.value[0] * cell_size * 4
                    offset_y = player_direction.value[1] * cell_size * 4
                    target = Vector2D(
                        player_position.x + offset_x,
                        player_position.y + offset_y
                    )
                    return target
                else:
                    return player_position.copy()
                
            elif self._ghost_type == "cyan":
                # Fantasma ciano: comportamento mais complexo (Inky)
                if other_ghosts:
                    red_ghost = next((g for g in other_ghosts if g._ghost_type == "red"), None)
                    if red_ghost:
                        # Calcula ponto intermediário entre jogador e fantasma vermelho
                        # Primeiro, calcula a posição 2 células à frente do jogador
                        if player_direction:
                            cell_size = 16
                            offset_x = player_direction.value[0] * cell_size * 2
                            offset_y = player_direction.value[1] * cell_size * 2
                            player_ahead = Vector2D(
                                player_position.x + offset_x,
                                player_position.y + offset_y
                            )
                        else:
                            player_ahead = player_position.copy()
                        
                        # Agora calcula o ponto médio entre player_ahead e red_ghost
                        mid_point = Vector2D(
                            (player_ahead.x + red_ghost.position.x) / 2,
                            (player_ahead.y + red_ghost.position.y) / 2
                        )
                        return mid_point
                return player_position.copy()
                
            else:  # orange (Clyde)
                # Fantasma laranja: alterna entre perseguir e fugir
                distance = self._position.distance_to(player_position)
                if distance > 80:  # Se estiver longe, persegue
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

    def choose_direction_advanced(self, game_map, target_position):
        """Escolhe direção com lógica mais avançada e orgânica"""
        possible_directions = []
        
        # Testa cada direção possível
        for direction in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
            if self.can_move(direction, game_map):
                # Calcula onde estaria se movesse nesta direção
                test_pos = Vector2D(
                    self._position.x + direction.value[0] * self._speed,
                    self._position.y + direction.value[1] * self._speed
                )
                # Usa distância Manhattan para consistência com A*
                distance = test_pos.manhattan_distance_to(target_position)
                possible_directions.append((direction, distance))
        
        if not possible_directions:
            return Direction.NONE
        
        # Adiciona preferência por continuar na direção atual (movimento mais suave)
        current_direction_bonus = 0
        if self._smooth_movement and self._direction != Direction.NONE:
            for i, (direction, distance) in enumerate(possible_directions):
                if direction == self._direction:
                    # Dá uma pequena vantagem para continuar na mesma direção
                    possible_directions[i] = (direction, distance * 0.9)
                    break
        
        if self._state == "vulnerable":
            # Quando vulnerável, foge do alvo
            return max(possible_directions, key=lambda x: x[1])[0]
        
        # Comportamentos específicos por tipo de fantasma mais orgânicos
        if self._ghost_type == "red":
            # Vermelho: geralmente direto, mas ocasionalmente impreciso
            if random.random() < 0.05:  # 5% de imprecisão
                return random.choice(possible_directions[:2])[0]  # Entre as 2 melhores
            return min(possible_directions, key=lambda x: x[1])[0]
            
        elif self._ghost_type == "pink":
            # Rosa: movimento mais imprevisível para emboscadas
            if random.random() < 0.2:  # 20% de aleatoriedade
                return random.choice(possible_directions)[0]
            # Às vezes escolhe segunda melhor opção
            elif random.random() < 0.3 and len(possible_directions) > 1:
                sorted_dirs = sorted(possible_directions, key=lambda x: x[1])
                return sorted_dirs[1][0]  # Segunda melhor
            else:
                return min(possible_directions, key=lambda x: x[1])[0]
                
        elif self._ghost_type == "cyan":
            # Ciano: evita reversões bruscas mas é tático
            if self._direction != Direction.NONE:
                opposite_direction = Direction((-self._direction.value[0], -self._direction.value[1]))
                filtered_directions = [d for d in possible_directions if d[0] != opposite_direction]
                if filtered_directions and random.random() < 0.8:  # 80% evita reverter
                    possible_directions = filtered_directions
            
            # Ocasionalmente escolhe rota mais longa para flanquear
            if random.random() < 0.15:  # 15% movimento tático
                return max(possible_directions[:3], key=lambda x: x[1])[0]  # Pior das 3 melhores
            return min(possible_directions, key=lambda x: x[1])[0]
            
        else:  # orange
            # Laranja: muito errático e orgânico
            rand = random.random()
            if rand < 0.25:  # 25% completamente aleatório
                return random.choice(possible_directions)[0]
            elif rand < 0.4:  # 15% escolhe pior direção
                return max(possible_directions, key=lambda x: x[1])[0]
            elif rand < 0.6 and len(possible_directions) > 2:  # 20% escolhe média
                sorted_dirs = sorted(possible_directions, key=lambda x: x[1])
                return sorted_dirs[len(sorted_dirs)//2][0]
            else:  # 40% escolhe melhor
                return min(possible_directions, key=lambda x: x[1])[0]

    def update_mode(self, delta_time):
        """Atualiza o modo do fantasma (patrol/chase) com timing ajustado pela dificuldade"""
        self._mode_timer += delta_time * 1000
        
        # Obtém timings ajustados pela dificuldade
        patrol_duration, chase_duration = self.get_difficulty_adjusted_mode_timing()
        
        if self._current_mode == "patrol":
            # Patrol com duração ajustada pela dificuldade
            if self._mode_timer > patrol_duration:
                self._current_mode = "chase"
                self._mode_timer = 0
        else:  # chase
            # Chase com duração ajustada pela dificuldade
            if self._mode_timer > chase_duration:
                self._current_mode = "patrol"
                self._mode_timer = 0

    def reset_position(self):
        """Reset normal da posição (usado quando o jogo reinicia)"""
        self._position = self._initial_position.copy()
        self._state = "normal"
        self._speed = self._base_speed  # Restaura velocidade original
        self._vulnerable_timer = 0
        self._current_mode = "patrol"  # Volta para patrol
        self._mode_timer = 0
        # Reset A* pathfinding
        self._current_path = []
        self._path_index = 0
        self._recalculate_path_timer = 0
        self._last_target = None
        # Reset patrol system
        self._patrol_index = 0
        self._patrol_timer = 0
        # Reset delay system
        self._is_in_spawn_delay = False
        self._spawn_delay_timer = 0

    def set_eaten_with_delay(self):
        """Coloca o fantasma no spawn com delay de 5 segundos após ser comido"""
        self._position = self._initial_position.copy()
        self._state = "normal"
        self._speed = self._base_speed  # Restaura velocidade original
        self._vulnerable_timer = 0
        self._current_mode = "patrol"  # Volta para patrol
        self._mode_timer = 0
        # Reset A* pathfinding
        self._current_path = []
        self._path_index = 0
        self._recalculate_path_timer = 0
        self._last_target = None
        # Reset patrol system
        self._patrol_index = 0
        self._patrol_timer = 0
        # Ativa delay de 5 segundos
        self._is_in_spawn_delay = True
        self._spawn_delay_timer = self._spawn_delay_duration
        
        print(f"Fantasma {self._ghost_type} comido! Aguardando 5s no spawn...")

    def reset_difficulty(self):
        """Reseta a dificuldade para o nível inicial"""
        self._difficulty_multiplier = 1.0
        self._speed = self._base_speed  # Velocidade sempre constante
        self._astar_frequency = 2000

    def calculate_direction_to_waypoint(self, waypoint):
        """
        Calcula a direção para se mover em direção ao próximo waypoint
        
        Args:
            waypoint: Vector2D do próximo ponto no caminho
            
        Returns:
            Direction: Direção para se mover
        """
        diff_x = waypoint.x - self._position.x
        diff_y = waypoint.y - self._position.y
        
        # Prioriza movimento no eixo com maior diferença
        if abs(diff_x) > abs(diff_y):
            if diff_x > 0:
                return Direction.RIGHT
            else:
                return Direction.LEFT
        else:
            if diff_y > 0:
                return Direction.DOWN
            else:
                return Direction.UP

    def should_use_astar(self, target_position):
        """
        Determina se deve usar A* baseado na personalidade, contexto e dificuldade
        
        Args:
            target_position: Vector2D do alvo
            
        Returns:
            bool: True se deve usar A*
        """
        # Calcula bonus de agressividade baseado na dificuldade - MUITO MAIS INTENSO!
        difficulty_bonus = (self._difficulty_multiplier - 1.0) * 0.6  # Até 120% mais agressivo (era 30%)
        
        # Personalidades com comportamento ajustado pela dificuldade - MUITO MAIS AGRESSIVAS!
        if self._ghost_type == "red":
            # Vermelho fica EXTREMAMENTE agressivo com dificuldade
            base_chance = 0.9
            return random.random() < min(base_chance + difficulty_bonus, 1.0)  # 100% agressividade máxima (era 98%)
        elif self._ghost_type == "pink":
            # Rosa fica MUITO mais calculista
            base_chance = 0.6
            return random.random() < min(base_chance + difficulty_bonus, 0.95)  # 95% máximo (era 85%)
        elif self._ghost_type == "cyan":
            # Ciano fica EXTREMAMENTE tático
            base_chance = 0.85
            return random.random() < min(base_chance + difficulty_bonus, 1.0)  # 100% máximo (era 95%)
        else:  # orange
            # Laranja fica MUITO menos errático e mais direto
            distance = self._position.distance_to(target_position)
            if distance > 150:
                base_chance = 0.8
                return random.random() < min(base_chance + difficulty_bonus, 1.0)  # 100% máximo (era 95%)
            elif distance > 80:
                base_chance = 0.5
                return random.random() < min(base_chance + difficulty_bonus, 0.95)  # 95% máximo (era 80%)
            else:
                base_chance = 0.2
                return random.random() < min(base_chance + difficulty_bonus, 0.8)  # 80% máximo (era 60%)

    def astar_pathfinding(self, game_map, target_position):
        """
        Usa A* para encontrar caminho até o alvo
        
        Args:
            game_map: Instância do mapa
            target_position: Vector2D do alvo
            
        Returns:
            Direction: Próxima direção a tomar
        """
        # Verifica se precisa recalcular o caminho
        should_recalculate = (
            len(self._current_path) == 0 or  # Sem caminho
            self._path_index >= len(self._current_path) - 1 or  # Chegou ao fim
            self._recalculate_path_timer > self._astar_frequency or  # Timeout
            (self._last_target and self._last_target.distance_to(target_position) > 32)  # Alvo mudou muito
        )
        
        if should_recalculate:
            # Calcula novo caminho usando A*
            self._current_path = AStar.find_path(
                self._position, 
                target_position, 
                game_map, 
                "manhattan"  # Melhor heurística para labirintos
            )
            self._path_index = 0
            self._recalculate_path_timer = 0
            self._last_target = target_position.copy()
            
            # Caminho calculado com sucesso
        
        # Se tem caminho válido, segue ele
        if self._current_path and self._path_index < len(self._current_path) - 1:
            next_waypoint = self._current_path[self._path_index + 1]
            
            # Se chegou perto do waypoint atual, avança para o próximo
            if self._position.distance_to(next_waypoint) < 12:
                self._path_index += 1
                if self._path_index < len(self._current_path) - 1:
                    next_waypoint = self._current_path[self._path_index + 1]
                else:
                    # Chegou ao fim do caminho
                    return Direction.NONE
            
            # Calcula direção para o próximo waypoint
            direction = self.calculate_direction_to_waypoint(next_waypoint)
            
            # Verifica se pode se mover nesta direção
            if self.can_move(direction, game_map):
                return direction
        
        # Fallback: usa sistema legado se A* falhar
        return self.choose_direction_advanced(game_map, target_position)

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

    def update(self, delta_time, player_position=None, player_direction=None, game_map=None, other_ghosts=None):
        # Atualiza timer de delay no spawn
        if self._is_in_spawn_delay:
            self._spawn_delay_timer -= delta_time * 1000
            if self._spawn_delay_timer <= 0:
                self._is_in_spawn_delay = False
                self._spawn_delay_timer = 0
                print(f"Fantasma {self._ghost_type} liberado do spawn!")
            else:
                # Durante o delay, não faz nada - permanece imóvel no spawn
                self._animation_frame += 1  # Só atualiza animação
                return

        # Atualiza timer de vulnerabilidade
        if self._state == "vulnerable":
            self._vulnerable_timer -= delta_time * 1000
            if self._vulnerable_timer <= 0:
                self._state = "normal"
                self._speed = 1.5  # Restaura velocidade normal

        # Atualiza modo
        self.update_mode(delta_time)

        if player_position and game_map:
            # Atualiza sistema de patrulhamento se estiver no modo patrol
            if self._current_mode == "patrol":
                self._patrol_timer += delta_time * 1000
                # Verifica se deve avançar para próximo waypoint da patrulha (mais frequente)
                if self._patrol_timer > 200:  # Verifica a cada 200ms para movimento mais fluido
                    self.advance_patrol_waypoint()
                    self._patrol_timer = 0
            
            # Calcula posição alvo
            target = self.get_target_position(player_position, player_direction, other_ghosts)
            
            # Atualiza timers
            self._path_finding_timer += delta_time * 1000
            self._recalculate_path_timer += delta_time * 1000
            
            # Decide se usa A* ou sistema legado
            use_astar = self._use_astar and self.should_use_astar(target)
            
            new_direction = Direction.NONE
            
            if use_astar:
                # Usa A* pathfinding com timing variável
                astar_interval = {
                    "red": 100,    # Vermelho: mais frequente (agressivo)
                    "pink": 100,   # Rosa: médio (emboscador)
                    "cyan": 100,   # Ciano: balanceado (tático)
                    "orange": 100  # Laranja: menos frequente (errático)
                }.get(self._ghost_type, 500)
                
                if self._recalculate_path_timer > astar_interval:
                    new_direction = self.astar_pathfinding(game_map, target)
                    if new_direction != Direction.NONE:
                        self._direction = new_direction
                        self._last_direction = new_direction
                    self._recalculate_path_timer = 0
            else:
                # Usa sistema legado com timing mais orgânico
                legacy_interval = {
                    "red": 250,    # Vermelho: rápido
                    "pink": 400,   # Rosa: médio
                    "cyan": 350,   # Ciano: médio-rápido
                    "orange": 500  # Laranja: mais lento
                }.get(self._ghost_type, 350)
                
                if self._path_finding_timer > legacy_interval:
                    new_direction = self.choose_direction_advanced(game_map, target)
                    if new_direction != Direction.NONE:
                        self._direction = new_direction
                        self._last_direction = new_direction
                    self._path_finding_timer = 0

            # Move
            if self.can_move(self._direction, game_map):
                self.move()
            else:
                # Se não pode mover, escolhe nova direção imediatamente
                if use_astar:
                    # Força recálculo do A*
                    self._current_path = []
                    self._direction = self.astar_pathfinding(game_map, target)
                else:
                    # Usa sistema legado
                    self._direction = self.choose_direction_advanced(game_map, target)
                
                if self._direction != Direction.NONE:
                    self._last_direction = self._direction

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