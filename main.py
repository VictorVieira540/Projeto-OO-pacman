import pygame
from src.game_objects import Player, Ghost, Pellet
from src.map import Map
from src.utils import Vector2D, Direction, GameState # Importar Vector2D, Direction e GameState

class Game:
    def __init__(self, width, height):
        pygame.init()
        self._width = width
        self._height = height
        self._screen = pygame.display.set_mode((self._width, self._height))
        pygame.display.set_caption("Pac-Man OO")
        self._clock = pygame.time.Clock()
        self._state = GameState.MENU  # Usar GameState enum

        # Inicialização de objetos do jogo (exemplo)
        self._map = Map(layout_data=[], cell_size=20) # Layout será carregado depois
        self._map.load_map("mapa_exemplo.txt")

        self._player = Player(x=50, y=50, color=(255, 255, 0), size=15, speed=5, lives=3)
        self._ghosts = [
            Ghost(x=150, y=150, color=(255, 0, 0), size=15, speed=4, initial_position=Vector2D(150, 150)),
            Ghost(x=200, y=200, color=(0, 255, 255), size=15, speed=4, initial_position=Vector2D(200, 200))
        ]
        self._pellets = [
            Pellet(x=70, y=70, color=(255, 255, 255), size=5),
            Pellet(x=100, y=100, color=(255, 255, 255), size=5, pellet_type="power_up", value=50)
        ]

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._state = GameState.GAME_OVER # Ou um estado de saída
            elif event.type == pygame.KEYDOWN:
                if self._state == GameState.PLAYING:
                    if event.key == pygame.K_UP: self._player.direction = Direction.UP
                    elif event.key == pygame.K_DOWN: self._player.direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT: self._player.direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT: self._player.direction = Direction.RIGHT
                elif self._state == GameState.MENU:
                    if event.key == pygame.K_RETURN: self._state = GameState.PLAYING
                elif self._state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN: self._state = GameState.MENU # Reiniciar ou voltar ao menu

    def update(self, delta_time):
        if self._state == GameState.PLAYING:
            self._player.update(delta_time)
            for ghost in self._ghosts:
                ghost.update(delta_time, self._player.position)

            # Lógica de colisão com pellets
            pellets_to_remove = []
            for pellet in self._pellets:
                # Usar Vector2D para cálculo de distância
                distance = (self._player.position - pellet.position).magnitude()
                if distance < (self._player.size + pellet.size) / 2:
                    self._player.eat_pellet(pellet.be_eaten())
                    pellets_to_remove.append(pellet)
            for pellet in pellets_to_remove:
                self._pellets.remove(pellet)

            # Lógica de colisão com fantasmas
            for ghost in self._ghosts:
                # Usar Vector2D para cálculo de distância
                distance = (self._player.position - ghost.position).magnitude()
                if distance < (self._player.size + ghost.size) / 2:
                    if ghost.state == "normal":
                        self._player.lose_life()
                        self._player.position = Vector2D(50, 50) # Resetar posição do player
                        for g in self._ghosts: g.reset_position()
                        if self._player.lives == 0:
                            self._state = GameState.GAME_OVER
                    elif ghost.state == "vulnerable":
                        print("Fantasma comido!")
                        ghost.reset_position()
                        self._player.eat_pellet(200) # Pontuação por comer fantasma

            # Verificar se todos os pellets foram comidos
            if not self._pellets:
                print("Todos os pellets foram comidos! Você venceu!")
                self._state = GameState.GAME_OVER # Ou ir para o próximo nível

    def render(self):
        self._screen.fill((0, 0, 0))  # Preenche a tela de preto

        if self._state == GameState.MENU:
            font = pygame.font.Font(None, 74)
            text = font.render("PAC-MAN OO", True, (255, 255, 0))
            text_rect = text.get_rect(center=(self._width // 2, self._height // 2 - 50))
            self._screen.blit(text, text_rect)

            font = pygame.font.Font(None, 36)
            text = font.render("Pressione ENTER para jogar", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self._width // 2, self._height // 2 + 50))
            self._screen.blit(text, text_rect)

        elif self._state == GameState.PLAYING:
            self._map.draw(self._screen)
            self._player.draw(self._screen)
            for ghost in self._ghosts:
                ghost.draw(self._screen)
            for pellet in self._pellets:
                pellet.draw(self._screen)

            # Exibir pontuação e vidas
            font = pygame.font.Font(None, 24)
            score_text = font.render(f"Pontuação: {self._player.score}", True, (255, 255, 255))
            lives_text = font.render(f"Vidas: {self._player.lives}", True, (255, 255, 255))
            self._screen.blit(score_text, (10, 10))
            self._screen.blit(lives_text, (self._width - lives_text.get_width() - 10, 10))

        elif self._state == GameState.GAME_OVER:
            font = pygame.font.Font(None, 74)
            text = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text.get_rect(center=(self._width // 2, self._height // 2 - 50))
            self._screen.blit(text, text_rect)

            font = pygame.font.Font(None, 36)
            text = font.render(f"Pontuação Final: {self._player.score}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self._width // 2, self._height // 2 + 10))
            self._screen.blit(text, text_rect)

            font = pygame.font.Font(None, 36)
            text = font.render("Pressione ENTER para voltar ao Menu", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self._width // 2, self._height // 2 + 70))
            self._screen.blit(text, text_rect)

        pygame.display.flip()

    def run(self):
        while self._state != GameState.GAME_OVER: # Mudar para um estado de saída mais claro
            delta_time = self._clock.tick(60) / 1000.0  # Tempo em segundos
            self.process_events()
            self.update(delta_time)
            self.render()

        pygame.quit()

if __name__ == "__main__":
    game = Game(width=600, height=400)
    game.run()


