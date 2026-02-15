import pygame
import config

def desenhar_fundo(tela):
    """Desenha a lousa verde com uma borda de madeira"""
    tela.fill(config.VERDE_LOUSA)
    
    # Desenha uma borda de madeira (20 pixels)
    pygame.draw.rect(tela, config.MARROM_MADEIRA, (0, 0, config.LARGURA, config.ALTURA), 20)
    
    # Um detalhe extra: borda interna fina para dar profundidade
    pygame.draw.rect(tela, (20, 60, 30), (20, 20, config.LARGURA-40, config.ALTURA-40), 2)

def desenhar_quadrado_letra(tela, fonte, letra, x, y, escala=1.0):
    """
    Desenha o quadrado de madeira com a letra dentro.
    O parâmetro 'escala' serve para fazer a animação de 'pop'.
    """
    tamanho_base = 70
    tamanho_real = int(tamanho_base * escala)
    
    # Ajuste de posição para manter o quadrado centralizado quando ele cresce
    offset = (tamanho_real - tamanho_base) // 2
    pos_x = x - offset
    pos_y = y - offset
    
    # Sombra do quadrado (para dar efeito 3D)
    sombra_rect = (pos_x + 5, pos_y + 5, tamanho_real, tamanho_real)
    pygame.draw.rect(tela, (50, 30, 10), sombra_rect, border_radius=5)
    
    # Quadrado principal (Marrom madeira)
    rect = (pos_x, pos_y, tamanho_real, tamanho_real)
    pygame.draw.rect(tela, config.MARROM_CLARO, rect, border_radius=5)
    pygame.draw.rect(tela, config.MARROM_MADEIRA, rect, 3, border_radius=5)
    
    # A Letra (com efeito de giz)
    if letra:
        texto = fonte.render(letra, True, config.BRANCO_GIZ)
        rect_texto = texto.get_rect(center=(pos_x + tamanho_real//2, pos_y + tamanho_real//2))
        tela.blit(texto, rect_texto)

def desenhar_underline(tela, x, y):
    """Desenha o traço onde a letra vai ficar"""
    pygame.draw.line(tela, config.BRANCO_GIZ, (x, y + 75), (x + 70, y + 75), 4)