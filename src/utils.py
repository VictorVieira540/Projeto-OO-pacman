from enum import Enum
import math

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)

class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    PAUSED = 3
    VICTORY = 4

class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        """Adiciona dois vetores ou um vetor e um tuple"""
        if isinstance(other, Vector2D):
            return Vector2D(self.x + other.x, self.y + other.y)
        elif isinstance(other, tuple) and len(other) == 2:
            return Vector2D(self.x + other[0], self.y + other[1])
        raise TypeError("Operando inválido para adição")

    def __sub__(self, other):
        """Subtrai dois vetores ou um vetor e um tuple"""
        if isinstance(other, Vector2D):
            return Vector2D(self.x - other.x, self.y - other.y)
        elif isinstance(other, tuple) and len(other) == 2:
            return Vector2D(self.x - other[0], self.y - other[1])
        raise TypeError("Operando inválido para subtração")

    def __mul__(self, scalar):
        """Multiplica um vetor por um escalar"""
        return Vector2D(self.x * scalar, self.y * scalar)

    def __eq__(self, other):
        """Verifica se dois vetores são iguais"""
        if isinstance(other, Vector2D):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, tuple) and len(other) == 2:
            return self.x == other[0] and self.y == other[1]
        return False

    def __str__(self):
        """Retorna uma string representando o vetor"""
        return f"({self.x}, {self.y})"

    def magnitude(self):
        """Calcula a magnitude (distância) do vetor"""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalize(self):
        """Retorna um vetor unitário na mesma direção"""
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

    def distance_to(self, other):
        """Calcula a distância até outro vetor"""
        return (self - other).magnitude()

    def to_tuple(self):
        """Converte o vetor para um tuple"""
        return (self.x, self.y)

    def copy(self):
        """Retorna uma cópia do vetor"""
        return Vector2D(self.x, self.y) 