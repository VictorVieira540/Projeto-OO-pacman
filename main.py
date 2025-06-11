import pygame
import sys
from src.game_objects import Player, Ghost, Pellet
from src.map import Map
from src.utils import Vector2D, Direction, GameState
from src.sprite_manager import sprite_manager

class Game:
    def __init__(self, width=560, height=336):  # 35x21 células de 16px cada = 560x336
        pygame.init()
        self._width = width
        self._height = height
        self._screen = pygame.display.set_mode((self._width, self._height))
        pygame.display.set_caption("Pac-Man OO - Projeto Orientado a Objetos com Sprites")
        self._clock = pygame.time.Clock()
        self._state = GameState.MENU
        self._font_large = pygame.font.Font(None, 48)
        self._font_medium = pygame.font.Font(None, 32)
        self._font_small = pygame.font.Font(None, 24)
        
        # Sons (TODO: Adicionar sons quando disponíveis)
        # self._sound_eat = pygame.mixer.Sound("assets/sounds/eat.wav")
        # self._sound_power_up = pygame.mixer.Sound("assets/sounds/power_up.wav")
        
        self._initialize_game()

    def _initialize_game(self):
        """Inicializa os objetos do jogo"""
        # Mapa - agora usa automaticamente o tamanho dos sprites
        self._map = Map()
        self._map.load_default_map()
        
        # Jogador
        player_pos = self._map.get_spawn_position("player")
        self._player = Player(
            x=player_pos.x, 
            y=player_pos.y, 
            color=(255, 255, 0), 
            size=sprite_manager.sprite_size,  # Usa tamanho do sprite
            speed=2,  # Aumentado de 2 para 4
            lives=3
        )
        
        # Fantasmas
        self._ghosts = []
        ghost_configs = [
            {"type": "red", "color": (255, 0, 0)},
            {"type": "pink", "color": (255, 182, 193)},
            {"type": "cyan", "color": (0, 255, 255)},
            {"type": "orange", "color": (255, 165, 0)}
        ]
        
        for config in ghost_configs:
            ghost_pos = self._map.get_spawn_position(f"ghost_{config['type']}")
            ghost = Ghost(
                x=ghost_pos.x,
                y=ghost_pos.y,
                color=config["color"],
                size=sprite_manager.sprite_size,  # Usa tamanho do sprite
                speed=1.5,  # Velocidade reduzida para 1.5 (era 2)
                initial_position=ghost_pos,
                ghost_type=config["type"]
            )
            self._ghosts.append(ghost)
        
        # Pellets
        self._pellets = []
        pellet_data = self._map.get_pellets()
        for pellet_info in pellet_data:
            pellet = Pellet(
                x=pellet_info["position"].x,
                y=pellet_info["position"].y,
                color=(255, 255, 255),
                size=sprite_manager.sprite_size,  # Usa tamanho do sprite
                pellet_type=pellet_info["type"],
                value=pellet_info["value"]
            )
            self._pellets.append(pellet)
        
        self._total_pellets = len(self._pellets)
        self._game_start_time = pygame.time.get_ticks()

    def _reset_game(self):
        """Reinicia o jogo"""
        self._initialize_game()
        self._state = GameState.PLAYING

    def _reset_positions(self):
        """Reinicia posições após morte"""
        player_pos = self._map.get_spawn_position("player")
        self._player.position = player_pos
        
        for ghost in self._ghosts:
            ghost.reset_position()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state

    def process_events(self):
        """Processa eventos do jogador"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if self._state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        self._state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        return False
                        
                elif self._state == GameState.PLAYING:
                    # Controles do jogador
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self._player.direction = Direction.UP
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self._player.direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self._player.direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self._player.direction = Direction.RIGHT
                    elif event.key == pygame.K_ESCAPE:
                        self._state = GameState.PAUSED
                        
                elif self._state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self._state = GameState.PLAYING
                    elif event.key == pygame.K_RETURN:
                        self._state = GameState.MENU
                        
                elif self._state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        self._reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self._state = GameState.MENU
                        
                elif self._state == GameState.VICTORY:
                    if event.key == pygame.K_RETURN:
                        self._reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self._state = GameState.MENU
        
        return True

    def update(self, delta_time):
        """Atualiza lógica do jogo"""
        if self._state != GameState.PLAYING:
            return
            
        # Atualiza player
        self._player.update(delta_time, self._map)
        
        # Atualiza fantasmas
        for ghost in self._ghosts:
            ghost.update(delta_time, self._player.position, self._map, self._ghosts)
        
        # Colisão com pellets
        pellets_to_remove = []
        for pellet in self._pellets:
            distance = self._player.position.distance_to(pellet.position)
            collision_radius = sprite_manager.sprite_size // 2
            if distance < collision_radius:
                # Come o pellet
                points = pellet.be_eaten()
                self._player.eat_pellet(points)
                
                # Remove pellet do mapa
                self._map.remove_pellet_at(pellet.position)
                
                # Ativa power-up se necessário
                if pellet.type == "power_up":
                    self._player.activate_power_up()
                    # Torna todos os fantasmas vulneráveis
                    for ghost in self._ghosts:
                        ghost.set_vulnerable(8000)  # 8 segundos
                    # TODO: Tocar som de power-up
                    # pygame.mixer.Sound.play(self._sound_power_up)
                else:
                    # TODO: Tocar som de comer pellet
                    # pygame.mixer.Sound.play(self._sound_eat)
                    pass  # Placeholder para futuras funcionalidades
                
                pellets_to_remove.append(pellet)
        
        # Remove pellets comidos
        for pellet in pellets_to_remove:
            self._pellets.remove(pellet)
        
        # Verifica vitória
        if len(self._pellets) == 0:
            self._state = GameState.VICTORY
            return
        
        # Colisão com fantasmas
        for ghost in self._ghosts:
            distance = self._player.position.distance_to(ghost.position)
            collision_radius = sprite_manager.sprite_size // 2
            if distance < collision_radius:
                if ghost.state == "vulnerable":
                    # Come o fantasma
                    self._player.eat_pellet(200)
                    ghost.reset_position()
                    # TODO: Adicionar efeito visual/sonoro
                elif ghost.state == "normal":
                    # Perde vida
                    self._player.lose_life()
                    
                    if self._player.lives <= 0:
                        self._state = GameState.GAME_OVER
                    else:
                        # Reinicia posições
                        self._reset_positions()
                        # Pequena pausa
                        pygame.time.wait(1000)

    def _draw_text_centered(self, text, font, color, y_offset=0):
        """Desenha texto centralizado na tela"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self._width // 2, self._height // 2 + y_offset))
        self._screen.blit(text_surface, text_rect)

    def _draw_hud(self):
        """Desenha interface do usuário"""
        # Pontuação
        score_text = self._font_small.render(f"Pontuação: {self._player.score}", True, (255, 255, 255))
        self._screen.blit(score_text, (10, 10))
        
        # Vidas
        lives_text = self._font_small.render(f"Vidas: {self._player.lives}", True, (255, 255, 255))
        lives_rect = lives_text.get_rect(topright=(self._width - 10, 10))
        self._screen.blit(lives_text, lives_rect)
        
        # Pellets restantes
        pellets_remaining = len(self._pellets)
        pellets_text = self._font_small.render(f"Pellets: {pellets_remaining}", True, (255, 255, 255))
        self._screen.blit(pellets_text, (10, 35))
        
        # Indicador de power-up
        if self._player.power_up_active:
            power_text = self._font_small.render("POWER-UP ATIVO!", True, (255, 255, 0))
            power_rect = power_text.get_rect(center=(self._width // 2, 30))
            self._screen.blit(power_text, power_rect)

    def render(self):
        """Renderiza a tela"""
        self._screen.fill((0, 0, 0))  # Fundo preto
        
        if self._state == GameState.MENU:
            # Tela do menu
            self._draw_text_centered("PAC-MAN OO", self._font_large, (255, 255, 0), -50)
            self._draw_text_centered("Com Sprites 16x16!", self._font_medium, (255, 255, 255), -10)
            self._draw_text_centered("ENTER - Jogar", self._font_small, (255, 255, 255), 30)
            self._draw_text_centered("ESC - Sair", self._font_small, (255, 255, 255), 55)
            self._draw_text_centered("Controles: WASD ou Setas", self._font_small, (200, 200, 200), 100)
            
        elif self._state == GameState.PLAYING:
            # Jogo em andamento
            self._map.draw(self._screen)
            
            # Desenha pellets
            for pellet in self._pellets:
                pellet.draw(self._screen)
            
            # Desenha personagens
            self._player.draw(self._screen)
            for ghost in self._ghosts:
                ghost.draw(self._screen)
            
            # Interface
            self._draw_hud()
            
        elif self._state == GameState.PAUSED:
            # Jogo pausado
            self._map.draw(self._screen)
            for pellet in self._pellets:
                pellet.draw(self._screen)
            self._player.draw(self._screen)
            for ghost in self._ghosts:
                ghost.draw(self._screen)
            
            # Overlay de pausa
            pause_surface = pygame.Surface((self._width, self._height))
            pause_surface.set_alpha(128)
            pause_surface.fill((0, 0, 0))
            self._screen.blit(pause_surface, (0, 0))
            
            self._draw_text_centered("PAUSADO", self._font_large, (255, 255, 255), -30)
            self._draw_text_centered("ESC - Continuar", self._font_small, (255, 255, 255), 10)
            self._draw_text_centered("ENTER - Menu", self._font_small, (255, 255, 255), 35)
            
        elif self._state == GameState.GAME_OVER:
            # Tela de game over
            self._draw_text_centered("GAME OVER", self._font_large, (255, 0, 0), -50)
            self._draw_text_centered(f"Pontuação Final: {self._player.score}", self._font_medium, (255, 255, 255), -10)
            self._draw_text_centered(f"Pellets Comidos: {self._total_pellets - len(self._pellets)}/{self._total_pellets}", 
                                   self._font_small, (255, 255, 255), 20)
            self._draw_text_centered("ENTER - Jogar Novamente", self._font_small, (255, 255, 255), 50)
            self._draw_text_centered("ESC - Menu", self._font_small, (255, 255, 255), 75)
            
        elif self._state == GameState.VICTORY:
            # Tela de vitória
            self._draw_text_centered("VITÓRIA!", self._font_large, (0, 255, 0), -50)
            self._draw_text_centered(f"Pontuação Final: {self._player.score}", self._font_medium, (255, 255, 255), -10)
            self._draw_text_centered("Todos os pellets foram coletados!", self._font_small, (255, 255, 255), 20)
            self._draw_text_centered("ENTER - Jogar Novamente", self._font_small, (255, 255, 255), 50)
            self._draw_text_centered("ESC - Menu", self._font_small, (255, 255, 255), 75)
        
        pygame.display.flip()

    def run(self):
        """Loop principal do jogo"""
        running = True
        while running:
            delta_time = self._clock.tick(60) / 1000.0  # 60 FPS, tempo em segundos
            
            running = self.process_events()
            self.update(delta_time)
            self.render()
        
        pygame.quit()
        sys.exit()

def main():
    """Função principal"""
    try:
        game = Game(width=560, height=336)  # Dimensões ajustadas para sprites 16x16
        game.run()
    except Exception as e:
        print(f"Erro ao executar o jogo: {e}")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main() 