"""
AVENTURA DAS LETRAS
Jogo educativo de plataforma para ensino fundamental
Desenvolvido para projeto de extensão - SI 5º período

Versão Modular - Sistema dinâmico de plataformas
"""

import pygame
import sys
from config import (
    LARGURA, ALTURA, FPS,
    FACIL, MEDIO, DIFICIL
)
from nivel import Nivel
from tela_formacao import TelaFormacao
from telas import TelaMenu, TelaFim


class Jogo:
    """Classe principal que gerencia o jogo"""
    
    def __init__(self):
        # Inicialização do Pygame
        pygame.init()
        
        # Configurar tela
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Aventura das Letras")
        
        # Clock
        self.clock = pygame.time.Clock()
        
        # Fontes
        self.fonte_titulo = pygame.font.Font(None, 80)
        self.fonte_grande = pygame.font.Font(None, 64)
        self.fonte_media = pygame.font.Font(None, 48)
        self.fonte_pequena = pygame.font.Font(None, 32)
        
        # Estado do jogo
        self.estado = "menu"
        self.nivel_atual = 0
        
        # Lista de palavras - agora suporta palavras de qualquer tamanho!
        self.palavras = [
            "GATO", 
            "BOLA", 
            # "CASA", 
            # "FLOR", 
            # "LIVRO",
            # "PARALELEPIPEDO",
            # "COMPUTADOR",
            # "FELICIDADE"
        ]
        
        self.nivel = None
        self.tela_formacao = None
        
        # Dificuldades
        self.dificuldades = [FACIL, MEDIO, DIFICIL]
        self.dificuldade_atual = 0
        
    def iniciar_nivel(self):
        """Inicia um novo nível"""
        if self.nivel_atual < len(self.palavras):
            palavra = self.palavras[self.nivel_atual]
            dificuldade = self.dificuldades[self.dificuldade_atual]
            self.nivel = Nivel(palavra, dificuldade, self.fonte_media)
            self.estado = "jogando"
        else:
            TelaFim.iniciar_serpentinas()  # 🎉 cria as serpentinas UMA VEZ
            self.estado = "fim"
            
    def proximo_nivel(self):
        """Avança para o próximo nível"""
        self.nivel_atual += 1
        # A cada 2 níveis, aumenta a dificuldade
        if self.nivel_atual % 2 == 0 and self.dificuldade_atual < 2:
            self.dificuldade_atual += 1
        self.iniciar_nivel()
        
    def processar_eventos(self):
        """Processa eventos do jogo"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
                
            if evento.type == pygame.KEYDOWN:
                # Menu
                if self.estado == "menu" and evento.key == pygame.K_RETURN:
                    self.iniciar_nivel()
                    
                # Jogando
                elif self.estado == "jogando" and evento.key == pygame.K_RETURN:
                    if len(self.nivel.letras_coletadas) == len(self.nivel.palavra_alvo):
                        self.tela_formacao = TelaFormacao(
                            self.nivel.letras_coletadas,
                            self.nivel.palavra_alvo
                        )
                        self.estado = "formando"
                        
                # Formando palavra
                elif self.estado == "formando":
                    if evento.key == pygame.K_BACKSPACE:
                        self.tela_formacao.remover_ultima()
                    elif evento.key == pygame.K_RETURN:
                        if self.tela_formacao.correto:
                            self.proximo_nivel()
                        elif len(self.tela_formacao.palavra_formada) > 0:
                            self.tela_formacao.verificar()
                            
                # Fim
                elif self.estado == "fim" and evento.key == pygame.K_r:
                    self.nivel_atual = 0
                    self.dificuldade_atual = 0
                    self.estado = "menu"
            
            # Clique nas letras (formando palavra)
            if self.estado == "formando" and evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                rects = self.tela_formacao.get_rect_letras_disponiveis()
                for i, rect in enumerate(rects):
                    if rect.collidepoint(mouse_x, mouse_y):
                        letra = self.tela_formacao.letras_disponiveis[i]
                        self.tela_formacao.adicionar_letra(letra)
                        break
                        
        return True
        
    def atualizar(self):
        """Atualiza a lógica do jogo"""
        if self.estado == "jogando":
            self.nivel.update()
            
    def desenhar(self):
        """Desenha todos os elementos na tela"""
        if self.estado == "menu":
            TelaMenu.desenhar(
                self.tela, 
                self.fonte_titulo, 
                self.fonte_media, 
                self.fonte_pequena
            )
            
        elif self.estado == "jogando":
            self.nivel.desenhar(
                self.tela, 
                self.fonte_pequena, 
                self.fonte_media, 
                self.fonte_grande
            )
            
        elif self.estado == "formando":
            self.tela_formacao.desenhar(
                self.tela, 
                self.fonte_titulo, 
                self.fonte_grande, 
                self.fonte_media, 
                self.fonte_pequena
            )
            
        elif self.estado == "fim":
            TelaFim.desenhar(
                self.tela, 
                self.fonte_titulo, 
                self.fonte_grande, 
                self.fonte_media, 
                self.fonte_pequena
            )
            
        pygame.display.flip()
        
    def executar(self):
        """Loop principal do jogo"""
        rodando = True
        
        while rodando:
            self.clock.tick(FPS)
            
            rodando = self.processar_eventos()
            self.atualizar()
            self.desenhar()
            
        pygame.quit()
        sys.exit()


# Executar o jogo
if __name__ == "__main__":
    jogo = Jogo()
    jogo.executar()
