"""
Classe que gerencia os níveis do jogo
"""
import pygame
import random

from config import (
    LARGURA, ALTURA, ALTURA_CHAO,
    MARGEM_ESQUERDA, MARGEM_DIREITA, MARGEM_SUPERIOR,
    CONFIG_PLATAFORMAS,
    AZUL_ESCURO, BRANCO, PRETO,
    COR_LETRA, COR_LETRA_BORDA,
    VERDE_SUCESSO
)

from elementos import Plataforma, Letra
from jogador import Jogador


class Nivel:
    """Classe que representa um nível do jogo"""
    
    def __init__(self, palavra_alvo, dificuldade, fonte_media):
        self.palavra_alvo = palavra_alvo.upper()
        self.dificuldade = dificuldade.lower()
        self.letras_coletadas = []
        self.completado = False
        self.fonte_media = fonte_media
        
        # Seed aleatória baseada na palavra para variar layouts
        # Isso garante que a mesma palavra terá layouts diferentes em cada jogo
        seed_valor = sum(ord(c) for c in self.palavra_alvo) + random.randint(0, 1000)
        random.seed(seed_valor)
        
        # Grupos de sprites
        self.todas_sprites = pygame.sprite.Group()
        self.plataformas = pygame.sprite.Group()
        self.letras = pygame.sprite.Group()
        
        # Criar jogador
        self.jogador = Jogador(100, ALTURA - 150)
        self.todas_sprites.add(self.jogador)
        
        # Criar plataformas
        self.criar_plataformas()
        
        # Distribuir letras
        self.distribuir_letras()
        
        # Resetar seed para não afetar outras partes
        random.seed()

    def gerar_plataformas_por_palavra(self, palavra, dificuldade):
        cfg = CONFIG_PLATAFORMAS[dificuldade]

        largura_base = cfg["largura_base"]
        largura_min = cfg["largura_minima"]
        salto_v = cfg["salto_vertical"]
        salto_h_min = cfg["salto_h_min"]
        salto_h_max = cfg["salto_h_max"]
        reducao = cfg["reducao_largura"]

        total = max(5, len(palavra) + 1)

        x = MARGEM_ESQUERDA
        y = ALTURA - ALTURA_CHAO - 120
        largura_atual = largura_base

        layout = []

        for _ in range(total):
            if x + largura_atual > LARGURA - MARGEM_DIREITA:
                x = MARGEM_ESQUERDA
                y -= salto_v

            if y < MARGEM_SUPERIOR:
                y = ALTURA - ALTURA_CHAO - 120
                x = MARGEM_ESQUERDA

            layout.append({
                "x": x,
                "y": y,
                "largura": largura_atual
            })

            espaco = random.randint(salto_h_min, salto_h_max)
            x += largura_atual + espaco

            largura_atual = max(largura_min, largura_atual - reducao)

        return layout
        
    def criar_plataformas(self):
        # Chão
        chao = Plataforma(0, ALTURA - ALTURA_CHAO, LARGURA, ALTURA_CHAO)
        self.plataformas.add(chao)
        self.todas_sprites.add(chao)

        # Reset jogador
        self.jogador.rect.x = 80
        self.jogador.rect.y = ALTURA - 150
        self.jogador.velocidade_y = 0

        layout = self.gerar_plataformas_por_palavra(
            self.palavra_alvo,
            self.dificuldade
        )

        for item in layout:
            plat = Plataforma(
                item["x"],
                item["y"],
                item["largura"],
                20
            )
            self.plataformas.add(plat)
            self.todas_sprites.add(plat)
                
    def distribuir_letras(self):
        plataformas_validas = list(self.plataformas)[1:]  # ignora o chão

        letras_embaralhadas = list(self.palavra_alvo)
        random.shuffle(letras_embaralhadas)

        for i, letra in enumerate(letras_embaralhadas):
            if i >= len(plataformas_validas):
                break

            plataforma = plataformas_validas[i]

            x = plataforma.rect.centerx - 20
            y = plataforma.rect.top - 45

            letra_sprite = Letra(x, y, letra, self.fonte_media)
            self.letras.add(letra_sprite)
            self.todas_sprites.add(letra_sprite)

                
    def update(self):
        """Atualiza o nível"""
        self.jogador.update(self.plataformas)
        self.letras.update()
        
        # Verificar colisão com letras
        letras_colididas = pygame.sprite.spritecollide(self.jogador, self.letras, True)
        for letra in letras_colididas:
            self.letras_coletadas.append(letra.letra)
            
    def desenhar(self, tela, fonte_pequena, fonte_media, fonte_grande):
        """Desenha todos os elementos do nível"""
        # Céu com degradê
        for y in range(ALTURA):
            cor_r = 135
            cor_g = 206 - int(y * 0.15)
            cor_b = 250
            pygame.draw.line(tela, (cor_r, cor_g, cor_b), (0, y), (LARGURA, y))
        
        # Desenhar sprites
        self.todas_sprites.draw(tela)
        
        # Desenhar HUD
        self.desenhar_hud(tela, fonte_pequena, fonte_media, fonte_grande)
        
    def desenhar_hud(self, tela, fonte_pequena, fonte_media, fonte_grande):
        """Desenha a interface"""
        # Painel superior com fundo semi-transparente
        painel = pygame.Surface((LARGURA, 120))
        painel.fill(AZUL_ESCURO)
        painel.set_alpha(200)
        tela.blit(painel, (0, 0))
        
        # Palavra alvo
        texto_dica = fonte_media.render(f"Palavra: {self.palavra_alvo}", True, BRANCO)
        tela.blit(texto_dica, (20, 15))
        
        # Letras coletadas
        y_coletadas = 65
        tela.blit(fonte_pequena.render("Coletadas:", True, BRANCO), (20, y_coletadas))
        
        x_letra = 180
        for letra in self.letras_coletadas:
            # Quadradinho com a letra
            rect_letra = pygame.Rect(x_letra, y_coletadas - 5, 40, 40)
            pygame.draw.rect(tela, COR_LETRA, rect_letra)
            pygame.draw.rect(tela, COR_LETRA_BORDA, rect_letra, 2)
            
            texto_letra = fonte_pequena.render(letra, True, PRETO)
            texto_rect = texto_letra.get_rect(center=rect_letra.center)
            tela.blit(texto_letra, texto_rect)
            
            x_letra += 50
        
        # Contador
        total = len(self.palavra_alvo)
        coletadas = len(self.letras_coletadas)
        cor_contador = VERDE_SUCESSO if coletadas == total else BRANCO
        texto_contador = fonte_grande.render(f"{coletadas}/{total}", True, cor_contador)
        rect_contador = texto_contador.get_rect(right=LARGURA - 20, top=20)
        tela.blit(texto_contador, rect_contador)
        
        # Instruções
        if coletadas == total:
            texto_instrucao = fonte_pequena.render("Pressione ENTER para formar a palavra!", True, COR_LETRA)
            rect_instrucao = texto_instrucao.get_rect(center=(LARGURA // 2, ALTURA - 30))
            
            # Fundo para a instrução
            fundo_instrucao = pygame.Surface((rect_instrucao.width + 40, rect_instrucao.height + 20))
            fundo_instrucao.fill(AZUL_ESCURO)
            fundo_instrucao.set_alpha(200)
            tela.blit(fundo_instrucao, (rect_instrucao.x - 20, rect_instrucao.y - 10))
            
            tela.blit(texto_instrucao, rect_instrucao)
