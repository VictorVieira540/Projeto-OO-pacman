import pygame
import sys
import json
import os
from src.game_objects import Player, Ghost, Pellet
from src.map import Map
from src.utils import Vector2D, Direction, GameState
from src.sprite_manager import sprite_manager
from src.sound_manager import sound_manager, SoundType

class HighScoreManager:
    def __init__(self, filename="highscores.json"):
        self.filename = filename
        self.highscores = self.load_highscores()

    def load_highscores(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except Exception:
                    return []
        return []

    def save_highscores(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.highscores, f, ensure_ascii=False, indent=2)

    def add_score(self, name, score):
        self.highscores.append({"name": name, "score": score})
        self.highscores = sorted(self.highscores, key=lambda x: x["score"], reverse=True)[:10]  # Top 10
        self.save_highscores()

class Game:
    def __init__(self, width=560, height=400):  # Aumentar altura para acomodar HUD
        pygame.init()
        
        # Inicializa o mixer do Pygame explicitamente
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("Mixer do Pygame inicializado no Game")
        except Exception as e:
            print(f"Erro ao inicializar mixer no Game: {e}")
        
        self._width = width
        self._height = height
        self._map_height = 336  # 21 células * 16px
        self._hud_y_start = self._map_height + 5  # HUD começa 5px abaixo do mapa
        self._screen = pygame.display.set_mode((self._width, self._height))
        pygame.display.set_caption("Pac-Man OO - Projeto Orientado a Objetos")
        self._clock = pygame.time.Clock()
        self._state = GameState.MENU
        self._font_large = pygame.font.Font(None, 48)
        self._font_medium = pygame.font.Font(None, 32)
        self._font_small = pygame.font.Font(None, 24)
        
        # Inicializa o sistema de sons
        self._initialize_sound_system()
        
        self._menu_options = ["Jogar", "Opções", "Sair"]
        self._selected_option = 0
        self._menu_animation_frame = 0
        
        self._options_menu = ["Ver Histórico", "Volume Música", "Volume Efeitos", "Volume Interface", "Volume Fantasmas", "Voltar"]
        self._selected_option_options = 0
        self._volume_step = 0.1
        
        self._history_page = 0
        self._history_per_page = 8
        
        self._highscore_manager = HighScoreManager()
        self._input_active = False
        self._player_name = ""
        self._show_save_confirmation = False
        self._save_confirmation_timer = 0
        
        # Sistema de campanha através dos mapas
        self._available_maps = []
        self._current_map_index = 0
        self._campaign_total_score = 0
        self._intermission_timer = 0
        self._intermission_duration = 3000  # 3 segundos
        self._next_map_info = None
        
        self._initialize_campaign()
        self._initialize_game()

    def _initialize_sound_system(self):
        """Inicializa o sistema de sons do jogo"""
        # Configura volumes iniciais
        sound_manager.set_volume(SoundType.MUSIC, 0.5)
        sound_manager.set_volume(SoundType.EFFECT, 0.7)
        sound_manager.set_volume(SoundType.UI, 0.8)
        sound_manager.set_volume(SoundType.GHOST, 0.6)
        
        # Inicia música de fundo
        sound_manager.play_sound("music_menu")

    def _initialize_campaign(self):
        """Inicializa o sistema de campanha carregando todos os mapas disponíveis"""
        from src.map import Map
        self._available_maps = Map.get_available_maps()
        self._current_map_index = 0
        self._campaign_total_score = 0
        
        print(f"Campanha inicializada com {len(self._available_maps)} mapas:")
        for i, map_info in enumerate(self._available_maps):
            difficulty_label = self._get_difficulty_label(map_info['difficulty'])
            print(f"  {i+1}. {map_info['name']} - {map_info['difficulty']}/200 ({difficulty_label})")

    def _get_difficulty_label(self, difficulty):
        """Converte valor de dificuldade para label"""
        if difficulty >= 175:
            return "EXTREMO"
        elif difficulty >= 150:
            return "MUITO DIFÍCIL"
        elif difficulty >= 125:
            return "DIFÍCIL+"
        elif difficulty >= 100:
            return "DIFÍCIL"
        elif difficulty >= 75:
            return "MÉDIO+"
        elif difficulty >= 50:
            return "MÉDIO"
        elif difficulty >= 25:
            return "FÁCIL+"
        else:
            return "MUITO FÁCIL"

    def _get_difficulty_color(self, difficulty):
        """Retorna cor baseada na dificuldade"""
        if difficulty >= 175:
            return (150, 0, 0)      # Vermelho escuro - EXTREMO
        elif difficulty >= 150:
            return (200, 0, 0)      # Vermelho - Muito difícil
        elif difficulty >= 125:
            return (255, 50, 50)    # Vermelho claro - Difícil+
        elif difficulty >= 100:
            return (255, 100, 0)    # Laranja avermelhado - Difícil
        elif difficulty >= 75:
            return (255, 150, 50)   # Laranja - Médio+
        elif difficulty >= 50:
            return (255, 255, 50)   # Amarelo - Médio
        elif difficulty >= 25:
            return (150, 255, 150)  # Verde claro - Fácil+
        else:
            return (100, 255, 100)  # Verde - Muito fácil

    def _initialize_game(self):
        """Inicializa os objetos do jogo"""
        # Mapa - carrega o mapa atual da campanha
        current_map_path = None
        if self._available_maps and self._current_map_index < len(self._available_maps):
            current_map_path = self._available_maps[self._current_map_index]['file_path']
        
        if hasattr(self, '_map') and self._map is not None and current_map_path:
            # Carrega novo mapa da campanha
            self._map = Map(map_file_path=current_map_path)
        elif current_map_path:
            # Cria mapa com arquivo específico da campanha
            self._map = Map(map_file_path=current_map_path)
        else:
            # Fallback para mapa padrão
            self._map = Map()
        
        # Jogador
        player_pos = self._map.get_spawn_position("player")
        self._player = Player(
            x=player_pos.x, 
            y=player_pos.y, 
            color=(255, 255, 0), 
            size=sprite_manager.sprite_size,  # Usa tamanho do sprite
            speed=2,  
            lives=20
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
        
        # Pellets - recria a partir do mapa resetado
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
        
        # Define dificuldade dos fantasmas baseada no mapa (NOVO SISTEMA!)
        map_difficulty = self._map.difficulty
        for ghost in self._ghosts:
            ghost.set_difficulty(map_difficulty)
        
        print(f"Mapa carregado: {self._map.metadata.get('name', 'Sem nome')}")
        print(f"Dificuldade do mapa: {map_difficulty}/200 ({map_difficulty/2}%)")
        print(f"Pellets no mapa: {len(self._pellets)}")

    def _reset_game(self):
        """Reinicia o jogo completamente"""
        # Para todos os sons
        sound_manager.stop_all_sounds()
        
        # Reseta variáveis de estado relacionadas a input/save
        self._input_active = False
        self._player_name = ""
        self._show_save_confirmation = False
        self._save_confirmation_timer = 0
        
        # Reseta campanha para o primeiro mapa
        self._current_map_index = 0
        self._campaign_total_score = 0
        
        # Reinicializa o jogo
        self._initialize_game()
        
        # A dificuldade agora é fixa baseada no mapa - não precisa resetar
        
        self._state = GameState.PLAYING
        
        # Inicia música do jogo
        sound_manager.play_sound("start-music")

    def _reset_positions(self):
        """Reinicia posições após morte"""
        player_pos = self._map.get_spawn_position("player")
        self._player.position = player_pos
        
        for ghost in self._ghosts:
            ghost.reset_position()

    # Métodos de dificuldade progressiva removidos - agora dificuldade é fixa por mapa

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state

    def _set_game_over(self):
        self._state = GameState.GAME_OVER
        self._input_active = True
        self._player_name = ""
        self._show_save_confirmation = False

    def process_events(self):
        """Processa eventos do jogador"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if self._state == GameState.MENU:
                    if event.key == pygame.K_UP:
                        self._selected_option = (self._selected_option - 1) % len(self._menu_options)
                    elif event.key == pygame.K_DOWN:
                        self._selected_option = (self._selected_option + 1) % len(self._menu_options)
                    elif event.key == pygame.K_RETURN:
                        if self._selected_option == 0:
                            # Força reset completo do jogo antes de iniciar
                            self._reset_game()
                        elif self._selected_option == 1:
                            self._state = GameState.OPTIONS
                        elif self._selected_option == 2:
                            return False
                    elif event.key == pygame.K_ESCAPE:
                        return False
                
                elif self._state == GameState.OPTIONS:
                    if event.key == pygame.K_UP:
                        self._selected_option_options = (self._selected_option_options - 1) % len(self._options_menu)
                    elif event.key == pygame.K_DOWN:
                        self._selected_option_options = (self._selected_option_options + 1) % len(self._options_menu)
                    elif event.key == pygame.K_RETURN:
                        if self._selected_option_options == 0:  # Ver Histórico
                            self._state = GameState.HISTORY
                            self._history_page = 0
                        elif self._selected_option_options == 1:  # Volume Música
                            pass  # Controlado pelas setas laterais
                        elif self._selected_option_options == 5:  # Voltar
                            self._state = GameState.MENU
                    elif event.key == pygame.K_LEFT:
                        if self._selected_option_options == 1:  # Volume Música
                            current = sound_manager.get_volume(SoundType.MUSIC)
                            new_volume = max(0.0, current - self._volume_step)
                            sound_manager.set_volume(SoundType.MUSIC, new_volume)
                        elif self._selected_option_options == 2:  # Volume Efeitos
                            current = sound_manager.get_volume(SoundType.EFFECT)
                            new_volume = max(0.0, current - self._volume_step)
                            sound_manager.set_volume(SoundType.EFFECT, new_volume)
                        elif self._selected_option_options == 3:  # Volume Interface
                            current = sound_manager.get_volume(SoundType.UI)
                            new_volume = max(0.0, current - self._volume_step)
                            sound_manager.set_volume(SoundType.UI, new_volume)
                        elif self._selected_option_options == 4:  # Volume Fantasmas
                            current = sound_manager.get_volume(SoundType.GHOST)
                            new_volume = max(0.0, current - self._volume_step)
                            sound_manager.set_volume(SoundType.GHOST, new_volume)
                        else:  # Voltar ao menu principal
                            self._state = GameState.MENU
                    elif event.key == pygame.K_RIGHT:
                        if self._selected_option_options == 1:  # Volume Música
                            current = sound_manager.get_volume(SoundType.MUSIC)
                            new_volume = min(1.0, current + self._volume_step)
                            sound_manager.set_volume(SoundType.MUSIC, new_volume)
                        elif self._selected_option_options == 2:  # Volume Efeitos
                            current = sound_manager.get_volume(SoundType.EFFECT)
                            new_volume = min(1.0, current + self._volume_step)
                            sound_manager.set_volume(SoundType.EFFECT, new_volume)
                        elif self._selected_option_options == 3:  # Volume Interface
                            current = sound_manager.get_volume(SoundType.UI)
                            new_volume = min(1.0, current + self._volume_step)
                            sound_manager.set_volume(SoundType.UI, new_volume)
                        elif self._selected_option_options == 4:  # Volume Fantasmas
                            current = sound_manager.get_volume(SoundType.GHOST)
                            new_volume = min(1.0, current + self._volume_step)
                            sound_manager.set_volume(SoundType.GHOST, new_volume)
                    elif event.key == pygame.K_ESCAPE:
                        self._state = GameState.MENU
                
                elif self._state == GameState.HISTORY:
                    if event.key == pygame.K_UP:
                        self._history_page = max(0, self._history_page - 1)
                    elif event.key == pygame.K_DOWN:
                        max_pages = max(0, (len(self._highscore_manager.highscores) - 1) // self._history_per_page)
                        self._history_page = min(max_pages, self._history_page + 1)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_ESCAPE:
                        self._state = GameState.OPTIONS
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
                        # Pausa todos os sons
                        sound_manager.pause_all_sounds()
                        
                elif self._state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self._state = GameState.PLAYING
                        # Despausa todos os sons
                        sound_manager.unpause_all_sounds()
                    elif event.key == pygame.K_RETURN:
                        # Resetar o jogo ao voltar para o menu
                        self._initialize_game()
                        self._state = GameState.MENU
                        # Para todos os sons e volta para música do menu
                        sound_manager.stop_all_sounds()
                        sound_manager.play_sound("music_menu")
                    return True
                elif self._state == GameState.GAME_OVER:
                    # PRIORIDADE: input de nome
                    if self._input_active:
                        if event.key == pygame.K_RETURN:
                            if self._player_name.strip():
                                self._highscore_manager.add_score(self._player_name.strip(), self._player.score)
                                self._input_active = False
                                self._show_save_confirmation = True
                                self._save_confirmation_timer = pygame.time.get_ticks()
                        elif event.key == pygame.K_BACKSPACE:
                            self._player_name = self._player_name[:-1]
                        else:
                            if len(self._player_name) < 12 and event.unicode.isprintable():
                                self._player_name += event.unicode
                        return True  # Não processa mais nada enquanto input de nome está ativo
                    # Só permite ENTER para reiniciar ou ESC para menu se não estiver no input de nome
                    elif not self._input_active and not self._show_save_confirmation:
                        if event.key == pygame.K_RETURN:
                            self._reset_game()
                        elif event.key == pygame.K_ESCAPE:
                            self._state = GameState.MENU
                            sound_manager.stop_all_sounds()
                            sound_manager.play_sound("music_menu")
                        return True
                elif self._state == GameState.VICTORY:
                    # PRIORIDADE: input de nome na vitória
                    if self._input_active:
                        if event.key == pygame.K_RETURN:
                            if self._player_name.strip():
                                # Salva pontuação total da campanha
                                self._highscore_manager.add_score(self._player_name.strip(), self._campaign_total_score)
                                self._input_active = False
                                self._show_save_confirmation = True
                                self._save_confirmation_timer = pygame.time.get_ticks()
                        elif event.key == pygame.K_BACKSPACE:
                            self._player_name = self._player_name[:-1]
                        else:
                            if len(self._player_name) < 12 and event.unicode.isprintable():
                                self._player_name += event.unicode
                        return True
                    elif not self._input_active and not self._show_save_confirmation:
                        if event.key == pygame.K_RETURN:
                            self._reset_game()
                        elif event.key == pygame.K_ESCAPE:
                            self._state = GameState.MENU
                            sound_manager.stop_all_sounds()
                            sound_manager.play_sound("music_menu")
                        return True
                elif self._state == GameState.INTERMISSION:
                    if event.key == pygame.K_RETURN:
                        # Pula a intermissão e carrega próximo mapa imediatamente
                        self._initialize_game()
                        self._state = GameState.PLAYING
                        sound_manager.stop_all_sounds()
                        sound_manager.play_sound("start-music")
                    elif event.key == pygame.K_ESCAPE:
                        self._state = GameState.MENU
                        # Para todos os sons e volta para música do menu
                        sound_manager.stop_all_sounds()
                        sound_manager.play_sound("music_menu")
        
        return True

    def update(self, delta_time):
        # Sempre verifica se precisa voltar ao menu após salvar
        if self._show_save_confirmation:
            if pygame.time.get_ticks() - self._save_confirmation_timer > 1000:
                self._show_save_confirmation = False
                self._state = GameState.MENU
                sound_manager.stop_all_sounds()
                sound_manager.play_sound("music_menu")
            return  # Não precisa atualizar o resto

        # Gerencia estado de intermissão (transição entre mapas)
        if self._state == GameState.INTERMISSION:
            current_time = pygame.time.get_ticks()
            if current_time - self._intermission_timer >= self._intermission_duration:
                # Tempo de intermissão acabou - carrega próximo mapa
                self._initialize_game()
                self._state = GameState.PLAYING
                sound_manager.play_sound("start-music")
                return

        # Ativa input de nome ao entrar em VICTORY ou GAME_OVER
        if (self._state == GameState.VICTORY or self._state == GameState.GAME_OVER) and not self._input_active and not self._show_save_confirmation:
            self._input_active = True
            self._player_name = ""

        if self._state not in [GameState.PLAYING, GameState.INTERMISSION]:
            return
        
        # Toda a lógica de gameplay apenas executa durante PLAYING
        if self._state == GameState.PLAYING:
            # Atualiza player
            self._player.update(delta_time, self._map)
            
            # Atualiza fantasmas
            for ghost in self._ghosts:
                ghost.update(delta_time, self._player.position, self._player.direction, self._map, self._ghosts)
            
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
                        # Torna todos os fantasmas vulneráveis com duração ajustada pela dificuldade
                        for ghost in self._ghosts:
                            ghost.set_vulnerable(8000)  # Duração será ajustada automaticamente pela dificuldade
                        # Toca som de power-up
                        sound_manager.play_sound("ghost-turn-to-blue")
                    else:
                        # Toca som de comer pellet
                        sound_manager.play_sound("eating")
                    
                    pellets_to_remove.append(pellet)
            
            # Remove pellets comidos
            for pellet in pellets_to_remove:
                self._pellets.remove(pellet)
            
            # Verifica vitória
            if len(self._pellets) == 0:
                # Adiciona pontuação atual ao total da campanha
                self._campaign_total_score += self._player.score
                
                # Verifica se há próximo mapa na campanha
                if self._current_map_index + 1 < len(self._available_maps):
                    # Há próximo mapa - vai para intermissão
                    self._current_map_index += 1
                    self._next_map_info = self._available_maps[self._current_map_index]
                    self._state = GameState.INTERMISSION
                    self._intermission_timer = pygame.time.get_ticks()
                    
                    # Toca som de vitória do mapa
                    sound_manager.stop_all_sounds()
                    sound_manager.play_sound("extend")
                    
                    print(f"✅ Mapa completado! Avançando para: {self._next_map_info['name']}")
                else:
                    # Último mapa - campanha completa!
                    self._state = GameState.VICTORY
                    # Toca música de vitória da campanha
                    sound_manager.stop_all_sounds()
                    sound_manager.play_sound("credit")
                    
                    print(f"CAMPANHA COMPLETA! Pontuação total: {self._campaign_total_score}")
                return
            
            # Colisão com fantasmas
            for ghost in self._ghosts:
                distance = self._player.position.distance_to(ghost.position)
                collision_radius = sprite_manager.sprite_size // 2
                if distance < collision_radius:
                    if ghost.state == "vulnerable":
                        # Come o fantasma
                        self._player.eat_pellet(200)
                        # Usa novo método com delay de 5 segundos
                        ghost.set_eaten_with_delay()
                        # Toca som de comer fantasma
                        sound_manager.play_sound("eating-ghost")
                    elif ghost.state == "normal":
                        # Perde vida
                        self._player.lose_life()
                        # Toca som de morte
                        sound_manager.play_sound("miss")
                        
                        if self._player.lives <= 0:
                            self._set_game_over()
                            sound_manager.stop_all_sounds()
                            sound_manager.play_sound("miss")
                        else:
                            # Reinicia posições
                            self._reset_positions()
                            # Pequena pausa
                            pygame.time.wait(1000)
        elif self._state == GameState.INTERMISSION:
            # Durante intermissão, não executa lógica de gameplay
            return

    def _draw_text_centered(self, text, font, color, y_offset=0):
        """Desenha texto centralizado na tela"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self._width // 2, self._height // 2 + y_offset))
        self._screen.blit(text_surface, text_rect)

    def _draw_hud(self):
        """Desenha interface do usuário abaixo do mapa"""
        # Pontuação (esquerda)
        score_text = self._font_small.render(f"Pontuação: {self._player.score}", True, (255, 255, 255))
        self._screen.blit(score_text, (10, self._hud_y_start))
        
        # Vidas (direita)
        lives_text = self._font_small.render(f"Vidas: {self._player.lives}", True, (255, 255, 255))
        lives_rect = lives_text.get_rect(topright=(self._width - 10, self._hud_y_start))
        self._screen.blit(lives_text, lives_rect)
        
        # Pellets restantes (centro, linha inferior)
        pellets_remaining = len(self._pellets)
        pellets_text = self._font_small.render(f"Pellets: {pellets_remaining}", True, (255, 255, 255))
        pellets_rect = pellets_text.get_rect(center=(self._width // 2, self._hud_y_start + 25))
        self._screen.blit(pellets_text, pellets_rect)
        
        # Indicador de dificuldade do mapa (esquerda, segunda linha) - SISTEMA FIXO POR MAPA!
        if hasattr(self, '_map') and self._map is not None:
            map_difficulty = self._map.difficulty
            difficulty_color = (255, 255, 255)
            difficulty_label = "FÁCIL"
            
            # Muda cor e label baseado na dificuldade do mapa (0-200)
            if map_difficulty >= 175:
                difficulty_color = (150, 0, 0)      # Vermelho escuro - EXTREMO
                difficulty_label = "EXTREMO"
            elif map_difficulty >= 150:
                difficulty_color = (200, 0, 0)      # Vermelho - Muito difícil
                difficulty_label = "MUITO DIFÍCIL" 
            elif map_difficulty >= 125:
                difficulty_color = (255, 50, 50)    # Vermelho claro - Difícil+
                difficulty_label = "DIFÍCIL+"
            elif map_difficulty >= 100:
                difficulty_color = (255, 100, 0)    # Laranja avermelhado - Difícil
                difficulty_label = "DIFÍCIL"
            elif map_difficulty >= 75:
                difficulty_color = (255, 150, 50)   # Laranja - Médio+
                difficulty_label = "MÉDIO+"
            elif map_difficulty >= 50:
                difficulty_color = (255, 255, 50)   # Amarelo - Médio
                difficulty_label = "MÉDIO"
            elif map_difficulty >= 25:
                difficulty_color = (150, 255, 150)  # Verde claro - Fácil+
                difficulty_label = "FÁCIL+"
            else:
                difficulty_color = (100, 255, 100)  # Verde - Muito fácil
                difficulty_label = "MUITO FÁCIL"
            
            difficulty_text = self._font_small.render(f"Dificuldade:{difficulty_label}", True, difficulty_color)
            self._screen.blit(difficulty_text, (10, self._hud_y_start + 25))
        
        # Progresso da campanha (direita, segunda linha)
        if hasattr(self, '_available_maps') and self._available_maps:
            current_map = self._current_map_index + 1
            total_maps = len(self._available_maps)
            campaign_text = self._font_small.render(f"Mapa: {current_map}/{total_maps}", True, (200, 200, 255))
            campaign_rect = campaign_text.get_rect(topright=(self._width - 10, self._hud_y_start + 25))
            self._screen.blit(campaign_text, campaign_rect)
            
            # Nome do mapa atual (centro, acima dos pellets)
            if self._current_map_index < len(self._available_maps):
                map_name = self._available_maps[self._current_map_index]['name']
                # Trunca o nome se for muito longo
                if len(map_name) > 20:
                    map_name = map_name[:17] + "..."
                map_name_text = self._font_small.render(map_name, True, (150, 150, 255))
                map_name_rect = map_name_text.get_rect(center=(self._width // 2, self._hud_y_start - 40))
                self._screen.blit(map_name_text, map_name_rect)
        
        # Indicador de power-up (centro, acima dos pellets)
        if self._player.power_up_active:
            power_text = self._font_small.render("POWER-UP ATIVO!", True, (255, 255, 0))
            power_rect = power_text.get_rect(center=(self._width // 2, self._hud_y_start - 20))
            self._screen.blit(power_text, power_rect)
        
        # Indicador de fantasmas em delay (canto inferior direito)
        ghosts_in_delay = [ghost for ghost in self._ghosts if ghost.is_in_spawn_delay]
        if ghosts_in_delay:
            delay_info = []
            for ghost in ghosts_in_delay:
                remaining = ghost.spawn_delay_remaining
                delay_info.append(f"{ghost._ghost_type.capitalize()}: {remaining:.1f}s")
            
            delay_text = "Fantasmas em delay:"
            delay_surface = self._font_small.render(delay_text, True, (255, 150, 150))
            self._screen.blit(delay_surface, (self._width - 180, self._hud_y_start + 50))
            
            for i, info in enumerate(delay_info):
                info_surface = self._font_small.render(info, True, (255, 200, 200))
                self._screen.blit(info_surface, (self._width - 180, self._hud_y_start + 70 + i * 15))

    def render(self):
        """Renderiza a tela"""
        self._screen.fill((0, 0, 0))  # Fundo preto
        
        if self._state == GameState.MENU:
            self._menu_animation_frame += 1
            # Tela do menu interativo
            self._draw_text_centered("PAC-MAN", self._font_large, (255, 255, 0), -120)
            for i, option in enumerate(self._menu_options):
                color = (255, 255, 0) if i == self._selected_option else (255, 255, 255)
                text_surface = self._font_medium.render(option, True, color)
                text_rect = text_surface.get_rect(center=(self._width // 2, self._height // 2 - 20 + i * 45))
                self._screen.blit(text_surface, text_rect)
                if i == self._selected_option:
                    pacman_sprite = sprite_manager.get_pacman_sprite(Direction.RIGHT, self._menu_animation_frame)
                    sprite_rect = pacman_sprite.get_rect(center=(self._width // 2 - 120, self._height // 2 - 20 + i * 45))
                    self._screen.blit(pacman_sprite, sprite_rect)
            self._draw_text_centered("Use as setas para navegar e ENTER para selecionar", self._font_small, (200, 200, 200), 120)

        elif self._state == GameState.OPTIONS:
            self._menu_animation_frame += 1
            # Tela de opções
            self._draw_text_centered("OPÇÕES", self._font_large, (255, 255, 0), -140)
            for i, option in enumerate(self._options_menu):
                color = (255, 255, 0) if i == self._selected_option_options else (255, 255, 255)
                
                # Para opções de volume, mostrar barra de volume
                if 1 <= i <= 4:
                    volume_types = [None, SoundType.MUSIC, SoundType.EFFECT, SoundType.UI, SoundType.GHOST]
                    current_volume = sound_manager.get_volume(volume_types[i])
                    volume_text = f"{option}: {int(current_volume * 100)}%"
                    text_surface = self._font_small.render(volume_text, True, color)
                else:
                    text_surface = self._font_small.render(option, True, color)
                
                text_rect = text_surface.get_rect(center=(self._width // 2, self._height // 2 - 90 + i * 25))
                self._screen.blit(text_surface, text_rect)
                
                if i == self._selected_option_options:
                    pacman_sprite = sprite_manager.get_pacman_sprite(Direction.RIGHT, self._menu_animation_frame)
                    sprite_rect = pacman_sprite.get_rect(center=(self._width // 2 - 140, self._height // 2 - 90 + i * 25))
                    self._screen.blit(pacman_sprite, sprite_rect)
            
            self._draw_text_centered("Setas para navegar | ENTER para selecionar", self._font_small, (200, 200, 200), 110)
            self._draw_text_centered("ESQ ou ESC para voltar", self._font_small, (200, 200, 200), 130)
            if 1 <= self._selected_option_options <= 4:
                self._draw_text_centered("ESQ/DIR para ajustar volume", self._font_small, (255, 255, 0), 150)

        elif self._state == GameState.HISTORY:
            self._menu_animation_frame += 1
            # Tela de histórico
            self._draw_text_centered("HISTÓRICO DE PONTUAÇÕES", self._font_medium, (255, 255, 0), -140)
            
            scores = self._highscore_manager.highscores
            if not scores:
                self._draw_text_centered("Nenhuma pontuação registrada", self._font_medium, (255, 255, 255), 0)
            else:
                start_idx = self._history_page * self._history_per_page
                end_idx = min(start_idx + self._history_per_page, len(scores))
                
                for i in range(start_idx, end_idx):
                    score_data = scores[i]
                    position = i + 1
                    text = f"{position:2d}. {score_data['name']:12s} - {score_data['score']:6d}"
                    color = (255, 255, 0) if position <= 3 else (255, 255, 255)
                    
                    y_pos = -100 + (i - start_idx) * 20
                    self._draw_text_centered(text, self._font_small, color, y_pos)
                
                # Navegação de páginas
                if len(scores) > self._history_per_page:
                    current_page = self._history_page + 1
                    total_pages = (len(scores) - 1) // self._history_per_page + 1
                    page_text = f"Página {current_page}/{total_pages}"
                    self._draw_text_centered(page_text, self._font_small, (200, 200, 200), 80)
            
            self._draw_text_centered("setas para navegar páginas", self._font_small, (200, 200, 200), 110)
            self._draw_text_centered("ESQ ou ESC para voltar", self._font_small, (200, 200, 200), 130)

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
            
            self._draw_text_centered("PAUSADO", self._font_large, (255, 255, 255), -40)
            self._draw_text_centered("ESC - Continuar", self._font_small, (255, 255, 255), 0)
            self._draw_text_centered("ENTER - Menu", self._font_small, (255, 255, 255), 25)
            
        elif self._state == GameState.GAME_OVER:
            # Tela de game over
            self._draw_text_centered("GAME OVER", self._font_large, (255, 0, 0), -80)
            self._draw_text_centered(f"Pontuação Final: {self._player.score}", self._font_medium, (255, 255, 255), -40)
            self._draw_text_centered(f"Pellets: {self._total_pellets - len(self._pellets)}/{self._total_pellets}", 
                                   self._font_small, (255, 255, 255), -10)
            if self._input_active:
                self._draw_text_centered("Digite seu nome e pressione ENTER:", self._font_small, (255, 255, 0), 30)
                name_surface = self._font_medium.render(self._player_name + "|", True, (255, 255, 255))
                name_rect = name_surface.get_rect(center=(self._width // 2, self._height // 2 + 70))
                self._screen.blit(name_surface, name_rect)
            elif self._show_save_confirmation:
                self._draw_text_centered("Pontuação salva!", self._font_small, (0, 255, 0), 30)
            else:
                self._draw_text_centered("ENTER - Jogar Novamente", self._font_small, (255, 255, 255), 30)
                self._draw_text_centered("ESC - Menu", self._font_small, (255, 255, 255), 55)
            
        elif self._state == GameState.VICTORY:
            # Tela de vitória da campanha
            self._draw_text_centered("CAMPANHA COMPLETA!", self._font_large, (255, 215, 0), -100)
            
            # Estatísticas da campanha
            total_maps = len(self._available_maps)
            self._draw_text_centered(f"Mapas Completados: {total_maps}/{total_maps}", 
                                   self._font_medium, (0, 255, 0), -60)
            self._draw_text_centered(f"Pontuação Total: {self._campaign_total_score}", 
                                   self._font_medium, (255, 255, 0), -30)
            
            # Média por mapa
            if total_maps > 0:
                average_score = self._campaign_total_score // total_maps
                self._draw_text_centered(f"Média por Mapa: {average_score}", 
                                       self._font_small, (200, 200, 200), 0)
            
            # Mensagem de parabéns
            self._draw_text_centered("Parabéns! Você dominou todos os mapas!", 
                                   self._font_small, (255, 255, 255), 30)
            
            if self._input_active:
                self._draw_text_centered("Digite seu nome e pressione ENTER:", self._font_small, (255, 255, 0), 60)
                name_surface = self._font_medium.render(self._player_name + "|", True, (255, 255, 255))
                name_rect = name_surface.get_rect(center=(self._width // 2, self._height // 2 + 100))
                self._screen.blit(name_surface, name_rect)
            elif self._show_save_confirmation:
                self._draw_text_centered("Pontuação salva!", self._font_small, (0, 255, 0), 60)
            else:
                self._draw_text_centered("ENTER - Nova Campanha", self._font_small, (255, 255, 255), 60)
                self._draw_text_centered("ESC - Menu", self._font_small, (255, 255, 255), 85)
        
        elif self._state == GameState.INTERMISSION:
            # Tela de intermissão (transição entre mapas)
            self._draw_text_centered("MAPA COMPLETADO!", self._font_large, (0, 255, 0), -120)
            
            # Informações da campanha
            current_map = self._current_map_index 
            total_maps = len(self._available_maps)
            self._draw_text_centered(f"Progresso da Campanha: {current_map}/{total_maps}", 
                                   self._font_medium, (255, 255, 255), -80)
            
            # Pontuação total
            self._draw_text_centered(f"Pontuação Total: {self._campaign_total_score}", 
                                   self._font_small, (255, 255, 0), -50)
            
            # Informações do próximo mapa
            if self._next_map_info:
                self._draw_text_centered("PRÓXIMO MAPA:", self._font_medium, (255, 255, 255), -10)
                self._draw_text_centered(f"{self._next_map_info['name']}", 
                                       self._font_medium, (255, 255, 0), 15)
                
                difficulty_label = self._get_difficulty_label(self._next_map_info['difficulty'])
                difficulty_color = self._get_difficulty_color(self._next_map_info['difficulty'])
                self._draw_text_centered(f"Dificuldade: {difficulty_label}", 
                                       self._font_small, difficulty_color, 40)
                
                # Tamanho do mapa
                self._draw_text_centered(f"Tamanho: {self._next_map_info['width']}x{self._next_map_info['height']}", 
                                       self._font_small, (200, 200, 200), 60)
                
                # Descrição se houver
                if self._next_map_info.get('description'):
                    self._draw_text_centered(f"'{self._next_map_info['description']}'", 
                                           self._font_small, (150, 150, 150), 80)
            
            # Barra de progresso do countdown
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self._intermission_timer
            progress = min(elapsed / self._intermission_duration, 1.0)
            remaining_time = max(0, (self._intermission_duration - elapsed) / 1000.0)
            
            # Texto do countdown
            self._draw_text_centered(f"Carregando em {remaining_time:.1f}s", 
                                   self._font_small, (255, 255, 255), 110)
            
            # Barra de progresso visual
            bar_width = 300
            bar_height = 10
            bar_x = (self._width - bar_width) // 2
            bar_y = self._height // 2 + 140
            
            # Fundo da barra
            pygame.draw.rect(self._screen, (50, 50, 50), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Progresso da barra
            progress_width = int(bar_width * progress)
            if progress_width > 0:
                pygame.draw.rect(self._screen, (0, 255, 0), 
                               (bar_x, bar_y, progress_width, bar_height))
            
            # Borda da barra
            pygame.draw.rect(self._screen, (255, 255, 255), 
                           (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Instruções
            self._draw_text_centered("ENTER - Pular | ESC - Menu", 
                                   self._font_small, (150, 150, 150), 170)
        
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
        game = Game(width=560, height=400)  # Ajustar altura para acomodar HUD
        game.run()
    except Exception as e:
        print(f"Erro ao executar o jogo: {e}")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main() 