import pygame
import sys
import os
import constantes
from sprite_manager import SpriteManager
from game import Game

class Menu:
    def __init__(self):
        # Inicialização do Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Configuração da tela
        self.tela = pygame.display.set_mode((constantes.LARGURA, constantes.ALTURA))
        pygame.display.set_caption(constantes.TITULO_JOGO)
        
        # Relógio para controlar o FPS
        self.relogio = pygame.time.Clock()
        
        # Carregando as fontes
        self.fonte_titulo = pygame.font.Font(None, 60)
        self.fonte_menu = pygame.font.Font(None, 36)
        
        # Carregando sons
        self.diretorio_sons = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sounds')
        try:
            self.som_selecao = pygame.mixer.Sound(os.path.join(self.diretorio_sons, 'credit.mp3'))
            self.som_confirmacao = pygame.mixer.Sound(os.path.join(self.diretorio_sons, 'eating-fruit.mp3'))
        except pygame.error as e:
            print(f"Erro ao carregar sons: {e}")
            self.som_selecao = None
            self.som_confirmacao = None
        
        # Carregando sprites através do SpriteManager
        self.game_directory = os.path.join(os.path.dirname(__file__), '..')
        self.sprite_manager = SpriteManager(self.game_directory)
        self.pacman_sprites = self.sprite_manager.get_pacman_sprites()
        self.frame_atual = 0
        self.tempo_animacao = 0
        
        # Itens do menu
        self.opcoes_menu = ["JOGAR", "INSTRUÇÕES", "CRÉDITOS", "SAIR"]
        self.indice_selecao = 0
        
        # Cores
        self.cor_titulo = constantes.AMARELO
        self.cor_selecao = constantes.AMARELO
        self.cor_padrao = constantes.BRANCO
        
        # Flags de estado
        self.executando = True
        
        # Efeito de pulsação para o item selecionado
        self.tamanho_pulsacao = 0
        self.aumentando = True
        
        # Carregar música de fundo
        try:
            pygame.mixer.music.load(os.path.join(self.diretorio_sons, 'start-music.mp3'))
            pygame.mixer.music.set_volume(0.5)
        except pygame.error as e:
            print(f"Erro ao carregar música: {e}")

    def desenhar_texto(self, texto, fonte, cor, x, y):
        superficie_texto = fonte.render(texto, True, cor)
        rect_texto = superficie_texto.get_rect()
        rect_texto.midtop = (x, y)
        self.tela.blit(superficie_texto, rect_texto)
        return rect_texto

    def desenhar_pacman(self, x, y):
        # Atualiza a animação do Pac-Man
        self.tempo_animacao += 1
        if self.tempo_animacao > 5:  # Ajuste este valor para controlar a velocidade da animação
            self.frame_atual = (self.frame_atual + 1) % 3
            self.tempo_animacao = 0
        
        # Usa os sprites reais do Pac-Man
        # Alterna entre as direções a cada seleção para criar um efeito mais dinâmico
        direcoes = ['right', 'down', 'left', 'up']
        direcao_atual = direcoes[self.indice_selecao % len(direcoes)]
        
        if direcao_atual in self.pacman_sprites and len(self.pacman_sprites[direcao_atual]) > 0:
            # Extrai o sprite correto da animação
            pacman_img = self.pacman_sprites[direcao_atual][self.frame_atual]
            
            # Aumenta o tamanho do sprite para ficar mais visível no menu
            pacman_img = self.sprite_manager.scale_sprite(pacman_img, 2.0)
            
            # Posicionando o Pac-Man ao lado da opção selecionada
            rect_pacman = pacman_img.get_rect()
            rect_pacman.midright = (x - 10, y)
            self.tela.blit(pacman_img, rect_pacman)

    def executar_menu(self):
        pygame.mixer.music.play(-1)  # Loop infinito para a música de fundo
        
        while self.executando:
            self.relogio.tick(constantes.FPS)
            
            # Processando eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.executando = False
                    pygame.quit()
                    sys.exit()
                
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_UP:
                        if self.som_selecao:
                            self.som_selecao.play()
                        self.indice_selecao = (self.indice_selecao - 1) % len(self.opcoes_menu)
                    elif evento.key == pygame.K_DOWN:
                        if self.som_selecao:
                            self.som_selecao.play()
                        self.indice_selecao = (self.indice_selecao + 1) % len(self.opcoes_menu)
                    elif evento.key == pygame.K_RETURN:
                        if self.som_confirmacao:
                            self.som_confirmacao.play()
                        self.processar_opcao_selecionada()
            
            # Atualizando o efeito de pulsação
            if self.aumentando:
                self.tamanho_pulsacao += 0.5
                if self.tamanho_pulsacao >= 5:
                    self.aumentando = False
            else:
                self.tamanho_pulsacao -= 0.5
                if self.tamanho_pulsacao <= 0:
                    self.aumentando = True
            
            # Renderizando a tela
            self.renderizar()
    
    def renderizar(self):
        # Limpar a tela com a cor preta
        self.tela.fill(constantes.PRETO)
        
        # Desenhar o título
        self.desenhar_texto("PAC-MAN", self.fonte_titulo, self.cor_titulo, constantes.LARGURA // 2, 80)
        
        # Desenhar os itens do menu
        espaco_y = 80
        posicao_y_inicial = 200
        
        for i, opcao in enumerate(self.opcoes_menu):
            posicao_y = posicao_y_inicial + i * espaco_y
            
            if i == self.indice_selecao:
                # Desenha o Pac-Man ao lado da opção selecionada
                self.desenhar_pacman(constantes.LARGURA // 2 - 80, posicao_y + 18)
                
                # Aumenta o tamanho da fonte para a opção selecionada com efeito de pulsação
                fonte_selecionada = pygame.font.Font(None, 36 + int(self.tamanho_pulsacao))
                self.desenhar_texto(opcao, fonte_selecionada, self.cor_selecao, constantes.LARGURA // 2, posicao_y)
            else:
                self.desenhar_texto(opcao, self.fonte_menu, self.cor_padrao, constantes.LARGURA // 2, posicao_y)
        
        # Desenhar instruções de controle na parte inferior
        self.desenhar_texto("Use as setas ↑↓ para navegar e ENTER para selecionar", 
                           pygame.font.Font(None, 20), self.cor_padrao, constantes.LARGURA // 2, constantes.ALTURA - 50)
        
        # Atualizar a tela
        pygame.display.flip()
    
    def processar_opcao_selecionada(self):
        if self.indice_selecao == 0:  # JOGAR
            print("Iniciando o jogo...")
            # Aqui você chamaria a função para iniciar o jogo
            self.iniciar_jogo()
        elif self.indice_selecao == 1:  # INSTRUÇÕES
            print("Mostrando instruções...")
            self.mostrar_instrucoes()
        elif self.indice_selecao == 2:  # CRÉDITOS
            print("Mostrando créditos...")
            self.mostrar_creditos()
        elif self.indice_selecao == 3:  # SAIR
            print("Saindo do jogo...")
            self.executando = False
            pygame.quit()
            sys.exit()
    
    def iniciar_jogo(self):
        # Aqui você pode iniciar o jogo real
        pygame.mixer.music.stop()
        # Por exemplo, chamar uma instância do jogo de principal.py
        # from assets.principal import Game
        # game = Game()
        # game.novo_jogo()
        print("Jogo iniciado!")
    
    def mostrar_instrucoes(self):
        mostrando_instrucoes = True
        
        while mostrando_instrucoes and self.executando:
            self.relogio.tick(constantes.FPS)
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    mostrando_instrucoes = False
                    self.executando = False
                    pygame.quit()
                    sys.exit()
                
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_RETURN:
                        mostrando_instrucoes = False
            
            # Limpar a tela
            self.tela.fill(constantes.PRETO)
            
            # Desenhar o título
            self.desenhar_texto("INSTRUÇÕES", self.fonte_titulo, self.cor_titulo, constantes.LARGURA // 2, 80)
            
            # Desenhar as instruções
            instrucoes = [
                "Use as teclas de seta para mover o Pac-Man",
                "Coma todas as pílulas para passar de fase",
                "Evite os fantasmas a menos que tenha comido",
                "uma pílula de poder",
                "Coma frutas para pontos extras"
            ]
            
            espaco_y = 50
            posicao_y_inicial = 180
            
            for i, linha in enumerate(instrucoes):
                posicao_y = posicao_y_inicial + i * espaco_y
                self.desenhar_texto(linha, self.fonte_menu, self.cor_padrao, constantes.LARGURA // 2, posicao_y)
            
            # Desenhar instrução para voltar
            self.desenhar_texto("Pressione ESC ou ENTER para voltar", 
                               pygame.font.Font(None, 24), self.cor_padrao, constantes.LARGURA // 2, constantes.ALTURA - 50)
            
            # Atualizar a tela
            pygame.display.flip()
    
    def mostrar_creditos(self):
        mostrando_creditos = True
        
        while mostrando_creditos and self.executando:
            self.relogio.tick(constantes.FPS)
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    mostrando_creditos = False
                    self.executando = False
                    pygame.quit()
                    sys.exit()
                
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_RETURN:
                        mostrando_creditos = False
            
            # Limpar a tela
            self.tela.fill(constantes.PRETO)
            
            # Desenhar o título
            self.desenhar_texto("CRÉDITOS", self.fonte_titulo, self.cor_titulo, constantes.LARGURA // 2, 80)
            
            # Desenhar os créditos
            creditos = [
                "Desenvolvido por: [Seu Nome]",
                "",
                "Sprites: Namco",
                "",
                "Sons: Namco",
                "",
                "PyGame: pygame.org"
            ]
            
            espaco_y = 50
            posicao_y_inicial = 180
            
            for i, linha in enumerate(creditos):
                posicao_y = posicao_y_inicial + i * espaco_y
                self.desenhar_texto(linha, self.fonte_menu, self.cor_padrao, constantes.LARGURA // 2, posicao_y)
            
            # Desenhar instrução para voltar
            self.desenhar_texto("Pressione ESC ou ENTER para voltar", 
                               pygame.font.Font(None, 24), self.cor_padrao, constantes.LARGURA // 2, constantes.ALTURA - 50)
            
            # Atualizar a tela
            pygame.display.flip()

def main():
    # Inicializa o Pygame
    pygame.init()
    pygame.mixer.init()
    
    # Cria a janela do jogo
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pacman POO")
    
    # Cria a instância do jogo
    game = Game(screen)
    
    # Loop principal do jogo
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Atualiza e desenha o jogo
        game.update()
        game.draw()
        
        # Atualiza a tela
        pygame.display.flip()
        
        # Controla o FPS
        pygame.time.Clock().tick(60)

# Iniciar o menu quando o script for executado diretamente
if __name__ == "__main__":
    main()