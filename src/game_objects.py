from abc import ABC, abstractmethod
from .utils import Vector2D, Direction # Importar Vector2D e Direction

class GameObject(ABC):
    def __init__(self, x, y, color, size):
        self._position = Vector2D(x, y)  # Usar Vector2D para posição
        self._color = color
        self._size = size

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

class MovableObject(GameObject):
    def __init__(self, x, y, color, size, speed, direction=Direction.NONE):
        super().__init__(x, y, color, size)
        self._speed = speed
        self._direction = direction  # Usar Direction enum

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
            self._direction = new_direction
        elif isinstance(new_direction, tuple) and len(new_direction) == 2:
            # Tentar converter tupla para Direction se for um dos valores conhecidos
            for d in Direction:
                if d.value == new_direction:
                    self._direction = d
                    return
            raise ValueError(f"Tupla de direção inválida: {new_direction}")
        else:
            raise TypeError("A direção deve ser um enum Direction ou uma tupla (x, y)")

    def move(self):
        # Usar sobrecarga de operador para adicionar a direção à posição
        self._position += Vector2D(self._direction.value[0] * self._speed, self._direction.value[1] * self._speed)

class Player(MovableObject):
    def __init__(self, x, y, color, size, speed, lives, score=0):
        super().__init__(x, y, color, size, speed)
        self._lives = lives
        self._score = score
        self._power_up_active = False

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

    def eat_pellet(self, pellet_value):
        self._score += pellet_value

    def lose_life(self):
        self._lives -= 1
        if self._lives < 0:
            self._lives = 0

    def draw(self, screen):
        print(f"Desenhando Player em {self._position} com cor {self._color}")

    def update(self, delta_time):
        self.move()

class Ghost(MovableObject):
    def __init__(self, x, y, color, size, speed, initial_position):
        super().__init__(x, y, color, size, speed)
        self._state = "normal"
        self._initial_position = Vector2D(initial_position[0], initial_position[1]) # Usar Vector2D

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state

    def move_ai(self, player_position):
        current_x, current_y = self._position.x, self._position.y
        player_x, player_y = player_position.x, player_position.y # player_position agora é Vector2D

        if self._state == "normal":
            if player_x > current_x: self.direction = Direction.RIGHT
            elif player_x < current_x: self.direction = Direction.LEFT
            elif player_y > current_y: self.direction = Direction.DOWN
            elif player_y < current_y: self.direction = Direction.UP
        elif self._state == "vulnerable":
            pass

        self.move()

    def reset_position(self):
        self._position = self._initial_position
        self._state = "normal"

    def draw(self, screen):
        print(f"Desenhando Ghost em {self._position} com cor {self._color} e estado {self._state}")

    def update(self, delta_time, player_position=None):
        if player_position:
            self.move_ai(player_position)
        else:
            self.move()

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
        print(f"Pellet de tipo {self._type} em {self._position} foi comido. Valor: {self._value}")
        return self._value

    def draw(self, screen):
        print(f"Desenhando Pellet em {self._position} com cor {self._color} e tipo {self._type}")

    def update(self, delta_time):
        pass


