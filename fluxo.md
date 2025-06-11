# Fluxo de Execução do Pac-Man - Documentação Técnica

## 1. Arquitetura do Jogo

### 1.1 Estrutura de Classes
```
Game (Classe Principal)
├── GameObject (Classe Abstrata Base)
│   ├── MovableObject (Classe Abstrata)
│   │   ├── Player
│   │   └── Ghost
│   └── Pellet
├── Map
└── SpriteManager
```

### 1.2 Dependências Principais
- Pygame: Biblioteca principal para renderização e eventos
- Enum: Para gerenciamento de estados e direções
- Vector2D: Classe personalizada para cálculos de posição

## 2. Inicialização e Configuração

### 2.1 Configuração do Pygame
```python
pygame.init()
self._screen = pygame.display.set_mode((560, 336))  # 35x21 células de 16px
self._clock = pygame.time.Clock()  # Controle de FPS
```

### 2.2 Inicialização de Recursos
- Carregamento de sprites (16x16 pixels)
- Configuração de fontes para UI
- Inicialização do sistema de áudio (preparado para implementação)

## 3. Sistema de Estados

### 3.1 Implementação do Estado
```python
class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    PAUSED = 3
    VICTORY = 4
```

### 3.2 Transições de Estado
- Menu → Playing: Tecla ENTER
- Playing → Paused: Tecla ESC
- Playing → Game Over: Vidas = 0
- Playing → Victory: Pellets coletados = 0

## 4. Loop Principal (Game Loop)

### 4.1 Estrutura do Loop
```python
def run(self):
    running = True
    while running:
        delta_time = self._clock.tick(60) / 1000.0  # 60 FPS
        running = self.process_events()
        self.update(delta_time)
        self.render()
```

### 4.2 Processamento de Eventos
- Sistema de eventos baseado em Pygame
- Mapeamento de teclas:
  - WASD / Setas: Movimento do jogador
  - ESC: Pausa/Menu
  - ENTER: Iniciar/Reiniciar

### 4.3 Atualização do Estado
- Delta time para movimento suave
- Atualização de posições
- Verificação de colisões
- Gerenciamento de power-ups

### 4.4 Renderização
- Double buffering (pygame.display.flip())
- Renderização em camadas:
  1. Fundo (Mapa)
  2. Pellets
  3. Personagens
  4. UI/HUD

## 5. Sistema de Colisão

### 5.1 Detecção de Colisão
```python
def get_rect(self):
    sprite_size = sprite_manager.sprite_size
    return pygame.Rect(
        self._position.x - sprite_size // 2,
        self._position.y - sprite_size // 2,
        sprite_size,
        sprite_size
    )
```

### 5.2 Tipos de Colisão
- Jogador-Pellet: Coleta de pontos
- Jogador-Fantasma: 
  - Fantasma normal: Perda de vida
  - Fantasma vulnerável: Pontuação extra

## 6. Sistema de Movimento

### 6.1 Movimento do Jogador
- Direção atual e próxima direção
- Verificação de colisão antes do movimento
- Velocidade base: 2 unidades por frame

### 6.2 Movimento dos Fantasmas
- 4 tipos diferentes de comportamento
- Sistema de pathfinding
- Estados: Normal, Vulnerável, Comido

## 7. Sistema de Pontuação

### 7.1 Valores de Pontuação
```python
PELLET_NORMAL = 10
POWER_UP = 50
GHOST_VULNERABLE = 200
```

### 7.2 Gerenciamento de Pontuação
- Atualização em tempo real
- Persistência durante o jogo
- Exibição no HUD

## 8. Sistema de Power-ups

### 8.1 Implementação
```python
def activate_power_up(self):
    self._power_up_active = True
    self._power_up_timer = self._power_up_duration  # 5000ms
```

### 8.2 Efeitos
- Fantasmas ficam vulneráveis
- Duração: 5 segundos
- Timer de contagem regressiva

## 9. Sistema de Vidas

### 9.1 Gerenciamento
- Início: 3 vidas
- Perda: Colisão com fantasma normal
- Game Over: Vidas = 0

## 10. Otimizações

### 10.1 Performance
- Delta time para movimento consistente
- Sprite caching
- Otimização de colisões

### 10.2 Memória
- Gerenciamento eficiente de sprites
- Limpeza de objetos não utilizados
- Reutilização de objetos

## 11. Debug e Logging

### 11.1 Informações de Debug
```python
print(f"Estado do jogo: {self._state}")
print(f"Posição do jogador: {self._player.position}")
print(f"Pellets restantes: {len(self._pellets)}")
```

### 11.2 Tratamento de Erros
- Try-catch para exceções críticas
- Logging de erros
- Recuperação graciosa de falhas

## 12. Extensibilidade

### 12.1 Pontos de Extensão
- Novos tipos de power-ups
- Diferentes comportamentos de fantasmas
- Novos mapas e layouts

### 12.2 Preparação para Features Futuras
- Sistema de áudio preparado
- Estrutura para múltiplos níveis
- Sistema de high scores 

## 13. Fluxo de Chamada dos Métodos

### 13.1 Inicialização do Jogo
Quando o jogo é iniciado, uma sequência específica de inicialização é seguida:

1. A função `main()` é o ponto de entrada do programa
2. Ela cria uma instância da classe `Game`
3. Durante a inicialização do `Game`:
   - O Pygame é inicializado para gerenciar gráficos e eventos
   - O método `_initialize_game()` é chamado para configurar:
     - O mapa do jogo é carregado com `Map.load_default_map()`
     - O jogador é criado com `Player.__init__()`
     - Os 4 fantasmas são criados com `Ghost.__init__()`
     - Todos os pellets são criados com `Pellet.__init__()`
4. Por fim, o método `run()` é chamado para iniciar o loop principal

```python
# Sequência de inicialização
main()
└── Game.__init__()
    ├── pygame.init()
    ├── self._initialize_game()
    │   ├── Map.load_default_map()
    │   ├── Player.__init__()
    │   ├── Ghost.__init__() [4x]
    │   └── Pellet.__init__() [Nx]
    └── Game.run()
```

### 13.2 Game Loop Principal
O coração do jogo é o loop principal, que executa 60 vezes por segundo. Cada iteração do loop:

1. **Controle de Tempo**:
   - Calcula o tempo entre frames (delta_time)
   - Mantém o jogo rodando a 60 FPS

2. **Processamento de Eventos**:
   - Captura eventos do teclado e mouse
   - Gerencia o fechamento do jogo
   - Processa comandos do jogador
   - Controla transições entre estados do jogo

3. **Atualização do Estado**:
   - Atualiza a posição do jogador
   - Move os fantasmas
   - Verifica colisões
   - Atualiza pontuação e vidas

4. **Renderização**:
   - Limpa a tela
   - Desenha todos os elementos
   - Atualiza a tela

Game.run()
├── while running:
    │
    ├── # Passo 1: Controle de Tempo
    ├── delta_time = self._clock.tick(60) / 1000.0
    │
    ├── # Passo 2: Processamento de Eventos
    ├── self.process_events()
    │   ├── pygame.event.get()
    │   ├── if event.type == pygame.QUIT:
    │   │   └── return False
    │   ├── if event.type == pygame.KEYDOWN:
    │   │   ├── if self._state == GameState.MENU:
    │   │   │   └── self._state = GameState.PLAYING
    │   │   ├── if self._state == GameState.PLAYING:
    │   │   │   └── self._player.direction = nova_direcao
    │   │   └── if self._state == GameState.PAUSED:
    │   │       └── self._state = GameState.PLAYING
    │   └── return True
    │
    ├── # Passo 3: Atualização do Estado do Jogo
    ├── self.update(delta_time)
    │   ├── # 3.1: Verifica Estado do Jogo
    │   ├── if self._state != GameState.PLAYING:
    │   │   └── return
    │   │
    │   ├── # 3.2: Atualiza Jogador
    │   ├── self._player.update(delta_time, self._map)
    │   │   ├── # 3.2.1: Verifica Movimento Possível
    │   │   ├── self.can_move(direction, game_map)
    │   │   │   ├── next_pos = Vector2D(x + dx, y + dy)
    │   │   │   └── return game_map.is_valid_position(next_pos)
    │   │   │
    │   │   ├── # 3.2.2: Executa Movimento
    │   │   └── self.move(direction)
    │   │       └── self._position += Vector2D(dx, dy)
    │   │
    │   ├── # 3.3: Atualiza Fantasmas
    │   ├── for ghost in self._ghosts:
    │   │   └── ghost.update(delta_time, self._player.position, self._map, self._ghosts)
    │   │
    │   ├── # 3.4: Verifica Colisões com Pellets
    │   ├── for pellet in self._pellets:
    │   │   ├── if collision:
    │   │   │   ├── pellet.be_eaten()
    │   │   │   ├── self._player.eat_pellet(points)
    │   │   │   └── if power_up:
    │   │   │       └── self._player.activate_power_up()
    │   │
    │   ├── # 3.5: Verifica Colisões com Fantasmas
    │   └── for ghost in self._ghosts:
    │       ├── if collision:
    │       │   ├── if ghost.state == "vulnerable":
    │       │   │   ├── self._player.eat_pellet(200)
    │       │   │   └── ghost.reset_position()
    │       │   └── if ghost.state == "normal":
    │       │       ├── self._player.lose_life()
    │       │       └── self._reset_positions()
    │
    ├── # Passo 4: Renderização
    └── self.render()
        ├── # 4.1: Limpa a Tela
        ├── self._screen.fill((0, 0, 0))
        │
        ├── # 4.2: Renderiza Menu
        ├── if self._state == GameState.MENU:
        │   └── self._draw_text_centered()
        │
        ├── # 4.3: Renderiza Jogo
        ├── if self._state == GameState.PLAYING:
        │   ├── self._map.draw(self._screen)
        │   ├── for pellet in self._pellets:
        │   │   └── pellet.draw(self._screen)
        │   ├── self._player.draw(self._screen)
        │   ├── for ghost in self._ghosts:
        │   │   └── ghost.draw(self._screen)
        │   └── self._draw_hud()
        │
        ├── # 4.4: Atualiza a Tela
        └── pygame.display.flip()
```

### 13.3 Fluxo de Movimento do Jogador
O movimento do jogador é um processo em duas etapas:

1. **Captura da Direção**:
   - O jogador pressiona uma tecla
   - O evento é processado
   - A nova direção é definida

2. **Aplicação do Movimento**:
   - Verifica se o movimento é possível
   - Calcula a nova posição
   - Atualiza a posição do jogador

```python
# Sequência de movimento do jogador
process_events()
└── self._player.direction = nova_direcao
    └── update(delta_time)
        ├── can_move(direction, game_map)
        │   ├── next_pos = Vector2D(x + dx, y + dy)
        │   └── return game_map.is_valid_position(next_pos)
        └── move(direction)
            └── self._position += Vector2D(dx, dy)
```


### 13.4 Fluxo de Colisão
O sistema de colisão verifica dois tipos principais de interações:

1. **Colisão com Pellets**:
   - Calcula a distância entre jogador e pellet
   - Se houver colisão:
     - Remove o pellet
     - Adiciona pontos
     - Ativa power-up se for o caso

2. **Colisão com Fantasmas**:
   - Verifica a distância entre jogador e fantasma
   - Se houver colisão:
     - Se o fantasma estiver vulnerável: come o fantasma
     - Se o fantasma estiver normal: perde uma vida

```python
# Sequência de detecção de colisão
update(delta_time)
├── for pellet in self._pellets:
│   ├── distance = self._player.position.distance_to(pellet.position)
│   └── if distance < collision_radius:
│       ├── pellet.be_eaten()
│       ├── self._player.eat_pellet(points)
│       └── if pellet.type == "power_up":
│           └── self._player.activate_power_up()
│
└── for ghost in self._ghosts:
    ├── distance = self._player.position.distance_to(ghost.position)
    └── if distance < collision_radius:
        ├── if ghost.state == "vulnerable":
        │   ├── self._player.eat_pellet(200)
        │   └── ghost.reset_position()
        └── if ghost.state == "normal":
            └── self._player.lose_life()
```

### 13.5 Fluxo de Power-up
Quando um power-up é ativado:

1. **Ativação**:
   - Marca o power-up como ativo
   - Inicia o timer de duração
   - Torna todos os fantasmas vulneráveis

2. **Efeitos**:
   - Duração: 8 segundos
   - Fantasmas mudam de cor
   - Jogador pode comer fantasmas

```python
# Sequência de ativação de power-up
activate_power_up()
├── self._power_up_active = True
├── self._power_up_timer = self._power_up_duration
└── for ghost in self._ghosts:
    └── ghost.set_vulnerable(8000)
```

### 13.6 Fluxo de Renderização
A renderização segue uma ordem específica para garantir que os elementos sejam desenhados corretamente:

1. **Preparação**:
   - Limpa a tela com cor preta

2. **Elementos do Jogo**:
   - Desenha o mapa de fundo
   - Renderiza todos os pellets
   - Desenha o jogador
   - Renderiza os fantasmas

3. **Interface**:
   - Desenha o HUD com informações do jogo
   - Atualiza a tela

```python
# Sequência de renderização
render()
├── self._screen.fill((0, 0, 0))
├── if self._state == GameState.PLAYING:
│   ├── self._map.draw(self._screen)
│   ├── for pellet in self._pellets:
│   │   └── pellet.draw(self._screen)
│   ├── self._player.draw(self._screen)
│   ├── for ghost in self._ghosts:
│   │   └── ghost.draw(self._screen)
│   └── self._draw_hud()
└── pygame.display.flip()
```

### 13.7 Fluxo de Transição de Estados
O jogo muda de estado baseado em diferentes condições:

1. **Menu para Jogo**:
   - Pressionar ENTER inicia o jogo

2. **Jogo para Pausa**:
   - ESC pausa o jogo
   - ESC novamente retorna ao jogo

3. **Condições de Fim**:
   - Sem vidas = Game Over
   - Todos pellets coletados = Vitória

```python
# Sequência de transição de estados
process_events()
├── if self._state == GameState.MENU:
│   └── if event.key == pygame.K_RETURN:
│       └── self._state = GameState.PLAYING
├── if self._state == GameState.PLAYING:
│   ├── if event.key == pygame.K_ESCAPE:
│   │   └── self._state = GameState.PAUSED
│   └── if self._player.lives <= 0:
│       └── self._state = GameState.GAME_OVER
└── if len(self._pellets) == 0:
    └── self._state = GameState.VICTORY
```

### 13.8 Fluxo de Reinicialização
Existem dois tipos de reinicialização:

1. **Reinício Completo**:
   - Reinicializa todos os objetos do jogo
   - Volta ao estado de jogo

2. **Reinício de Posições**:
   - Reposiciona jogador e fantasmas
   - Mantém pontuação e vidas

```python
# Sequência de reinicialização
_reset_game()
├── self._initialize_game()
└── self._state = GameState.PLAYING

_reset_positions()
├── player_pos = self._map.get_spawn_position("player")
├── self._player.position = player_pos
└── for ghost in self._ghosts:
    └── ghost.reset_position()
``` 