# Pac-Man Orientado a Objetos - Projeto Completo

Um jogo Pac-Man totalmente implementado em Python usando princípios avançados de programação orientada a objetos e a biblioteca Pygame, com **sprites reais 16x16**, **sistema de sons imersivo** e **campanha com múltiplos mapas**!

## 🎮 Características do Projeto

### 🏗️ Conceitos de Orientação a Objetos Implementados:

1. **Encapsulamento**: Atributos privados com getters/setters apropriados
2. **Herança**: Hierarquia clara (GameObject → MovableObject → Player/Ghost)
3. **Abstração**: Classes abstratas e métodos abstratos bem definidos
4. **Polimorfismo**: Métodos draw() e update() específicos para cada classe
5. **Padrões de Design**: Strategy, State Machine, Singleton, Manager

### 🎯 Funcionalidades Implementadas:

- ✅ **Sistema de sons avançado** com categorização (música, efeitos, UI, fantasmas)
- ✅ **Controle de volume individualizado** por tipo de som
- ✅ **Movimento suave** do Pac-Man com detecção de colisões precisa
- ✅ **IA avançada dos fantasmas** com pathfinding A* e múltiplos comportamentos
- ✅ **Sistema de dificuldade baseado em mapas** (0-200 níveis)
- ✅ **Campanha progressiva** através de múltiplos mapas JSON
- ✅ **Sistema de power-ups** com efeitos visuais e vulnerabilidade
- ✅ **Sistema de pontuação e vidas** com histórico persistente
- ✅ **Interface gráfica completa** (Menu, Opções, Histórico, Game Over)
- ✅ **Carregamento dinâmico de mapas** via arquivos JSON


## 🚀 Instalação e Execução

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

## 🎮 Controles

- **Movimento**: WASD ou Setas direcionais
- **Pausa**: ESC (durante o jogo)
- **Menu**: ENTER (para navegar/reiniciar)
- **Navegação de menus**: Setas UP/DOWN, ENTER para confirmar
- **Controle de volume**: Setas LEFT/RIGHT (no menu de opções)

## 📁 Estrutura de Arquivos

```
assets/
├── sprites/
│   ├── pacman/           # Sprites do Pac-Man (16x16)
│   │   ├── pac-fechado.png
│   │   ├── pac-dir.png, pac-dir-ab.png
│   │   ├── pac-esq.png, pac-esq-ab.png
│   │   ├── pac-cima.png, pac-cima-ab.png
│   │   └── pac-baixo.png, pac-baixo-fechado.png
│   ├── ghosts/           # Sprites dos fantasmas (16x16)
│   │   ├── red/, pink/, blue/, yellow/
│   │   └── vulnerable/   # Estados vulneráveis
│   └── itens/
│       └── fruit.png     # Power-ups
├── sounds/               # Sistema de áudio completo
│   ├── music_menu.mp3    # Música do menu
│   ├── start-music.mp3   # Música do jogo
│   ├── eating*.mp3       # Efeitos de comer
│   ├── ghost-*.mp3       # Sons dos fantasmas
│   └── miss.mp3, extend.mp3
└── maps/                 # Mapas JSON da campanha
    ├── default_map.json  # Mapa clássico (dificuldade 50)
    ├── test_map.json     # Mapa de teste (dificuldade 25)
    └── extreme_map.json  # Mapa extremo (dificuldade 200)

src/
├── __init__.py           # Módulo Python
├── utils.py             # Vector2D, Direction, GameState, A*
├── sprite_manager.py    # 🎨 Gerenciador de sprites 16x16
├── sound_manager.py     # 🔊 Sistema de áudio avançado
├── game_objects.py      # Classes dos objetos (Player, Ghost, Pellet)
└── map.py              # Sistema de mapas JSON

examples/
└── map_loader_example.py # Exemplo de criação/validação de mapas

main.py                 # Arquivo principal do jogo
requirements.txt        # Dependências Python
Uml.png                # Diagrama UML da arquitetura
highscores.json        # Persistência de pontuações
```

## 🎨 Sistema de Sprites e Gráficos

### **SpriteManager** - Gerenciamento Avançado
- **Carregamento automático** de todos os sprites 16x16
- **Sistema de animação** para Pac-Man e fantasmas
- **Fallback inteligente** para sprites faltantes
- **Colorização automática** para fantasmas sem sprites específicos

### **Sprites Implementados:**

#### **Pac-Man** (sprites reais):
- Animação de boca baseada na direção de movimento
- Sprites específicos para cada direção (cima, baixo, esquerda, direita)
- Estados aberto/fechado para simular mastigação

#### **Fantasmas** (sprites reais + colorização):
- **Vermelho**: Sprites originais carregados
- **Outros**: Colorização automática dos sprites vermelhos
- **Estados vulneráveis**: Sprites azuis e brancos piscantes
- **Animação**: Alternância entre frames para movimento fluido

#### **Power-ups e Pellets**:
- Power-ups usam sprite de fruta com efeito piscante
- Pellets normais criados proceduralmente
- Efeitos visuais durante power-up ativo

## 🔊 Sistema de Áudio

### **SoundManager** - Controle Avançado
- **Categorização de sons**: Música, Efeitos, UI, Fantasmas
- **Controle de volume individual** por categoria
- **Prevenção de sobreposição** indesejada
- **Canais dedicados** para cada tipo de som

### **Sons Implementados:**
- **Música**: Menu, jogo, créditos
- **Efeitos**: Comer pellets, power-ups, fantasmas
- **Interface**: Navegação, game over, extend
- **Fantasmas**: Movimento normal, vulnerável, retorno

## 🗺️ Sistema de Mapas

### **Carregamento Dinâmico via JSON**
- **Metadados completos**: Nome, autor, descrição, dificuldade
- **Layout configurável**: Paredes, pellets, power-ups, spawn points
- **Validação automática** de estrutura e consistência
- **Sistema de campanha** com progressão entre mapas

### **Formato do Mapa JSON:**
```json
{
  "metadata": {
    "name": "Nome do Mapa",
    "difficulty": 50,
    "description": "Descrição do mapa"
  },
  "spawn_positions": {
    "player": {"x": 1, "y": 1},
    "ghost_red": {"x": 17, "y": 9}
  },
  "layout": [
    [1, 2, 2, 3],  // 1=parede, 2=pellet, 3=power-up, 0=vazio
    [1, 2, 1, 2]
  ]
}
```

## 🤖 Sistema de IA dos Fantasmas

### **Pathfinding A*** 
- **Algoritmo A*** para encontrar caminhos otimizados
- **Heurísticas configuráveis** (Manhattan, Euclidiana, Diagonal)
- **Evita colisões** com paredes e outros fantasmas
- **Recálculo dinâmico** baseado na dificuldade do mapa

### **Comportamentos dos Fantasmas:**
- **Patrol Mode**: Patrulhamento em rotas específicas por tipo
- **Chase Mode**: Perseguição ativa do jogador
- **Vulnerable Mode**: Comportamento defensivo quando comível
- **Difficulty Scaling**: Velocidade e agressividade baseada no mapa

### **Personalidades Únicas:**
- **Vermelho**: Patrulha ampla e dominante
- **Rosa**: Movimento em S suave
- **Ciano**: Patrulha tática em L
- **Laranja**: Movimento errático e imprevisível

## 🎯 Sistema de Dificuldade

### **Baseado em Mapas (0-200):**
- **0-24**: MUITO FÁCIL - Fantasmas lentos, longos períodos vulneráveis
- **25-49**: FÁCIL+ - Comportamento básico
- **50-74**: MÉDIO - Dificuldade equilibrada
- **75-99**: MÉDIO+ - Maior agressividade
- **100-124**: DIFÍCIL - IA mais inteligente
- **125-149**: DIFÍCIL+ - Pathfinding frequente
- **150-174**: MUITO DIFÍCIL - Extremamente agressivo
- **175-200**: EXTREMO - Fantasmas implacáveis

### **Efeitos da Dificuldade:**
- **Frequência de pathfinding**: De 2000ms (fácil) a 200ms (extremo)
- **Duração de vulnerabilidade**: De 8s (fácil) a 1s (extremo)
- **Timing de modos**: Menos patrol, mais chase em dificuldades altas

## 📊 Classes Principais

### **GameObject** (Abstrata)
- Classe base para todos os objetos do jogo
- Controle de posição, cor, tamanho e animação
- Interface comum (draw, update, get_rect)

### **MovableObject** (Herda de GameObject)
- Adiciona capacidade de movimento e direção
- Sistema de detecção de colisões otimizado
- Suporte para diferentes tipos de entidade

### **Player** (Herda de MovableObject)
- Implementa o Pac-Man com sprites e animação
- Sistema de vidas, pontuação e power-ups
- Controles responsivos e movimento fluido

### **Ghost** (Herda de MovableObject)
- IA com pathfinding A* e múltiplos comportamentos
- Estados vulnerável/normal com sprites específicos
- Sistema de dificuldade adaptativa por mapa

### **Pellet** (Herda de GameObject)
- Pontos coletáveis com diferentes tipos e valores
- Efeitos visuais (piscante para power-ups)

### **Map**
- Carregamento dinâmico de mapas JSON
- Sistema de spawn points configurável
- Controle de layout e elementos do mapa

### **SpriteManager** (Singleton)
- Carregamento e cache de todos os sprites
- Sistema de animação e fallbacks
- Otimização de performance

### **SoundManager** (Singleton)
- Controle completo do sistema de áudio
- Categorização e volumes individuais
- Prevenção de sobreposição sonora

## 🎮 Estados do Jogo

- **MENU**: Tela inicial com opções
- **PLAYING**: Jogo ativo
- **PAUSED**: Jogo pausado
- **GAME_OVER**: Fim de jogo com input de nome
- **VICTORY**: Vitória na campanha
- **OPTIONS**: Configurações de volume
- **HISTORY**: Histórico de pontuações
- **INTERMISSION**: Transição entre mapas

## 🏆 Sistema de Pontuação

- **Pellets normais**: 10 pontos cada
- **Power-ups**: 50 pontos cada
- **Fantasmas vulneráveis**: Pontuação progressiva
- **Persistência**: Salvamento automático em JSON
- **Top 10**: Ranking dos melhores jogadores

## 🛠️ Tecnologias e Padrões

- **Python 3.7+**
- **Pygame 2.5+**
- **Programação Orientada a Objetos**
- **Padrões de Design**: Singleton, Strategy, State Machine
- **Algoritmos**: A* Pathfinding, Collision Detection
- **Formato JSON**: Para mapas e configurações
- **Sprites 16x16**: PNG com transparência

## 📈 Melhorias Técnicas

### **Performance:**
- Sprites carregados uma vez na inicialização
- Cache inteligente de pathfinding
- Detecção de colisões otimizada por tipo de entidade

### **Manutenibilidade:**
- Código modular e bem documentado
- Separação clara entre lógica e apresentação
- Sistema de fallbacks para robustez

### **Extensibilidade:**
- Sistema de mapas JSON facilmente extensível
- IA configurável e ajustável
- Sistema de sons plugável

## 🎯 Como Executar:

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar o jogo
python main.py

# Testar sistema de mapas (opcional)
python examples/map_loader_example.py
```

## 🎉 Principais Conquistas

- ✅ **Arquitetura OO robusta** com todos os conceitos implementados
- ✅ **Sistema completo de jogo** com progressão e persistência
- ✅ **IA avançada** com pathfinding A* e comportamentos únicos
- ✅ **Sistema de áudio imersivo** com controle granular
- ✅ **Interface profissional** com múltiplas telas e navegação
- ✅ **Sistema de mapas flexível** com carregamento dinâmico
- ✅ **Performance otimizada** para experiência fluida

---

**🚀 Resultado**: Um jogo Pac-Man completo e profissional que demonstra domínio total dos conceitos de Programação Orientada a Objetos, com arquitetura extensível, performance otimizada e experiência de usuário polida! 