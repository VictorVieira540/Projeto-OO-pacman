# Pac-Man Orientado a Objetos

Jogo Pac-Man implementado em Python usando Pygame com princípios de programação orientada a objetos.

## Instalação e Execução

### Pré-requisitos:
```bash
pip install pygame>=2.5.0
```

Ou usar o arquivo requirements.txt:
```bash
pip install -r requirements.txt
```

### Executar o jogo:
```bash
python main.py
```

## Controles

- **Movimento**: WASD ou Setas direcionais
- **Pausa**: ESC
- **Menu**: ENTER
- **Navegação**: Setas UP/DOWN, ENTER para confirmar

## Estrutura de Arquivos

```
assets/
├── sprites/         # Sprites do jogo
├── sounds/          # Sistema de áudio
└── maps/            # Mapas JSON

src/
├── utils.py         # Vector2D, Direction, GameState, A*
├── sprite_manager.py # Gerenciador de sprites
├── sound_manager.py # Sistema de áudio
├── game_objects.py  # Classes dos objetos
└── map.py          # Sistema de mapas

main.py             # Arquivo principal
requirements.txt    # Dependências
```

## Funcionalidades

- Sistema de movimento fluido
- IA dos fantasmas com pathfinding A*
- Sistema de áudio completo
- Carregamento dinâmico de mapas
- Sistema de pontuação e vidas
- Interface gráfica (Menu, Opções, Game Over)

## Classes Principais

- **GameObject**: Classe base abstrata
- **MovableObject**: Adiciona movimento
- **Player**: Implementa o Pac-Man
- **Ghost**: IA dos fantasmas
- **Pellet**: Pontos coletáveis
- **Map**: Carregamento de mapas
- **SpriteManager**: Gerenciamento de sprites
- **SoundManager**: Controle de áudio 