import pygame
import random
import threading 
import pyttsx3
import sys
import config
import interface

# Inicialização # 
pygame.init()

# 1. Descobrir a resolução do monitor do usuário
info_monitor = pygame.display.Info()
largura_inicial = info_monitor.current_w
altura_inicial = info_monitor.current_h - 50 # Subtrai 50px para não cobrir a barra de tarefas do Windows

# 2. Criar a tela com a flag RESIZABLE (Redimensionável)
tela = pygame.display.set_mode((largura_inicial, altura_inicial), pygame.RESIZABLE)
pygame.display.set_caption(config.TITULO)

# Configuração de Voz # 
VOZ_ID_BRASILEIRA = None 
temp_engine = pyttsx3.init()
for voz in temp_engine.getProperty('voices'):
    if "brazil" in voz.name.lower() or "pt-br" in voz.id.lower():
        VOZ_ID_BRASILEIRA = voz.id
        break
del temp_engine

# Fontes # 
fonte_grande = pygame.font.Font(None, config.TAM_GRANDE)
fonte_media = pygame.font.Font(None, config.TAM_MEDIO)
fonte_pequena = pygame.font.Font(None, config.TAM_PEQUENO)

# Dados do Jogo # 
PALAVRAS_MESTRA = ["ABACAXI", "COMPUTADOR", "PYTHON", "ESCOLA", "LOUSA", "FUTURO", "BRASIL"]
palavras_pendentes = PALAVRAS_MESTRA.copy()
falando_agora = False

# Funções Auxiliares # 
def executar_fala(texto):
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

def falar_texto_livre(texto):
    if falando_agora: return
    threading.Thread(target=executar_fala, args=(texto,), daemon=True).start()

def novo_jogo():
    global palavras_pendentes
    if len(palavras_pendentes) == 0:
        return None, 0, "" 
    palavra = random.choice(palavras_pendentes)
    palavras_pendentes.remove(palavra)
    return palavra, 0, ""

def reiniciar_tudo():
    global palavras_pendentes
    palavras_pendentes = PALAVRAS_MESTRA.copy()
    return novo_jogo()

def main():
    global tela 
    
    rodando = True
    relogio = pygame.time.Clock()
    
    palavra_alvo, indice_atual, msg_erro = novo_jogo()
    jogo_zerado = False
    tempo_erro = 0
    
    animacao_indice = -1   
    animacao_escala = 1.0  
    
    pygame.time.delay(500)
    falar_palavra(palavra_alvo)

    while rodando:
        # TAMANHO ATUAL DA TELA A CADA FRAME
        largura_tela = tela.get_width()
        altura_tela = tela.get_height()

        interface.desenhar_fundo(tela)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            
            # EVENTO DE REDIMENSIONAMENTO # 
            elif event.type == pygame.VIDEORESIZE:
                nova_largura, nova_altura = event.w, event.h
                
                # Bloqueio: Se tentar diminuir menos que LARGURA_MINIMA, força volta para LARGURA_MINIMA
                if nova_largura < config.LARGURA_MINIMA:
                    nova_largura = config.LARGURA_MINIMA
                if nova_altura < config.ALTURA_MINIMA:
                    nova_altura = config.ALTURA_MINIMA
                
                # Aplica o novo tamanho (ou o tamanho corrigido)
                tela = pygame.display.set_mode((nova_largura, nova_altura), pygame.RESIZABLE)

            # Eventos de Teclado # 
            elif event.type == pygame.KEYDOWN:
                if jogo_zerado:
                    if event.key == pygame.K_RETURN:
                        palavra_alvo, indice_atual, msg_erro = reiniciar_tudo()
                        jogo_zerado = False
                        falar_palavra(palavra_alvo)
                else:
                    if indice_atual == len(palavra_alvo) and event.key == pygame.K_RETURN:
                        proxima_palavra, i, msg = novo_jogo()
                        if proxima_palavra is None:
                            jogo_zerado = True
                            palavra_alvo = "" 
                            falar_texto_livre("Parabéns! Você completou todas as palavras.")
                        else:
                            palavra_alvo = proxima_palavra
                            indice_atual = 0
                            msg_erro = ""
                            falar_palavra(palavra_alvo)
                        
                    elif event.key == pygame.K_SPACE and not jogo_zerado:
                        falar_palavra(palavra_alvo)
                        
                    elif event.unicode.isalpha() and indice_atual < len(palavra_alvo):
                        letra = event.unicode.upper()
                        if letra == palavra_alvo[indice_atual]:
                            animacao_indice = indice_atual 
                            animacao_escala = 1.5          
                            indice_atual += 1
                            msg_erro = ""
                        else:
                            msg_erro = f"Ops! '{letra}' não é a correta."
                            tempo_erro = pygame.time.get_ticks()

        # Animação das letras aparecendo# 
        if animacao_escala > 1.0:
            animacao_escala -= 0.05
        else:
            animacao_escala = 1.0
            animacao_indice = -1

        # Desenhando Elementos (Centralizados Dinamicamente) # 
        centro_x = largura_tela // 2
        centro_y = altura_tela // 2

        if jogo_zerado:
            texto_fim = fonte_grande.render("VOCÊ VENCEU!", True, config.VERDE_LOUSA)
            
            # Caixa centralizada
            rect_fim = pygame.Rect(0, 0, 500, 200)
            rect_fim.center = (centro_x, centro_y)
            pygame.draw.rect(tela, config.BRANCO_GIZ, rect_fim, border_radius=10)
            
            rect_texto = texto_fim.get_rect(center=(centro_x, centro_y - 20))
            tela.blit(texto_fim, rect_texto)
            
            texto_restart = fonte_pequena.render("Pressione ENTER para jogar novamente", True, config.MARROM_MADEIRA)
            rect_restart = texto_restart.get_rect(center=(centro_x, centro_y + 40))
            tela.blit(texto_restart, rect_restart)

        else:
            instrucao = fonte_pequena.render("ESPAÇO: Ouvir palavra  |  ENTER: Próxima", True, config.BRANCO_GIZ)
            tela.blit(instrucao, (centro_x - instrucao.get_width()//2, 30))

            # Calculando posição das palavras para ficar sempre no meio
            largura_palavra_total = len(palavra_alvo) * 80 
            inicio_x = centro_x - (largura_palavra_total // 2)
            # Define o Y um pouco acima do meio, mas proporcional
            pos_y_letras = centro_y - 50 
            
            for i, letra_correta in enumerate(palavra_alvo):
                pos_x = inicio_x + (i * 80)
                
                if i < indice_atual:
                    escala_atual = 1.0
                    if i == animacao_indice:
                        escala_atual = animacao_escala
                    interface.desenhar_quadrado_letra(tela, fonte_grande, letra_correta, pos_x, pos_y_letras, escala_atual)
                else:
                    # Quadrado vazio
                    pygame.draw.rect(tela, (20, 50, 30), (pos_x, pos_y_letras, 70, 70), border_radius=5)
                    interface.desenhar_underline(tela, pos_x, pos_y_letras)

            # Mensagem de Erro e Vitória (Centralizados na parte inferior)
            if msg_erro:
                if pygame.time.get_ticks() - tempo_erro < 2000:
                    txt = fonte_media.render(msg_erro, True, config.VERMELHO_ERRO)
                    rect_txt = txt.get_rect(center=(centro_x, altura_tela - 100))
                    tela.blit(txt, rect_txt)

            if indice_atual == len(palavra_alvo):
                txt = fonte_media.render("Muito Bem! Pressione ENTER.", True, config.BRANCO_GIZ)
                rect_txt = txt.get_rect(center=(centro_x, pos_y_letras - 100))
                tela.blit(txt, rect_txt)

        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()