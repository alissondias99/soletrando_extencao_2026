import pygame
import random
import threading 
import pyttsx3
import sys
import config
import interface

# Inicialização 
pygame.init()
info_monitor = pygame.display.Info()
largura_inicial = info_monitor.current_w
altura_inicial = info_monitor.current_h - 50 
tela = pygame.display.set_mode((largura_inicial, altura_inicial), pygame.RESIZABLE)
pygame.display.set_caption(config.TITULO)

# Configuração de Voz 
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

# DADOS DO JOGO 
LISTAS_PALAVRAS = {
    "FACIL": ["GATO", "CASA"],
    "MEDIO": ["CADERNO", "ESCOLA", "BRINCAR", "JARDIM", "QUEIJO", "FOGUETE"],
    "DIFICIL": ["COMPUTADOR", "ELEFANTE", "PROGRAMACAO", "CHOCOLATE", "ASTRONAUTA"]
}
lista_atual = [] 
palavras_pendentes = []
falando_agora = False

# Funções Auxiliares de Voz e Jogo 
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
    global palavras_pendentes, lista_atual
    palavras_pendentes = lista_atual.copy()
    return novo_jogo()

# Loop Principal 
def main():
    global tela 
    
    rodando = True
    relogio = pygame.time.Clock()
    
    estado_jogo = "MENU"
    
    # Variáveis da partida
    palavra_alvo = ""
    indice_atual = 0
    msg_erro = ""
    jogo_zerado = False
    tempo_erro = 0
    animacao_indice = -1   
    animacao_escala = 1.0  
    
    # Variáveis de Pontuação
    pontuacao = 0
    erros_palavra = 0 # Conta os erros na palavra atual

    while rodando:
        largura_tela = tela.get_width()
        altura_tela = tela.get_height()
        centro_x = largura_tela // 2
        centro_y = altura_tela // 2

        interface.desenhar_fundo(tela)
        mx, my = pygame.mouse.get_pos()
        clicou = False
        
        # Tratamento de Eventos 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
                
            elif event.type == pygame.VIDEORESIZE:
                nova_largura, nova_altura = event.w, event.h
                if nova_largura < config.LARGURA_MINIMA: nova_largura = config.LARGURA_MINIMA
                if nova_altura < config.ALTURA_MINIMA: nova_altura = config.ALTURA_MINIMA
                tela = pygame.display.set_mode((nova_largura, nova_altura), pygame.RESIZABLE)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    clicou = True

            elif event.type == pygame.KEYDOWN:
                if estado_jogo == "JOGANDO":
                    if event.key == pygame.K_ESCAPE:
                        estado_jogo = "MENU" 
                        
                    elif jogo_zerado:
                        if event.key == pygame.K_RETURN:
                            palavra_alvo, indice_atual, msg_erro = reiniciar_tudo()
                            jogo_zerado = False
                            pontuacao = 0 # Zera os pontos ao reiniciar
                            erros_palavra = 0
                            falar_palavra(palavra_alvo)
                    else:
                        if indice_atual == len(palavra_alvo) and event.key == pygame.K_RETURN:
                            proxima_palavra, i, msg = novo_jogo()
                            erros_palavra = 0 # Reseta os erros para a nova palavra
                            
                            if proxima_palavra is None:
                                jogo_zerado = True
                                palavra_alvo = "" 
                                falar_texto_livre(f"Parabéns! Você completou todas as palavras. Sua pontuação foi {pontuacao}.")
                            else:
                                palavra_alvo = proxima_palavra
                                indice_atual = 0
                                msg_erro = ""
                                falar_palavra(palavra_alvo)
                            
                        elif event.key == pygame.K_SPACE and not jogo_zerado:
                            falar_palavra(palavra_alvo)
                            
                        elif event.unicode.isalpha() and indice_atual < len(palavra_alvo):
                            letra = event.unicode.upper()
                            
                            # ACERTOU A LETRA
                            if letra == palavra_alvo[indice_atual]:
                                animacao_indice = indice_atual 
                                animacao_escala = 1.5          
                                indice_atual += 1
                                msg_erro = ""
                                
                                # VERIFICA SE A PALAVRA ACABOU NESTE EXATO MOMENTO
                                if indice_atual == len(palavra_alvo):
                                    if erros_palavra == 0 or erros_palavra <= 2:
                                        pontuacao += 2
                                    elif erros_palavra >= 3:
                                        pontuacao += 1
                                    # else:
                                         # Se errou 3 ou mais, ganha 0.
                                    #    pontuacao += 0 
                                        
                            # ERROU A LETRA
                            else:
                                msg_erro = f"Ops! '{letra}' não é a correta."
                                tempo_erro = pygame.time.get_ticks()
                                erros_palavra += 1 # Aumenta a contagem de erros

        # Lógica da Animação 
        if animacao_escala > 1.0: animacao_escala -= 0.05
        else: animacao_escala, animacao_indice = 1.0, -1

        # DESENHO DA TELA
        
        if estado_jogo == "MENU":
            titulo = fonte_grande.render("ESCOLHA A DIFICULDADE", True, config.BRANCO_GIZ)
            tela.blit(titulo, titulo.get_rect(center=(centro_x, centro_y - 150)))
            
            def criar_botao_menu(texto, pos_y, chave_nivel):
                nonlocal estado_jogo, palavra_alvo, indice_atual, msg_erro, jogo_zerado, pontuacao, erros_palavra
                global lista_atual, palavras_pendentes
                
                largura_btn, altura_btn = 250, 70
                rect_btn = pygame.Rect(centro_x - largura_btn//2, pos_y, largura_btn, altura_btn)
                hover = rect_btn.collidepoint((mx, my))
                cor_atual = config.MARROM_CLARO if hover else config.MARROM_MADEIRA
                
                interface.desenhar_botao(tela, texto, fonte_media, rect_btn.x, rect_btn.y, largura_btn, altura_btn, cor_atual, config.BRANCO_GIZ)
                
                if hover and clicou:
                    lista_atual = LISTAS_PALAVRAS[chave_nivel].copy()
                    palavra_alvo, indice_atual, msg_erro = reiniciar_tudo()
                    jogo_zerado = False
                    estado_jogo = "JOGANDO"
                    pontuacao = 0 # Inicia o nível com zero pontos
                    erros_palavra = 0
                    pygame.time.delay(300) 
                    falar_palavra(palavra_alvo)

            criar_botao_menu("FÁCIL", centro_y - 40, "FACIL")
            criar_botao_menu("MÉDIO", centro_y + 50, "MEDIO")
            criar_botao_menu("DIFÍCIL", centro_y + 140, "DIFICIL")

        elif estado_jogo == "JOGANDO":
            instrucao = fonte_pequena.render("ESPAÇO: Ouvir  |  ENTER: Próxima  |  ESC: Menu", True, config.BRANCO_GIZ)
            tela.blit(instrucao, (centro_x - instrucao.get_width()//2, 30))

            # DESENHAR A PONTUAÇÃO 
            texto_pontos = fonte_media.render(f"Pontos: {pontuacao}", True, config.BRANCO_GIZ)
            tela.blit(texto_pontos, (largura_tela - texto_pontos.get_width() - 30, 20))

            if jogo_zerado:
                # TELA FINAL MOSTRANDO A PONTUAÇÃO
                texto_fim = fonte_grande.render("NÍVEL CONCLUÍDO!", True, config.VERDE_LOUSA)
                texto_score = fonte_media.render(f"Sua Pontuação: {pontuacao}", True, config.MARROM_MADEIRA)
                
                rect_fim = pygame.Rect(0, 0, 600, 250)
                rect_fim.center = (centro_x, centro_y)
                pygame.draw.rect(tela, config.BRANCO_GIZ, rect_fim, border_radius=10)
                
                tela.blit(texto_fim, texto_fim.get_rect(center=(centro_x, centro_y - 40)))
                tela.blit(texto_score, texto_score.get_rect(center=(centro_x, centro_y + 10)))
                
                texto_restart = fonte_pequena.render("ENTER: Jogar Novamente  |  ESC: Menu", True, config.CINZA)
                tela.blit(texto_restart, texto_restart.get_rect(center=(centro_x, centro_y + 70)))

            else:
                largura_palavra_total = len(palavra_alvo) * 80 
                inicio_x = centro_x - (largura_palavra_total // 2)
                pos_y_letras = centro_y - 50 
                
                for i, letra_correta in enumerate(palavra_alvo):
                    pos_x = inicio_x + (i * 80)
                    if i < indice_atual:
                        escala_atual = animacao_escala if i == animacao_indice else 1.0
                        interface.desenhar_quadrado_letra(tela, fonte_grande, letra_correta, pos_x, pos_y_letras, escala_atual)
                    else:
                        pygame.draw.rect(tela, (20, 50, 30), (pos_x, pos_y_letras, 70, 70), border_radius=5)
                        interface.desenhar_underline(tela, pos_x, pos_y_letras)

                if msg_erro and (pygame.time.get_ticks() - tempo_erro < 2000):
                    txt = fonte_media.render(msg_erro, True, config.VERMELHO_ERRO)
                    tela.blit(txt, txt.get_rect(center=(centro_x, altura_tela - 100)))

                if indice_atual == len(palavra_alvo):
                    txt = fonte_media.render("Muito Bem! Pressione ENTER.", True, config.BRANCO_GIZ)
                    tela.blit(txt, txt.get_rect(center=(centro_x, pos_y_letras - 100)))

        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()