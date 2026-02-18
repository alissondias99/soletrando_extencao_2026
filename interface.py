import pygame
import config

def desenhar_fundo(tela):
    """
    Desenha a lousa adaptando-se ao tamanho ATUAL da janela.
    """
    largura_atual = tela.get_width()
    altura_atual = tela.get_height()

    tela.fill(config.VERDE_LOUSA)
    
    # Desenha borda de madeira externa
    pygame.draw.rect(tela, config.MARROM_MADEIRA, (0, 0, largura_atual, altura_atual), 20)
    
    # Desenha borda fina interna
    pygame.draw.rect(tela, (20, 60, 30), (20, 20, largura_atual-40, altura_atual-40), 2)

def desenhar_quadrado_letra(tela, fonte, letra, x, y, escala=1.0):
    """
    Desenha o quadrado. A posição X e Y agora são calculadas
    dinamicamente no main.py antes de chamar esta função.
    """
    tamanho_base = 70
    tamanho_real = int(tamanho_base * escala)
    
    # Ajuste de centro para o efeito de "pop"
    offset = (tamanho_real - tamanho_base) // 2
    pos_x = x - offset
    pos_y = y - offset
    
    # Sombra
    sombra_rect = (pos_x + 5, pos_y + 5, tamanho_real, tamanho_real)
    pygame.draw.rect(tela, (50, 30, 10), sombra_rect, border_radius=5)
    
    # Madeira
    rect = (pos_x, pos_y, tamanho_real, tamanho_real)
    pygame.draw.rect(tela, config.MARROM_CLARO, rect, border_radius=5)
    pygame.draw.rect(tela, config.MARROM_MADEIRA, rect, 3, border_radius=5)
    
    # Letra
    if letra:
        texto = fonte.render(letra, True, config.BRANCO_GIZ)
        rect_texto = texto.get_rect(center=(pos_x + tamanho_real//2, pos_y + tamanho_real//2))
        tela.blit(texto, rect_texto)

def desenhar_underline(tela, x, y):
    pygame.draw.line(tela, config.BRANCO_GIZ, (x, y + 75), (x + 70, y + 75), 4)