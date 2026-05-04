import pygame
import random
import threading 
import pyttsx3
import sys
import config
import interface
from gtts import gTTS
import io


pygame.init()
pygame.mixer.init()
info_monitor = pygame.display.Info()
largura_inicial = info_monitor.current_w
altura_inicial = info_monitor.current_h - 50 
tela = pygame.display.set_mode((largura_inicial, altura_inicial), pygame.RESIZABLE)
pygame.display.set_caption(config.TITULO)


# Fontes 
fonte_grande = pygame.font.Font(None, config.TAM_GRANDE)
fonte_media = pygame.font.Font(None, config.TAM_MEDIO)
fonte_pequena = pygame.font.Font(None, config.TAM_PEQUENO)

# DADOS DO JOGO 
LISTAS_PALAVRAS = {
    "FACIL": ["CAÇADOR", "PROGRAMAÇÂO", "PÉ"],
    "MEDIO": ["CADERNO", "ESCOLA", "BRINCAR", "JARDIM", "QUEIJO", "FOGUETE"],
    "DIFICIL": ["COMPUTADOR", "ELEFANTE", "PROGRAMAÇÃO", "CHOCOLATE", "ASTRONAUTA"]
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
    """Gera o áudio com o Google e toca sem travar o jogo"""
    try:
        # Cria o áudio em português do Brasil
        tts = gTTS(text=texto, lang='pt', tld='com.br')
        
        # Salva o áudio na memória RAM (muito rápido, não cria arquivo no PC)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # O Pygame toca a música de fundo perfeitamente
        pygame.mixer.music.load(fp)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"[ERRO DE ÁUDIO] Verifique a conexão com a internet: {e}")

def falar_palavra(palavra):
    falar_texto_livre(f"A palavra é: {palavra}")

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
    
    # O jogo agora começa na tela de LOGIN
    estado_jogo = "LOGIN" 
    
    # Variáveis do Login
    ra_texto = ""
    nome_texto = ""
    campo_ativo = "RA" 
    
    # Variáveis da partida
    palavra_alvo = ""
    indice_atual = 0
    msg_erro = ""
    jogo_zerado = False
    tempo_erro = 0
    animacao_indice = -1   
    animacao_escala = 1.0  
    pontuacao = 0
    
    # VARIÁVEIS DE MÉTRICA (Invisíveis na tela, enviadas para o console/API) 
    erros_palavra = 0 
    tempo_inicio_palavra = 0

    while rodando:
        largura_tela = tela.get_width()
        altura_tela = tela.get_height()
        centro_x = largura_tela // 2
        centro_y = altura_tela // 2

        # Posições das caixas de texto
        rect_box_ra = pygame.Rect(centro_x - 150, centro_y - 70, 300, 50)
        rect_box_nome = pygame.Rect(centro_x - 150, centro_y + 30, 300, 50)
        rect_btn_entrar = pygame.Rect(centro_x - 100, centro_y + 120, 200, 60)

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
                    if estado_jogo == "LOGIN":
                        if rect_box_ra.collidepoint((mx, my)):
                            campo_ativo = "RA"
                        elif rect_box_nome.collidepoint((mx, my)):
                            campo_ativo = "NOME"

            elif event.type == pygame.KEYDOWN:
                
                # EVENTOS DA TELA DE LOGIN 
                if estado_jogo == "LOGIN":
                    if event.key == pygame.K_TAB:
                        campo_ativo = "NOME" if campo_ativo == "RA" else "RA"
                    elif event.key == pygame.K_RETURN:
                        if len(ra_texto) > 0 and len(nome_texto) > 0:
                            estado_jogo = "MENU" 
                        else:
                            campo_ativo = "NOME" if campo_ativo == "RA" else "RA"
                    elif event.key == pygame.K_BACKSPACE:
                        if campo_ativo == "RA": ra_texto = ra_texto[:-1]
                        else: nome_texto = nome_texto[:-1]
                    else:
                        if campo_ativo == "RA":
                            if event.unicode.isnumeric() and len(ra_texto) < 15:
                                ra_texto += event.unicode
                        elif campo_ativo == "NOME":
                            if (event.unicode.isalpha() or event.unicode == " ") and len(nome_texto) < 20:
                                nome_texto += event.unicode.upper()

                # EVENTOS DO JOGO 
                elif estado_jogo == "JOGANDO":
                    if event.key == pygame.K_ESCAPE:
                        estado_jogo = "MENU" 
                        
                    elif jogo_zerado:
                        if event.key == pygame.K_RETURN:
                            palavra_alvo, indice_atual, msg_erro = reiniciar_tudo()
                            jogo_zerado = False
                            pontuacao = 0 
                            # Reseta métricas ao reiniciar o nível
                            erros_palavra = 0
                            tempo_inicio_palavra = pygame.time.get_ticks()
                            falar_palavra(palavra_alvo)
                    else:
                        if indice_atual == len(palavra_alvo) and event.key == pygame.K_RETURN:
                            proxima_palavra, i, msg = novo_jogo()
                            # Reseta métricas para a próxima palavra
                            erros_palavra = 0 
                            tempo_inicio_palavra = pygame.time.get_ticks()
                            
                            if proxima_palavra is None:
                                jogo_zerado = True
                                palavra_alvo = "" 
                                falar_texto_livre(f"Parabéns {nome_texto}! Você completou todas as palavras. Sua pontuação foi {pontuacao}.")
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
                                    # Calcula tempo final (Ticks atuais - Ticks iniciais) / 1000 para segundos
                                    tempo_total_segundos = (pygame.time.get_ticks() - tempo_inicio_palavra) / 1000
                                    
                                    # Lógica de Pontuação baseada em erros
                                    if erros_palavra == 0: pontuacao += 2
                                    elif erros_palavra < 5: pontuacao += 1
                                    
                                    # LOG PARA O DESENVOLVEDOR (Futuro envio API)
                                    print(f"[API_LOG] Aluno: {nome_texto} | RA: {ra_texto} | Palavra: {palavra_alvo} | Erros: {erros_palavra} | Tempo: {tempo_total_segundos:.2f}s")
                                        
                            # ERROU A LETRA
                            else:
                                msg_erro = f"Ops! '{letra}' não é a correta."
                                tempo_erro = pygame.time.get_ticks()
                                erros_palavra += 1 # Aumenta a contagem de erros

        # Lógica da Animação 
        if animacao_escala > 1.0: animacao_escala -= 0.05
        else: animacao_escala, animacao_indice = 1.0, -1

        # DESENHO DA TELA
        
        if estado_jogo == "LOGIN":
            titulo = fonte_grande.render("IDENTIFICAÇÃO DO ALUNO", True, config.BRANCO_GIZ)
            tela.blit(titulo, titulo.get_rect(center=(centro_x, centro_y - 150)))

            lbl_ra = fonte_pequena.render("Digite seu RA (Apenas Números):", True, config.BRANCO_GIZ)
            tela.blit(lbl_ra, (rect_box_ra.x, rect_box_ra.y - 25))
            
            lbl_nome = fonte_pequena.render("Digite seu Nome:", True, config.BRANCO_GIZ)
            tela.blit(lbl_nome, (rect_box_nome.x, rect_box_nome.y - 25))

            COR_ATIVA = (255, 215, 0) 
            cor_borda_ra = COR_ATIVA if campo_ativo == "RA" else config.MARROM_MADEIRA
            cor_borda_nome = COR_ATIVA if campo_ativo == "NOME" else config.MARROM_MADEIRA

            pygame.draw.rect(tela, (250, 250, 250), rect_box_ra, border_radius=5)
            pygame.draw.rect(tela, cor_borda_ra, rect_box_ra, 4, border_radius=5)
            
            pygame.draw.rect(tela, (250, 250, 250), rect_box_nome, border_radius=5)
            pygame.draw.rect(tela, cor_borda_nome, rect_box_nome, 4, border_radius=5)

            cursor_ra = "|" if campo_ativo == "RA" and pygame.time.get_ticks() % 1000 < 500 else ""
            cursor_nome = "|" if campo_ativo == "NOME" and pygame.time.get_ticks() % 1000 < 500 else ""

            txt_ra = fonte_media.render(ra_texto + cursor_ra, True, (0, 0, 0))
            tela.blit(txt_ra, (rect_box_ra.x + 10, rect_box_ra.y + 10))
            
            txt_nome = fonte_media.render(nome_texto + cursor_nome, True, (0, 0, 0))
            tela.blit(txt_nome, (rect_box_nome.x + 10, rect_box_nome.y + 10))

            pode_entrar = len(ra_texto) > 0 and len(nome_texto) > 0
            hover_entrar = rect_btn_entrar.collidepoint((mx, my))
            
            if pode_entrar:
                cor_btn = config.MARROM_CLARO if hover_entrar else config.MARROM_MADEIRA
            else:
                cor_btn = (150, 150, 150) 

            interface.desenhar_botao(tela, "ENTRAR", fonte_media, rect_btn_entrar.x, rect_btn_entrar.y, 200, 60, cor_btn, config.BRANCO_GIZ)

            if hover_entrar and clicou and pode_entrar:
                estado_jogo = "MENU"

        elif estado_jogo == "MENU":
            saudacao = fonte_pequena.render(f"Olá, {nome_texto}! RA: {ra_texto}", True, config.BRANCO_GIZ)
            tela.blit(saudacao, saudacao.get_rect(center=(centro_x, 30)))

            titulo = fonte_grande.render("ESCOLHA A DIFICULDADE", True, config.BRANCO_GIZ)
            tela.blit(titulo, titulo.get_rect(center=(centro_x, centro_y - 120)))
            
            def criar_botao_menu(texto, pos_y, chave_nivel):
                nonlocal estado_jogo, palavra_alvo, indice_atual, msg_erro, jogo_zerado, pontuacao, erros_palavra, tempo_inicio_palavra
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
                    pontuacao = 0 
                    
                    # Inicia as métricas para a 1ª palavra do nível
                    erros_palavra = 0
                    tempo_inicio_palavra = pygame.time.get_ticks() 
                    
                    pygame.time.delay(300) 
                    falar_palavra(palavra_alvo)

            criar_botao_menu("FÁCIL", centro_y - 20, "FACIL")
            criar_botao_menu("MÉDIO", centro_y + 70, "MEDIO")
            criar_botao_menu("DIFÍCIL", centro_y + 160, "DIFICIL")

        elif estado_jogo == "JOGANDO":
            instrucao = fonte_pequena.render("ESPAÇO: Ouvir  |  ENTER: Próxima  |  ESC: Menu", True, config.BRANCO_GIZ)
            tela.blit(instrucao, (centro_x - instrucao.get_width()//2, 30))

            texto_pontos = fonte_media.render(f"Pontos: {pontuacao}", True, config.BRANCO_GIZ)
            tela.blit(texto_pontos, (largura_tela - texto_pontos.get_width() - 30, 20))

            if jogo_zerado:
                texto_fim = fonte_grande.render("NÍVEL CONCLUÍDO!", True, config.VERDE_LOUSA)
                texto_score = fonte_media.render(f"Sua Pontuação: {pontuacao}", True, config.MARROM_MADEIRA)
                
                rect_fim = pygame.Rect(0, 0, 600, 250)
                rect_fim.center = (centro_x, centro_y)
                pygame.draw.rect(tela, config.BRANCO_GIZ, rect_fim, border_radius=10)
                
                tela.blit(texto_fim, texto_fim.get_rect(center=(centro_x, centro_y - 40)))
                tela.blit(texto_score, texto_score.get_rect(center=(centro_x, centro_y + 10)))
                
                texto_restart = fonte_pequena.render("ENTER: Jogar Novamente  |  ESC: Menu", True, (150, 150, 150))
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