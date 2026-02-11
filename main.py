import pygame
import random
import pyttsx3
import sys

# --- Configurações Iniciais ---
pygame.init()

# Configuração da Voz (TTS)
engine = pyttsx3.init()

# 1. Obter todas as vozes instaladas no computador
vozes = engine.getProperty('voices')
voz_encontrada = False

# 2. Procurar por uma voz brasileira
for voz in vozes:
    # Verifica se o ID ou o Nome contém "BR", "Brazil" ou "PT"
    if "brazil" in voz.name.lower() or "pt-br" in voz.id.lower() or "portuguese" in voz.name.lower():
        engine.setProperty('voice', voz.id)
        voz_encontrada = True
        print(f"Voz definida para: {voz.name}") # Apenas para você conferir no terminal
        break

# Se não encontrar nenhuma, avisa no terminal (vai usar a padrão em inglês)
if not voz_encontrada:
    print("AVISO: Nenhuma voz em português foi encontrada no sistema.")

engine.setProperty('rate', 150) # Velocidade da fala

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (50, 205, 50)
VERMELHO = (220, 20, 60)
CINZA = (200, 200, 200)

# Tela
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Soletrando com Pygame")

# Fontes
fonte_grande = pygame.font.Font(None, 80)
fonte_media = pygame.font.Font(None, 50)
fonte_pequena = pygame.font.Font(None, 30)

# Lista de palavras
palavras = ["ABACAXI", "COMPUTADOR", "PYTHON", "PROGRAMACAO", "JOGO", "ELEFANTE"]

def falar_palavra(palavra):
    """Função para o computador falar a palavra"""
    engine.say(f"Soletre a palavra: {palavra}")
    engine.runAndWait()

def novo_jogo():
    """Reseta o estado para uma nova palavra"""
    palavra = random.choice(palavras)
    return palavra, 0, "" # palavra_alvo, indice_atual, mensagem_erro

# --- Loop Principal ---
def main():
    rodando = True
    relogio = pygame.time.Clock()
    
    palavra_alvo, indice_atual, msg_erro = novo_jogo()
    tempo_erro = 0 # Para controlar quanto tempo a msg de erro fica na tela
    
    # Fala a palavra assim que começa
    # Nota: O pyttsx3 bloqueia o loop enquanto fala. 
    # Para jogos complexos, usa-se threading, mas aqui simplificamos.
    falar_palavra(palavra_alvo) 

    while rodando:
        tela.fill(BRANCO)
        
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
                
            if event.type == pygame.KEYDOWN:
                # Se o jogo acabou (palavra completa), ENTER reinicia
                if indice_atual == len(palavra_alvo):
                    if event.key == pygame.K_RETURN:
                        palavra_alvo, indice_atual, msg_erro = novo_jogo()
                        falar_palavra(palavra_alvo)
                
                # Tecla ESPAÇO repete a palavra
                elif event.key == pygame.K_SPACE:
                    falar_palavra(palavra_alvo)
                
                # Lógica de digitação (apenas letras)
                elif event.unicode.isalpha():
                    letra_digitada = event.unicode.upper()
                    letra_correta = palavra_alvo[indice_atual]
                    
                    if letra_digitada == letra_correta:
                        indice_atual += 1
                        msg_erro = "" # Limpa erro se acertar
                    else:
                        msg_erro = f"Errado! Tente novamente. (Você digitou {letra_digitada})"
                        tempo_erro = pygame.time.get_ticks()

        # --- Desenho na Tela ---
        
        # 1. Instruções
        texto_instrucao = fonte_pequena.render("Pressione ESPAÇO para ouvir novamente", True, CINZA)
        tela.blit(texto_instrucao, (20, 20))

        # 2. Desenhar a palavra (Letras acertadas + Underlines para as que faltam)
        pos_x_inicial = 100
        espacamento = 60
        
        for i, letra in enumerate(palavra_alvo):
            pos_x = pos_x_inicial + (i * espacamento)
            
            if i < indice_atual:
                # Letra já acertada
                texto = fonte_grande.render(letra, True, VERDE)
                tela.blit(texto, (pos_x, 250))
            else:
                # Letra ainda não descoberta (mostra underline)
                pygame.draw.line(tela, PRETO, (pos_x, 300), (pos_x + 40, 300), 5)

        # 3. Mensagem de Erro (some após 2 segundos)
        if msg_erro:
            agora = pygame.time.get_ticks()
            if agora - tempo_erro < 2000: # 2000ms = 2 segundos
                texto_erro = fonte_media.render(msg_erro, True, VERMELHO)
                rect_erro = texto_erro.get_rect(center=(LARGURA//2, 450))
                tela.blit(texto_erro, rect_erro)
            else:
                msg_erro = ""

        # 4. Mensagem de Vitória
        if indice_atual == len(palavra_alvo):
            texto_win = fonte_media.render("Parabéns! Pressione ENTER para continuar.", True, PRETO)
            rect_win = texto_win.get_rect(center=(LARGURA//2, 150))
            tela.blit(texto_win, rect_win)

        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()