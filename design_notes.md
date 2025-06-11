# Notas de Design para o Projeto Pac-Man (Orientado a Objetos)

## 1. Esboço das Classes Principais e Suas Responsabilidades

### Game
**Responsabilidade:** Gerenciar o loop principal do jogo, os estados (menu, jogando, game over), a tela e o tempo. Atua como o orquestrador principal, coordenando as interações entre as outras classes.
**Atributos Principais:** `estado` (enum: MENU, PLAYING, GAME_OVER), `tela` (objeto Pygame.Surface), `clock` (objeto Pygame.time.Clock).
**Métodos Principais:** `run()` (inicia o loop do jogo), `process_events()` (lida com entradas do usuário), `update()` (atualiza o estado do jogo), `render()` (desenha os elementos na tela).

### Map
**Responsabilidade:** Carregar o layout do labirinto a partir de um arquivo ou estrutura de dados, e renderizar as paredes e caminhos na tela. Também pode fornecer métodos para verificar colisões com paredes.
**Atributos Principais:** `layout` (matriz 2D representando o labirinto), `tamanho_celula`.
**Métodos Principais:** `load_map()` (carrega o layout do labirinto), `draw()` (desenha o labirinto), `is_wall(x, y)` (verifica se uma posição é uma parede).

### GameObject (Classe Abstrata)
**Responsabilidade:** Servir como a classe base para todos os objetos que existem no jogo (Pac-Man, fantasmas, pellets). Define uma interface comum para propriedades e comportamentos básicos.
**Atributos Principais:** `posicao` (tupla ou vetor), `cor`, `tamanho`.
**Métodos Principais:** `draw()` (método abstrato para desenhar o objeto), `update()` (método abstrato para atualizar o estado do objeto).
**Conceito OO:** Classe Abstrata, Herança.

### MovableObject (Classe Base)
**Responsabilidade:** Estender `GameObject` para incluir propriedades e comportamentos comuns a objetos que se movem no jogo (Pac-Man, fantasmas).
**Atributos Principais:** `velocidade`, `direcao` (enum: CIMA, BAIXO, ESQUERDA, DIREITA, NENHUMA).
**Métodos Principais:** `move()` (atualiza a posição com base na velocidade e direção), `set_direction()`.
**Conceito OO:** Herança.

### Player (Herda de MovableObject)
**Responsabilidade:** Lógica específica do Pac-Man: movimento controlado pelo jogador, comer pellets, gerenciar vidas e pontuação.
**Atributos Principais:** `vidas`, `pontuacao`, `power_up_ativo`.
**Métodos Principais:** `eat_pellet()` (lógica para comer pellets e power-ups), `lose_life()`.
**Conceito OO:** Herança, Polimorfismo (no `draw()` e `update()`).

### Pellet (Herda de GameObject)
**Responsabilidade:** Representar as bolinhas que o Pac-Man come. Pode ter diferentes tipos (normal, power-up).
**Atributos Principais:** `tipo` (enum: NORMAL, POWER_UP), `valor_pontuacao`.
**Métodos Principais:** `be_eaten()` (lógica quando é comido).
**Conceito OO:** Herança, Polimorfismo (no `draw()`).

### Ghost (Herda de MovableObject)
**Responsabilidade:** Lógica dos fantasmas: IA simples (movimento autônomo), estados (normal, vulnerável, caça), e reset de posição.
**Atributos Principais:** `estado` (enum: NORMAL, VULNERAVEL, CAÇA), `posicao_inicial`.
**Métodos Principais:** `move_ai()` (lógica de movimento da IA), `reset_position()`.
**Conceito OO:** Herança, Polimorfismo (no `draw()` e `update()`).

## 2. Aplicação de Conceitos de Orientação a Objetos

### Herança
- `GameObject` será a classe base abstrata para todos os elementos visuais do jogo.
- `MovableObject` herdará de `GameObject` e adicionará funcionalidades de movimento.
- `Player` e `Ghost` herdarão de `MovableObject`, reutilizando a lógica de movimento e adicionando comportamentos específicos.
- `Pellet` herdará diretamente de `GameObject`, pois não é um objeto móvel no mesmo sentido.

### Polimorfismo
- O método `draw()` será definido em `GameObject` como abstrato e implementado de forma diferente em `Player`, `Ghost`, `Pellet` e `Map` (embora `Map` não herde de `GameObject`, terá um método `draw()` com propósito similar).
- O método `update()` também será polimórfico para `Player` e `Ghost`, permitindo que o loop do jogo chame `objeto.update()` sem saber o tipo exato do objeto.

### Classes Abstratas
- `GameObject` será uma classe abstrata (usando `abc` module do Python) para garantir que `draw()` e `update()` sejam implementados pelas subclasses. Isso força uma interface comum para todos os objetos do jogo.

### Sobrecarga de Operadores
- **Posições:** Podemos criar uma classe `Vector2D` ou similar para representar posições e direções. Esta classe pode sobrecarregar operadores como `__add__` (para somar vetores de posição e movimento) e `__eq__` (para comparar se duas posições são iguais).
- **Colisões:** Embora não seja uma sobrecarga de operador direta, a lógica de colisão pode se beneficiar de métodos especiais que simulam comparações ou intersecções entre objetos.

## 3. Estrutura de Módulos (Arquivos Python)

- `main.py`: Contém a classe `Game` e o ponto de entrada do jogo.
- `game_objects.py`: Contém as classes `GameObject`, `MovableObject`, `Player`, `Pellet`, `Ghost`.
- `map.py`: Contém a classe `Map`.
- `utils.py`: Contém classes auxiliares como `Vector2D` (para sobrecarga de operadores) e enums para direções e estados.

Esta estrutura visa organizar o código de forma modular e clara, facilitando a aplicação dos princípios de OO.



## 4. Aplicação de Encapsulamento

O encapsulamento será aplicado em todas as classes para proteger os dados internos e expor apenas o necessário através de métodos públicos (getters e setters, quando apropriado, ou métodos que manipulam os dados internamente).

- **Atributos Privados/Protegidos:** Atributos que representam o estado interno de um objeto (ex: `_posicao`, `_vidas`, `_estado`) serão tratados como privados ou protegidos por convenção em Python (prefixo com um ou dois underscores).
- **Métodos Públicos:** A interação com os objetos será feita através de métodos públicos que controlam o acesso e a modificação desses atributos (ex: `get_posicao()`, `set_direcao()`, `move()`, `eat_pellet()`).
- **Propriedades (Properties):** Para atributos que precisam de validação ou lógica adicional ao serem acessados ou modificados, serão utilizadas as `@property` do Python, que permitem controlar o acesso a atributos como se fossem públicos, mas com lógica interna.

O encapsulamento garantirá que a complexidade interna de cada classe seja escondida, promovendo a modularidade e facilitando a manutenção e evolução do código.

