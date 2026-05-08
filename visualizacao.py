"""
Modulo de Visualizacao Grafica para o Jogo enclose.horse
Usa matplotlib para desenhar o grid hexagonal e o caminho de fuga.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import to_rgba
import numpy as np
import os


# Cores para cada tipo de celula
CORES = {
    ' ': (0.95, 0.95, 0.90, 1.0),   # espaco livre - bege claro
    '%': (0.30, 0.60, 0.80, 1.0),   # lagoa - azul
    'C': (0.85, 0.55, 0.20, 1.0),   # cavalo - laranja
    '+': (0.40, 0.25, 0.10, 1.0),   # parede - castanho escuro
    'J': (0.90, 0.20, 0.20, 1.0),   # cereja - vermelho
    'M': (0.20, 0.75, 0.20, 1.0),   # maca - verde
    'A': (0.90, 0.80, 0.10, 1.0),    # abelhas - amarelo
}

# Simbolos para cada tipo de celula
SIMBOLOS = {
    ' ': '',
    '%': '~~',
    'C': '\u265E',  # ♞
    '+': '\u2593',  # ▓
    'J': '\u2764',   # ❤
    'M': '\u2B24',   # ⬤
    'A': '\u2603',   # ☃
}

LEGENDAS = {
    ' ': 'Livre',
    '%': 'Lagoa',
    'C': 'Cavalo',
    '+': 'Parede',
    'J': 'Cereja (+3)',
    'M': 'Maca (+10)',
    'A': 'Abelhas (-5)',
}

# Cores para o caminho
COR_CAMINHO = (0.0, 0.0, 0.8, 0.9)       # azul escuro
COR_INICIO = (0.0, 0.8, 0.0, 1.0)         # verde
COR_FIM = (0.8, 0.0, 0.0, 1.0)            # vermelho


def calcular_vertices_hexagono(centro_y, centro_x, tamanho=1.0):
    """
    Calcula os 6 vertices de um hexagono com orientacao 'pointy-top'.
    O hexagono tem a ponta para cima e para baixo.

    Para um grid hexagonal onde linhas pares e impares sao deslocadas:
    - Linhas pares (y%2==0): centro_x alinhado
    - Linhas impares (y%2==1): centro_x deslocado +0.5
    """
    vertices = []
    for i in range(6):
        angulo = np.deg2rad(60 * i - 90)  # -90 para ponta para cima
        vx = centro_x + tamanho * np.cos(angulo)
        vy = centro_y + tamanho * np.sin(angulo)
        vertices.append((vx, vy))
    return vertices


def desenhar_hexagono(ax, centro_y, centro_x, cor, tamanho=0.5, edgecolor='gray', linewidth=0.5):
    """Desenha um hexagono no eixo matplotlib."""
    vertices = calcular_vertices_hexagono(centro_y, centro_x, tamanho)
    hex_poly = mpatches.Polygon(vertices, closed=True,
                                facecolor=cor, edgecolor=edgecolor,
                                linewidth=linewidth)
    ax.add_patch(hex_poly)


def desenhar_mapa(mapa_jogo, caminho=None, titulo=None, mostrar=False,
                  salvar_em=None):
    """
    Desenha o mapa do jogo com visualizacao hexagonal.

    Parametros:
        mapa_jogo: instancia de JogoCavalo
        caminho: lista de posicoes (y, x) do caminho de fuga (opcional)
        titulo: titulo personalizado (opcional)
        mostrar: se True, exibe a figura (default False em modo batch)
        salvar_em: caminho para salvar a figura (opcional)
    """
    linhas = mapa_jogo.linhas
    colunas = mapa_jogo.colunas
    mapa = mapa_jogo.mapa

    # Tamanho do hexagono
    tam = 0.5

    # Calcular dimensoes da figura
    # Largura: cada hexagono tem largura 2*tam, mas com sobreposicao
    # Altura: cada hexagono tem altura sqrt(3)*tam
    altura_hex = np.sqrt(3) * tam
    largura_hex = 2 * tam

    fig_largura = colunas * largura_hex * 0.75 + 2
    fig_altura = linhas * altura_hex * 0.75 + 2

    fig, ax = plt.subplots(1, 1, figsize=(fig_largura, fig_altura))

    # Desenhar cada celula do mapa
    for y in range(linhas):
        for x in range(colunas):
            celula = mapa[y][x]

            # Calcular centro do hexagono
            # Linhas impares deslocadas para a direita
            offset_x = 0.5 * tam if y % 2 != 0 else 0.0
            # A altura real entre linhas eh sqrt(3) * tam * 0.75
            centro_x = x * largura_hex * 0.75 + offset_x + 0.5
            centro_y = -y * altura_hex * 0.75 + 0.5

            # Cor da celula
            cor = CORES.get(celula, (0.8, 0.8, 0.8, 1.0))

            # Se a celula faz parte do caminho, pinta com cor especial
            cor_borda = 'gray'
            espessura_borda = 0.5

            desenhar_hexagono(ax, centro_y, centro_x, cor, tam, cor_borda, espessura_borda)

            # Desenhar simbolo no centro
            if celula in SIMBOLOS and SIMBOLOS[celula]:
                ax.text(centro_x, centro_y, SIMBOLOS[celula],
                        ha='center', va='center', fontsize=8,
                        fontweight='bold')

    # Se ha caminho, desenha-lo
    if caminho and len(caminho) > 1:
        # Converter coordenadas do caminho para coordenadas do grafico
        pontos_x = []
        pontos_y = []
        for (y, x) in caminho:
            offset_x = 0.5 * tam if y % 2 != 0 else 0.0
            px = x * largura_hex * 0.75 + offset_x + 0.5
            py = -y * altura_hex * 0.75 + 0.5
            pontos_x.append(px)
            pontos_y.append(py)

        # Desenhar linha do caminho
        ax.plot(pontos_x, pontos_y, color=COR_CAMINHO, linewidth=3,
                linestyle='-', marker='o', markersize=6,
                markerfacecolor=COR_CAMINHO, markeredgecolor='white',
                markeredgewidth=1.5, zorder=5,
                label='Caminho de fuga')

        # Destacar inicio e fim
        ax.plot(pontos_x[0], pontos_y[0], marker='s', markersize=10,
                color=COR_INICIO, markeredgecolor='white',
                markeredgewidth=2, zorder=6, label='Inicio (Cavalo)')
        ax.plot(pontos_x[-1], pontos_y[-1], marker='*', markersize=14,
                color=COR_FIM, markeredgecolor='white',
                markeredgewidth=2, zorder=6, label='Fuga (Borda)')

        # Numerar os passos
        for i, (px, py) in enumerate(zip(pontos_x, pontos_y)):
            if i > 0 and i < len(pontos_x) - 1:
                ax.annotate(str(i), (px, py),
                           textcoords="offset points",
                           xytext=(0, 10), fontsize=7,
                           ha='center', color='darkblue',
                           fontweight='bold')

    # Configurar limites e aspeto
    ax.set_xlim(-0.5, colunas * largura_hex * 0.75 + 1)
    ax.set_ylim(-linhas * altura_hex * 0.75, 1)
    ax.set_aspect('equal')
    ax.axis('off')

    # Titulo
    if titulo:
        ax.set_title(titulo, fontsize=14, fontweight='bold', pad=10)
    else:
        nome = os.path.splitext(mapa_jogo.nome_arquivo)[0]
        ax.set_title(f'Estado: {nome}  ({colunas}x{linhas})',
                    fontsize=14, fontweight='bold', pad=10)

    # Legenda personalizada
    patches_legenda = []
    for char, legenda in LEGENDAS.items():
        cor = CORES.get(char, (0.5, 0.5, 0.5, 1.0))
        patches_legenda.append(
            mpatches.Patch(color=cor[:3], label=legenda)
        )

    # Adicionar legenda do caminho se existir
    if caminho and len(caminho) > 1:
        patches_legenda.append(
            mpatches.Patch(color=COR_CAMINHO[:3], label='Caminho de fuga')
        )

    ax.legend(handles=patches_legenda, loc='upper center',
              bbox_to_anchor=(0.5, -0.02),
              ncol=4, fontsize=8, framealpha=0.9)

    plt.tight_layout()

    # Salvar se especificado
    if salvar_em:
        plt.savefig(salvar_em, dpi=150, bbox_inches='tight')
        print(f"Figura salva em: {salvar_em}")

    # Mostrar se solicitado
    if mostrar:
        plt.show()
    else:
        plt.close(fig)

    return fig, ax


def visualizar_resultado(mapa_jogo, resultado, nome_algoritmo, mostrar=True):
    """
    Visualiza o resultado de uma busca no mapa.

    Parametros:
        mapa_jogo: instancia de JogoCavalo
        resultado: dicionario com 'caminho', 'expandidos', etc.
        nome_algoritmo: string com nome do algoritmo
        mostrar: se True, mostra a figura
    """
    caminho = resultado.get('caminho')

    if caminho:
        subtitulo = f'{nome_algoritmo} | {len(caminho)-1} passos | {resultado["expandidos"]} nos expandidos'
    else:
        area, pontuacao, itens = mapa_jogo.calcular_pontuacao()
        subtitulo = f'{nome_algoritmo} | CAVALO PRESO! Area: {area} | Pont: {pontuacao}'

    fig, ax = desenhar_mapa(mapa_jogo, caminho, titulo=subtitulo, mostrar=mostrar)
    return fig, ax
