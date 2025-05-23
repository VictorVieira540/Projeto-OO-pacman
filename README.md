# Pacman POO

Um jogo do Pacman desenvolvido em Python usando programação orientada a objetos.

## Requisitos

- Python 3.8 ou superior
- Pygame 2.5.2

## Instalação

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/pacman-poo.git
cd pacman-poo
```

2. Crie um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Executando o jogo

```bash
python src/main.py
```

## Controles

- Setas direcionais: Movimentar o Pacman
- ENTER: Selecionar opção no menu
- ESPAÇO: Voltar ao menu principal
- ESC: Sair do jogo

## Funcionalidades

- Menu inicial com música de fundo
- Sistema de pontuação
- Recordes
- Configurações de volume
- Fantasmas com comportamentos diferentes
- Labirinto com paredes e comida
- Sistema de vidas
- Game over

## Estrutura do Projeto

```
pacman-poo/
├── src/
│   ├── main.py
│   ├── game.py
│   ├── player.py
│   ├── ghost.py
│   ├── maze.py
│   ├── score.py
│   └── menu.py
├── assets/
│   ├── sprites/
│   └── sounds/
├── requirements.txt
└── README.md
```

## Desenvolvimento

Este projeto foi desenvolvido como um trabalho de Programação Orientada a Objetos, utilizando os seguintes conceitos:

- Classes e Objetos
- Herança
- Encapsulamento
- Polimorfismo
- Tratamento de Exceções
- Sobrecarga de Operadores
- Tipagem Estática
- Documentação de Código

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

# Roteiro de Desenvolvimento: Versão do Pac-Man em Python (Orientado a Objetos)

## 1. Definição de Requisitos

### Funcionalidades Mínimas
1. Labirinto com paredes e caminhos
2. Pac-Man que se move em quatro direções (cima, baixo, esquerda e direita)
3. Pellets (bolinhas) espalhados pelo labirinto
4. Fantasmas com IA simples
5. Sistema de pontuação, vidas e condições de fim de jogo

### Extras Opcionais
- Power-ups (pellets maiores) que deixam fantasmas vulneráveis
- Sons e música de fundo
- Animações: abertura/fechamento da boca do Pac-Man e morte dos fantasmas
- Múltiplas fases

---

## 2. Configuração do Ambiente

1. Instalar **Python** (versão ≥ 3.8)
2. Instalar **Pygame**:
   ```bash
   pip install pygame
   ```
3. Estrutura de pastas inicial:
   ```plaintext
   pacman/
   ├── assets/       # imagens e sons
   ├── src/          # código-fonte
   │   ├── main.py
   │   ├── game.py
   │   ├── player.py
   │   ├── ghost.py
   │   ├── map.py
   │   └── pellet.py
   └── README.md
   ```

## 3. Projeto de Classes (UML Simplificado)

- **Game**
    - **Responsabilidade:** Loop principal e estados (menu, jogando, game over)
    - **Atributos Principais:** `estado`, `tela`, `clock`
    - **Métodos Principais:** `run()`, `process_events()`, `render()`

- **Map**
    - **Responsabilidade:** Carregar layout do labirinto e renderizar paredes e caminhos
    - **Atributos Principais:** `layout` (matriz 2D)
    - **Métodos Principais:** `load_map()`, `draw()`

- **Player**
    - **Responsabilidade:** Lógica do Pac-Man: movimento, comer pellets, vidas, pontuação
    - **Atributos Principais:** `posição`, `direção`, `velocidade`, `vidas`
    - **Métodos Principais:** `move()`, `eat_pellet()`, `draw()`

- **Pellet**
    - **Responsabilidade:** Representar bolinha normal ou power-up
    - **Atributos Principais:** `posição`, `tipo` (normal/vulnerável)
    - **Métodos Principais:** `draw()`, `be_eaten()`

- **Ghost**
    - **Responsabilidade:** IA simples com estados (normal, vulnerável) e reset de posição
    - **Atributos Principais:** `posição`, `estado`, `velocidade`, `direção`
    - **Métodos Principais:** `move_ai()`, `draw()`, `reset()`

## 4. Desenvolvimento Incremental

1. Loop básico e janela
   - Iniciar Pygame e criar janela
   - Configurar loop de eventos sem lógica do jogo

2. Renderização do labirinto
   - Modelar mapa como matriz 2D (`0` = caminho, `1` = parede)
   - Desenhar retângulos para paredes

3. Movimentação do Pac-Man
   - Capturar entrada do teclado (setas)
   - Atualizar direção e verificar colisões antes de mover

4. Pellets e pontuação
   - Gerar `Pellet` em todas as células de caminho
   - Detectar colisão Pac-Man × Pellet e remover pellet
   - Atualizar pontuação

5. Fantasmas com IA simples
   - Instanciar `Ghost` em posições fixas
   - Movimento aleatório ou perseguição básica (direção livre em direção ao Pac-Man)

6. Colisões Pac-Man × Fantasma
   - Fantasma normal: Pac-Man perde vida e ambos resetam
   - Fantasma vulnerável: fantasma "morre" e volta ao spawn

7. Estados de jogo e HUD
   - Telas: menu inicial, instruções, jogo em andamento, game over e vitória
   - Barra de HUD com pontuação e vidas

8. Power-ups e temporizadores
   - Pellets maiores ativam estado vulnerável dos fantasmas
   - Gerenciar timers para reverter estado

9. Áudio e animações
   - Sons: comer pellet, power-up, perder vida, música de fundo
   - Animações: boca do Pac-Man e morte dos fantasmas

10. Testes e ajustes finais
    - Verificar vidas, game over e vitória
    - Ajustar velocidades, layout e IA
    - Refatorar código (princípios DRY e SOLID)

---

## 5. Documentação e Entrega

- **README.md**: instruções de instalação e execução, visão geral da arquitetura e classes
- Comentários no código: descrição de classes e métodos principais
- **Demonstração** (opcional): vídeo curto mostrando o jogo em ação

> **Dica:**
> - Use grids para simplificar colisões (checando células em vez de pixels)
> - Para IA avançada, pesquise algoritmos como A* ou BFS
> - Mantenha responsabilidade única em cada classe (SRP do SOLID)

