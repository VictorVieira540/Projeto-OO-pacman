# Instruções para Ajuste de Sprites do Pac-Man

Este documento contém instruções detalhadas sobre como extrair e configurar os sprites para o jogo Pac-Man a partir da spritesheet principal.

## Pré-requisitos

- Python 3.9+ instalado
- Pygame instalado (`pip install pygame`)
- Uma cópia do projeto Pac-Man baixada

## Ferramentas Disponíveis

O projeto contém as seguintes ferramentas para trabalhar com sprites:

1. `sprite_identifier.py` - Ferramenta para identificar e extrair coordenadas dos sprites
2. `sprite_manager.py` - Classe para gerenciar os sprites no jogo
3. `sprite_viewer.py` - Ferramenta para visualizar os sprites recortados

## Passo 1: Identificar as Coordenadas dos Sprites

Execute a ferramenta de identificação de sprites:

```bash
python src/sprite_identifier.py
```

### Como Usar o Identificador de Sprites:

1. **Navegação na imagem:**
   - Arraste com o mouse para mover a visualização
   - Use a roda do mouse para aumentar/diminuir o zoom
   - Pressione `G` para ativar/desativar a grade
   - Use `+` e `-` para ajustar o tamanho da grade

2. **Selecionar um sprite:**
   - Mantenha a tecla `SHIFT` pressionada e clique para iniciar a seleção
   - Arraste até completar a área do sprite
   - Solte o botão do mouse para finalizar a seleção
   - Digite um nome descritivo para o sprite (sugestão de formato abaixo)
   - Pressione `ENTER` para confirmar

3. **Nomenclatura recomendada para sprites:**
   - `pacman_direção_frame` (ex: `pacman_right_1`, `pacman_left_2`)
   - `ghost_cor_direção_frame` (ex: `ghost_red_right_1`)
   - `fruit_nome` (ex: `fruit_cherry`, `fruit_strawberry`)
   - `pellet_tipo` (ex: `pellet_small`, `pellet_power`)

4. **Atalhos úteis:**
   - `CTRL+Z` para desfazer a última seleção
   - `CTRL+S` para salvar todas as coordenadas
   - `ESC` para cancelar a seleção atual ou sair

5. **Salvar coordenadas:**
   - Após selecionar todos os sprites necessários, pressione `CTRL+S`
   - Isso criará um arquivo `sprite_coordinates.py` no diretório `src`

## Passo 2: Verificar as Coordenadas

Abra o arquivo `sprite_coordinates.py` gerado e confirme se as coordenadas estão corretas. O arquivo deve conter estruturas como:

```python
pacman_sprites = {
    'right': [
        (0, 0, 16, 16),  # pacman_right_1
        (16, 0, 16, 16),  # pacman_right_2
        # ...
    ],
    # ...
}
```

## Passo 3: Integrar com o SpriteManager

Abra o arquivo `sprite_manager.py` e atualize os métodos para usar as coordenadas extraídas:

1. Importe o arquivo de coordenadas no topo:

```python
from sprite_coordinates import pacman_sprites, ghost_sprites, fruit_sprites, pellet_sprites, all_sprites
```

2. Atualize os métodos como `get_pacman_sprites()`, `get_ghost_sprites()`, etc. para usar as coordenadas importadas.

## Passo 4: Testar os Recortes

Execute o visualizador de sprites para confirmar que os recortes estão corretos:

```bash
python src/sprite_viewer.py
```

Certifique-se de que:
- Todos os sprites aparecem corretamente posicionados
- Não há artefatos ou cortes indesejados
- A animação dos sprites parece fluida quando exibida em sequência

## Dicas Importantes para o Ajuste de Sprites

1. **Dimensões consistentes:**
   - Mantenha todos os sprites do mesmo tipo com as mesmas dimensões
   - Pacman e fantasmas geralmente são quadrados (ex: 16x16 pixels)
   - Frutas e power pellets podem variar, mas mantenha proporção

2. **Pixels transparentes:**
   - A ferramenta já lida com transparência automaticamente
   - Certifique-se de que a área selecionada não inclui partes de outros sprites

3. **Animação:**
   - Para sprites animados (como Pacman abrindo e fechando a boca), selecione cada frame separadamente
   - Mantenha a ordem dos frames consistente (ex: boca aberta → meio aberta → fechada)

4. **Organização:**
   - Organize os sprites por tipo (pacman, fantasmas, frutas, etc.)
   - Use a nomenclatura sugerida para facilitar a identificação

## Resolução de Problemas

Se os sprites não aparecem corretamente:

1. **Coordenadas incorretas:**
   - Verifique se as coordenadas no arquivo `sprite_coordinates.py` estão corretas
   - Use o identificador de sprites para refazer a seleção se necessário

2. **Problemas de transparência:**
   - Confirme se a spritesheet tem um canal alfa (transparência)
   - O fundo da spritesheet deve ser transparente ou de uma cor única

3. **Sprites não carregados:**
   - Verifique o caminho correto para a spritesheet
   - Confirme que os métodos no `sprite_manager.py` estão corretos
   
## Contato para Suporte

Se você tiver problemas que não consegue resolver, entre em contato com o desenvolvedor responsável pela implementação do spritesheet.

---

Boa sorte com o ajuste dos sprites! Esta é uma etapa fundamental para termos um jogo Pac-Man com aparência profissional e autêntica.