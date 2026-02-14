import pygame
import random
import threading 
import pyttsx3
import sys

import config
import interface

# Inicialização
pygame.init()
tela = pygame.display.set_mode((config.LARGURA, config.ALTURA))
pygame.display.set_caption(config.TITULO)

# ↓ Procura por um pacote de voz em português no sistema seguindo padrão windows, se não achar o programa ira falar em inglês
VOZ_ID_BRASILEIRA = None 
temp_engine = pyttsx3.init()
for voz in temp_engine.getProperty('voices'):
    if "brazil" in voz.name.lower() or "pt-br" in voz.id.lower():
        VOZ_ID_BRASILEIRA = voz.id
        break
del temp_engine

# Fontes
fonte_grande = pygame.font.Font(None, config.TAM_GRANDE)
fonte_media = pygame.font.Font(None, config.TAM_MEDIO)
fonte_pequena = pygame.font.Font(None, config.TAM_PEQUENO)

palavras = ["ABACAXI", "COMPUTADOR", "PYTHON", "ESCOLA", "LOUSA", "FUTURO"]
falando_agora = False


def executar_fala(texto): # fala a palavra, o programa fica travado enquanto a palavra estiver sendo dita
    global falando_agora
    try:
        falando_agora = True
        tts = pyttsx3.init()
        if VOZ_ID_BRASILEIRA: tts.setProperty('voice', VOZ_ID_BRASILEIRA)
        tts.setProperty('rate', 150)
        tts.say(texto)
        tts.runAndWait()
    except: pass
    finally: falando_agora = False

def falar_palavra(palavra):
    if falando_agora: return
    threading.Thread(target=executar_fala, args=(f"A palavra é: {palavra}",), daemon=True).start()

def novo_jogo():
    return random.choice(palavras), 0, ""

# --- Loop Principal ---
def main():
    rodando = True
    relogio = pygame.time.Clock()
    
    palavra_alvo, indice_atual, msg_erro = novo_jogo()
    tempo_erro = 0
    
    # Variáveis de Animação
    animacao_indice = -1   # Qual letra está animando
    animacao_escala = 1.0  # Tamanho atual da letra (1.0 é normal, 1.5 é grande)
    
    pygame.time.delay(500)
    falar_palavra(palavra_alvo)

    while rodando:
        # 1. Desenha o fundo da lousa (vem do interface.py)
        interface.desenhar_fundo(tela)
        
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            
            if event.type == pygame.KEYDOWN:
                if indice_atual == len(palavra_alvo) and event.key == pygame.K_RETURN:
                    palavra_alvo, indice_atual, msg_erro = novo_jogo()
                    falar_palavra(palavra_alvo)
                    
                elif event.key == pygame.K_SPACE:
                    falar_palavra(palavra_alvo)
                    
                elif event.unicode.isalpha() and indice_atual < len(palavra_alvo):
                    letra = event.unicode.upper()
                    if letra == palavra_alvo[indice_atual]:
                        # ACERTOU: Configura a animação
                        animacao_indice = indice_atual # Marca qual índice vai pular
                        animacao_escala = 1.5          # Começa grande (150%)
                        
                        indice_atual += 1
                        msg_erro = ""
                    else:
                        msg_erro = f"Ops! '{letra}' não é a letra correta."
                        tempo_erro = pygame.time.get_ticks()

        # Animação
        # Se a escala for maior que 1, diminui um pouco por frame
        if animacao_escala > 1.0:
            animacao_escala -= 0.05 # Velocidade da animação
        else:
            animacao_escala = 1.0
            animacao_indice = -1 # Para a animação

        # Desenhando os Elementos
        
        # Texto de instrução (no topo)
        instrucao = fonte_pequena.render("ESPAÇO: Ouvir palavra  |  ENTER: Próxima palavra", True, config.BRANCO_GIZ)
        tela.blit(instrucao, (config.LARGURA//2 - instrucao.get_width()//2, 30))

        # Loop para desenhar as letras
        largura_total = len(palavra_alvo) * 80 # = tamanho quadrado + espaço
        inicio_x = (config.LARGURA - largura_total) // 2
        
        for i, letra_correta in enumerate(palavra_alvo):
            pos_x = inicio_x + (i * 80)
            pos_y = 250
            
            if i < indice_atual:
                # Letra já acertada
                escala_atual = 1.0
                
                # Se for a letra que acabamos de acertar, aplica o 'zoom'
                if i == animacao_indice:
                    escala_atual = animacao_escala
                
                # Chama a função visual do arquivo interface.py
                interface.desenhar_quadrado_letra(tela, fonte_grande, letra_correta, pos_x, pos_y, escala_atual)
            else:
                # Letra ainda oculta (apenas o underline ou quadrado vazio)
                # Vamos desenhar um quadrado vazio escuro para parecer um buraco na madeira
                pygame.draw.rect(tela, (20, 50, 30), (pos_x, pos_y, 70, 70), border_radius=5)
                interface.desenhar_underline(tela, pos_x, pos_y)

        # Mensagem de Erro
        if msg_erro:
            if pygame.time.get_ticks() - tempo_erro < 2000:
                txt = fonte_media.render(msg_erro, True, config.VERMELHO_ERRO)
                tela.blit(txt, (config.LARGURA//2 - txt.get_width()//2, 450))

        # Vitória
        if indice_atual == len(palavra_alvo):
            txt = fonte_media.render("Muito Bem! Pressione ENTER.", True, config.BRANCO_GIZ)
            tela.blit(txt, (config.LARGURA//2 - txt.get_width()//2, 150))

        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()