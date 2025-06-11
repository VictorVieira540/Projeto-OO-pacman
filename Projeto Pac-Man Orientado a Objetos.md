# Projeto Pac-Man Orientado a Objetos

Este projeto demonstra a aplicação de conceitos de Programação Orientada a Objetos (POO) em Python, utilizando como base a estrutura de um jogo Pac-Man simplificado. O foco principal não é o desenvolvimento de um jogo completo e jogável, mas sim a exemplificação de princípios como Herança, Polimorfismo, Classes Abstratas, Encapsulamento e Sobrecarga de Operadores.

## Estrutura do Projeto

O projeto está organizado na seguinte estrutura de diretórios:

```
pacman_game/
├── src/
│   ├── __init__.py
│   ├── game_objects.py
│   ├── map.py
│   └── utils.py
├── main.py
└── design_notes.md
└── README.md
```

- `main.py`: Contém a classe `Game`, que gerencia o loop principal do jogo, os estados e a interação entre os objetos.
- `src/game_objects.py`: Define as classes relacionadas aos objetos do jogo, como `GameObject` (abstrata), `MovableObject`, `Player`, `Ghost` e `Pellet`.
- `src/map.py`: Contém a classe `Map`, responsável por carregar e renderizar o labirinto.
- `src/utils.py`: Inclui classes e enums auxiliares, como `Vector2D` (para manipulação de posições e sobrecarga de operadores) e `Direction`.
- `design_notes.md`: Documento detalhando o planejamento e o design das classes, incluindo a aplicação dos conceitos de POO.
- `README.md`: Este arquivo, explicando a estrutura do projeto e os conceitos de OO aplicados.

## Conceitos de Orientação a Objetos Aplicados

### 1. Encapsulamento

O encapsulamento é aplicado em todas as classes para proteger os dados internos e controlar o acesso a eles. Atributos que representam o estado interno de um objeto (ex: `_position`, `_lives`, `_state`) são definidos como protegidos (por convenção, prefixados com um underscore `_`). O acesso e a modificação desses atributos são realizados através de métodos públicos ou propriedades (`@property`).

**Exemplos:**
- Na classe `GameObject`, `_position`, `_color` e `_size` são atributos protegidos, acessíveis via propriedades `position`, `color` e `size`.
- Na classe `Player`, `_lives` e `_score` são protegidos, com acesso via propriedades `lives` e `score` e métodos como `lose_life()` e `eat_pellet()`.

### 2. Herança

A herança é utilizada para estabelecer uma hierarquia de classes, permitindo a reutilização de código e a especialização de comportamentos.

- `GameObject`: É a classe base abstrata para todos os elementos visuais e interativos do jogo. Define uma interface comum para `draw()` e `update()`.
- `MovableObject`: Herda de `GameObject` e adiciona funcionalidades de movimento, como `_speed` e `_direction`, e o método `move()`.
- `Player` e `Ghost`: Herdam de `MovableObject`, especializando o comportamento de movimento e adicionando atributos e métodos específicos (ex: `lives` e `eat_pellet()` para `Player`; `state` e `move_ai()` para `Ghost`).
- `Pellet`: Herda diretamente de `GameObject`, pois não possui lógica de movimento complexa como os `MovableObject`.

### 3. Polimorfismo

O polimorfismo é demonstrado através da capacidade de diferentes classes responderem ao mesmo método de maneiras distintas, dependendo de sua implementação específica.

- Os métodos `draw()` e `update()` são definidos como abstratos em `GameObject`. Isso força todas as subclasses (`Player`, `Ghost`, `Pellet`) a fornecerem suas próprias implementações desses métodos. No loop principal do jogo, é possível iterar sobre uma lista de `GameObject`s e chamar `objeto.draw(screen)` ou `objeto.update(delta_time)` sem precisar saber o tipo exato de cada objeto.

### 4. Classes Abstratas

A classe `GameObject` é definida como uma classe abstrata usando o módulo `abc` do Python (`ABC` e `@abstractmethod`). Isso garante que ela não pode ser instanciada diretamente e que suas subclasses devem implementar os métodos abstratos `draw()` e `update()`. Isso impõe uma estrutura e uma interface comum para todos os objetos do jogo.

### 5. Sobrecarga de Operadores

A sobrecarga de operadores é utilizada para permitir que objetos de classes personalizadas respondam a operadores padrão do Python (como `+`, `-`, `==`) de maneira significativa.

- `Vector2D`: Uma classe auxiliar foi criada para representar coordenadas 2D. Ela sobrecarrega os operadores:
    - `__add__`: Permite somar dois objetos `Vector2D` ou um `Vector2D` com uma tupla, facilitando o cálculo de novas posições.
    - `__sub__`: Permite subtrair dois objetos `Vector2D` ou um `Vector2D` de uma tupla, útil para calcular distâncias ou vetores de direção.
    - `__eq__`: Permite comparar se dois objetos `Vector2D` ou um `Vector2D` e uma tupla são iguais em valor, simplificando verificações de posição.

## Como Executar (Requer Pygame)

1.  Certifique-se de ter o Python instalado.
2.  Instale a biblioteca Pygame:
    ```bash
    pip install pygame
    ```
3.  Navegue até o diretório `pacman_game` no terminal.
4.  Execute o arquivo `main.py`:
    ```bash
    python main.py
    ```

**Nota:** Este projeto é uma demonstração dos princípios de POO. A interface gráfica e a jogabilidade são simplificadas, e algumas funcionalidades podem não estar totalmente implementadas para manter o foco nos conceitos de Orientação a Objetos.

