import json
import os
import subprocess
import sys

import pygame

# ---------------------------------------------------------------------------
# launcher.py
#
# Tela inicial do projeto Soletrando.
# Coleta nome, RA e turma do aluno, salva o contexto em arquivo temporário
# e lança o jogo selecionado via subprocess.
#
# Para gerar executável:
#   pip install pyinstaller
#   pyinstaller --onefile --windowed launcher.py
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Configuração — ajuste os caminhos conforme sua estrutura de pastas
# ---------------------------------------------------------------------------
TEMP_CONTEXT_PATH = "/tmp/sessao_context.json"

JOGOS = [
    {
        "nome": "Soletrando",
        "descricao": "Ouça e soletre!",
        "icone": "🔤",
        "script": "main.py",  # caminho relativo ao launcher
        "jogo_id": 1,
    },
    {
        "nome": "Jogo 2",
        "descricao": "Em breve...",
        "icone": "🧩",
        "script": "jogo2/main.py",
        "jogo_id": 2,
    },
    {
        "nome": "Jogo 3",
        "descricao": "Em breve...",
        "icone": "🎯",
        "script": "jogo3/main.py",
        "jogo_id": 3,
    },
]

TURMAS = [
    ("— Selecione —", None),
    ("1º Ano", 1),
    ("2º Ano", 2),
    ("3º Ano", 3),
    ("4º Ano", 4),
    ("5º Ano", 5),
]

# ---------------------------------------------------------------------------
# Cores (mesmo padrão do jogo)
# ---------------------------------------------------------------------------
VERDE_LOUSA = (34, 80, 34)
VERDE_ESCURO = (20, 50, 20)
MARROM = (107, 63, 31)
MARROM_CLARO = (160, 100, 50)
BRANCO_GIZ = (245, 240, 232)
AMARELO = (240, 192, 64)
CINZA = (120, 110, 100)
PRETO = (0, 0, 0)
VERMELHO = (192, 57, 43)
VERDE_OK = (60, 160, 60)

# ---------------------------------------------------------------------------
# Helpers de desenho
# ---------------------------------------------------------------------------


def draw_rect_shadow(surf, cor, rect, radius=10, shadow_offset=5):
    sr = pygame.Rect(
        rect.x + shadow_offset, rect.y + shadow_offset, rect.width, rect.height
    )
    pygame.draw.rect(surf, (10, 30, 10), sr, border_radius=radius)
    pygame.draw.rect(surf, cor, rect, border_radius=radius)


def draw_text_centered(surf, texto, fonte, cor, cx, cy):
    s = fonte.render(texto, True, cor)
    surf.blit(s, s.get_rect(center=(cx, cy)))


def draw_text(surf, texto, fonte, cor, x, y):
    s = fonte.render(texto, True, cor)
    surf.blit(s, (x, y))


def draw_input(surf, fonte, label, valor, rect, ativo, erro=False):
    lbl = fonte.render(label, True, (200, 190, 175))
    surf.blit(lbl, (rect.x, rect.y - 22))
    pygame.draw.rect(surf, (240, 235, 220), rect, border_radius=6)
    cor_borda = AMARELO if ativo else (VERMELHO if erro else MARROM)
    pygame.draw.rect(surf, cor_borda, rect, 3, border_radius=6)
    cursor = "|" if ativo and pygame.time.get_ticks() % 900 < 450 else ""
    txt = fonte.render(valor + cursor, True, (40, 20, 5))
    surf.blit(txt, (rect.x + 10, rect.y + rect.height // 2 - txt.get_height() // 2))


def draw_select(surf, fonte, label, opcoes, indice_sel, rect, aberto):
    lbl = fonte.render(label, True, (200, 190, 175))
    surf.blit(lbl, (rect.x, rect.y - 22))
    pygame.draw.rect(surf, (240, 235, 220), rect, border_radius=6)
    cor_borda = AMARELO if aberto else MARROM
    pygame.draw.rect(surf, cor_borda, rect, 3, border_radius=6)
    txt_sel = fonte.render(opcoes[indice_sel][0], True, (40, 20, 5))
    surf.blit(
        txt_sel, (rect.x + 10, rect.y + rect.height // 2 - txt_sel.get_height() // 2)
    )
    arrow = fonte.render("▾", True, MARROM)
    surf.blit(
        arrow, (rect.right - 28, rect.y + rect.height // 2 - arrow.get_height() // 2)
    )

    if aberto:
        for i, (nome_op, _) in enumerate(opcoes):
            op_rect = pygame.Rect(
                rect.x, rect.bottom + i * rect.height, rect.width, rect.height
            )
            cor_bg = AMARELO if i == indice_sel else (240, 235, 220)
            pygame.draw.rect(surf, cor_bg, op_rect, border_radius=4)
            pygame.draw.rect(surf, MARROM, op_rect, 2, border_radius=4)
            op_txt = fonte.render(nome_op, True, (40, 20, 5))
            surf.blit(
                op_txt,
                (
                    op_rect.x + 10,
                    op_rect.y + op_rect.height // 2 - op_txt.get_height() // 2,
                ),
            )


def draw_card_jogo(surf, fonte_titulo, fonte_desc, jogo, rect, disponivel, hover):
    cor = MARROM_CLARO if hover and disponivel else MARROM
    draw_rect_shadow(surf, cor, rect, radius=14)
    pygame.draw.rect(surf, MARROM, rect, 3, border_radius=14)

    cy = rect.centery
    titulo = fonte_titulo.render(jogo["nome"], True, BRANCO_GIZ)
    surf.blit(titulo, titulo.get_rect(center=(rect.centerx, cy - 18)))
    desc = fonte_desc.render(jogo["descricao"], True, (200, 185, 165))
    surf.blit(desc, desc.get_rect(center=(rect.centerx, cy + 14)))

    if disponivel:
        label = "▶  JOGAR"
        cor_btn = AMARELO if hover else (200, 160, 40)
        btn = pygame.Rect(rect.centerx - 60, rect.bottom - 46, 120, 32)
        pygame.draw.rect(surf, cor_btn, btn, border_radius=20)
        bt = fonte_desc.render(label, True, MARROM)
        surf.blit(bt, bt.get_rect(center=btn.center))
    else:
        lock = fonte_desc.render("🔒 bloqueado", True, CINZA)
        surf.blit(lock, lock.get_rect(center=(rect.centerx, rect.bottom - 30)))


# ---------------------------------------------------------------------------
# Salva contexto e lança jogo
# ---------------------------------------------------------------------------


def salvar_contexto_e_lancar(nome, ra, turma_id, jogo):
    contexto = {
        "ra_aluno": ra,
        "turma_id": turma_id,
        "jogo_id": jogo["jogo_id"],
        "nome": nome,
    }
    with open(TEMP_CONTEXT_PATH, "w", encoding="utf-8") as f:
        json.dump(contexto, f)

    script = os.path.join(os.path.dirname(__file__), jogo["script"])
    subprocess.Popen([sys.executable, script])


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------


def main():
    pygame.init()
    info = pygame.display.Info()
    W, H = min(860, info.current_w), min(620, info.current_h - 60)
    tela = pygame.display.set_mode((W, H), pygame.RESIZABLE)
    pygame.display.set_caption("Soletrando — Launcher")
    clock = pygame.time.Clock()

    f_titulo = pygame.font.Font(None, 62)
    f_grande = pygame.font.Font(None, 36)
    f_media = pygame.font.Font(None, 28)
    f_pequena = pygame.font.Font(None, 22)

    # Estado do formulário
    nome_val = ""
    ra_val = ""
    turma_idx = 0  # índice em TURMAS
    campo_ativo = "nome"  # "nome" | "ra" | None
    select_aberto = False

    rodando = True
    while rodando:
        W = tela.get_width()
        H = tela.get_height()
        cx = W // 2

        # Layout dinâmico
        form_y = 120
        field_h = 44
        field_w = min(380, W - 80)
        field_x = cx - field_w // 2

        rect_nome = pygame.Rect(field_x, form_y, field_w, field_h)
        rect_ra = pygame.Rect(field_x, form_y + 90, field_w, field_h)
        rect_turma = pygame.Rect(field_x, form_y + 180, field_w, field_h)

        card_y = form_y + 290
        card_w = min(200, (W - 80) // 3 - 10)
        card_h = 130
        total_cards = len(JOGOS) * card_w + (len(JOGOS) - 1) * 16
        card_x0 = cx - total_cards // 2
        cards_rects = [
            pygame.Rect(card_x0 + i * (card_w + 16), card_y, card_w, card_h)
            for i in range(len(JOGOS))
        ]

        valido = (
            nome_val.strip() and ra_val.strip() and TURMAS[turma_idx][1] is not None
        )
        mx, my = pygame.mouse.get_pos()

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

            elif event.type == pygame.VIDEORESIZE:
                tela = pygame.display.set_mode(
                    (max(event.w, 500), max(event.h, 400)), pygame.RESIZABLE
                )

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Fecha select se clicar fora
                if select_aberto:
                    fechou = False
                    for i in range(len(TURMAS)):
                        op_rect = pygame.Rect(
                            rect_turma.x,
                            rect_turma.bottom + i * rect_turma.height,
                            rect_turma.width,
                            rect_turma.height,
                        )
                        if op_rect.collidepoint(mx, my):
                            turma_idx = i
                            select_aberto = False
                            fechou = True
                            break
                    if not fechou:
                        select_aberto = False
                    continue

                if rect_nome.collidepoint(mx, my):
                    campo_ativo = "nome"
                elif rect_ra.collidepoint(mx, my):
                    campo_ativo = "ra"
                elif rect_turma.collidepoint(mx, my):
                    select_aberto = not select_aberto
                    campo_ativo = None
                else:
                    campo_ativo = None

                # Cards
                if valido:
                    for i, cr in enumerate(cards_rects):
                        if cr.collidepoint(mx, my):
                            salvar_contexto_e_lancar(
                                nome_val.strip(),
                                ra_val.strip(),
                                TURMAS[turma_idx][1],
                                JOGOS[i],
                            )

            elif event.type == pygame.KEYDOWN:
                if campo_ativo == "nome":
                    if event.key == pygame.K_BACKSPACE:
                        nome_val = nome_val[:-1]
                    elif event.key == pygame.K_TAB:
                        campo_ativo = "ra"
                    elif (event.unicode.isalpha() or event.unicode == " ") and len(
                        nome_val
                    ) < 30:
                        nome_val += event.unicode.upper()

                elif campo_ativo == "ra":
                    if event.key == pygame.K_BACKSPACE:
                        ra_val = ra_val[:-1]
                    elif event.key == pygame.K_TAB:
                        campo_ativo = "nome"
                    elif event.unicode.isnumeric() and len(ra_val) < 15:
                        ra_val += event.unicode

        # ---------------------------------------------------------------
        # Desenho
        # ---------------------------------------------------------------
        tela.fill(VERDE_LOUSA)
        # Grade de linhas estilo lousa
        for y in range(0, H, 40):
            pygame.draw.line(tela, (255, 255, 255, 15), (0, y), (W, y), 1)
        # Borda madeira
        pygame.draw.rect(tela, MARROM, (0, 0, W, H), 16)
        pygame.draw.rect(tela, VERDE_ESCURO, (16, 16, W - 32, H - 32), 2)

        # Título
        draw_text_centered(tela, "🎓  SOLETRANDO", f_titulo, BRANCO_GIZ, cx, 60)

        # Campos
        draw_input(
            tela, f_media, "Nome completo", nome_val, rect_nome, campo_ativo == "nome"
        )
        draw_input(tela, f_media, "RA do Aluno", ra_val, rect_ra, campo_ativo == "ra")
        draw_select(
            tela, f_media, "Turma / Ano", TURMAS, turma_idx, rect_turma, select_aberto
        )

        # Separador
        sep_y = card_y - 24
        pygame.draw.line(tela, MARROM_CLARO, (cx - 200, sep_y), (cx + 200, sep_y), 1)
        draw_text_centered(
            tela, "ESCOLHA UM JOGO", f_pequena, (180, 165, 140), cx, sep_y - 14
        )

        # Cards de jogo
        for i, jogo in enumerate(JOGOS):
            cr = cards_rects[i]
            hover = cr.collidepoint(mx, my)
            draw_card_jogo(tela, f_grande, f_media, jogo, cr, valido, hover)

        # Aviso
        if not valido:
            aviso = f_pequena.render(
                "Preencha todos os campos para liberar os jogos", True, CINZA
            )
            tela.blit(aviso, aviso.get_rect(center=(cx, card_y + card_h + 26)))

        # Select sempre por cima
        if select_aberto:
            draw_select(
                tela,
                f_media,
                "Turma / Ano",
                TURMAS,
                turma_idx,
                rect_turma,
                select_aberto,
            )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
