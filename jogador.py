"""
Classe do personagem jogador
"""
import pygame
from config import (COR_PERSONAGEM, PRETO, 
                    GRAVIDADE, FORCA_PULO, 
                    VELOCIDADE_HORIZONTAL,
                    LARGURA, ALTURA)


class Jogador(pygame.sprite.Sprite):
    """Personagem principal do jogo"""
    
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 50))
        self.image.fill(COR_PERSONAGEM)
        
        # Adicionar um rosto simples
        pygame.draw.circle(self.image, PRETO, (12, 15), 3)  # Olho esquerdo
        pygame.draw.circle(self.image, PRETO, (28, 15), 3)  # Olho direito
        pygame.draw.arc(self.image, PRETO, (10, 20, 20, 15), 3.14, 0, 2)  # Sorriso
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Física
        self.velocidade_x = 0
        self.velocidade_y = 0
        self.no_chao = False
        
    def update(self, plataformas):
        """Atualiza posição e física do jogador"""
        # Aplicar gravidade
        self.velocidade_y += GRAVIDADE
        
        # Movimento horizontal
        teclas = pygame.key.get_pressed()
        self.velocidade_x = 0
        if teclas[pygame.K_LEFT]:
            self.velocidade_x = -VELOCIDADE_HORIZONTAL
        if teclas[pygame.K_RIGHT]:
            self.velocidade_x = VELOCIDADE_HORIZONTAL
            
        # Pular
        if teclas[pygame.K_SPACE] and self.no_chao:
            self.velocidade_y = FORCA_PULO
            self.no_chao = False
            
        # Atualizar posição
        self.rect.x += self.velocidade_x
        self.rect.y += self.velocidade_y
        
        # Limites da tela (horizontal)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LARGURA:
            self.rect.right = LARGURA
            
        # Detectar colisão com plataformas
        self.no_chao = False
        for plataforma in plataformas:
            if self.rect.colliderect(plataforma.rect):
                # Colisão vertical
                if self.velocidade_y > 0:  # Caindo
                    self.rect.bottom = plataforma.rect.top
                    self.velocidade_y = 0
                    self.no_chao = True
                elif self.velocidade_y < 0:  # Subindo
                    self.rect.top = plataforma.rect.bottom
                    self.velocidade_y = 0
                    
        # Cair fora da tela (respawn)
        if self.rect.top > ALTURA:
            self.rect.x = 100
            self.rect.y = ALTURA - 150
            self.velocidade_y = 0
