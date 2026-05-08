import heapq
import os
from collections import deque

# Tenta importar o modulo de visualizacao (opcional)
try:
    from visualizacao import desenhar_mapa, visualizar_resultado
    from visualizacao import CORES as VIS_CORES
    from visualizacao import calcular_vertices_hexagono
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    VISUALIZACAO_DISPONIVEL = True
except ImportError:
    VISUALIZACAO_DISPONIVEL = False


class JogoCavalo:
    """Classe que representa o ambiente do jogo enclose.horse."""

    # Legenda dos elementos do mapa
    LEGENDA = {
        ' ': 'espaco livre',
        '%': 'lagoa (obstaculo)',
        'C': 'cavalo',
        '+': 'parede (obstaculo)',
        'J': 'cereja (+3 pontos)',
        'M': 'maca (+10 pontos)',
        'A': 'abelhas (-5 pontos)',
    }

    def __init__(self, caminho_arquivo):
        self.mapa = []
        self.cavalo = (0, 0)
        self.linhas = 0
        self.colunas = 0
        self.nome_arquivo = os.path.basename(caminho_arquivo)

        self.carregar_mapa(caminho_arquivo)

    def carregar_mapa(self, caminho_arquivo):
        """Carrega o mapa a partir de um ficheiro .txt."""
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            linhas_do_arquivo = arquivo.readlines()

        # Primeira linha: dimensoes H V (colunas x linhas)
        dimensoes = linhas_do_arquivo[0].strip().split()
        self.colunas = int(dimensoes[0])
        self.linhas = int(dimensoes[1])

        # Linhas seguintes: o mapa propriamente dito
        self.mapa = []
        for i in range(1, self.linhas + 1):
            texto_da_linha = linhas_do_arquivo[i].rstrip('\n')
            self.mapa.append(list(texto_da_linha))

        # Localiza o cavalo no mapa
        for y in range(self.linhas):
            for x in range(self.colunas):
                if self.mapa[y][x] == 'C':
                    self.cavalo = (y, x)
                    return

    def pegar_acoes_validas(self, estado_atual):
        """
        Devolve lista de posicoes vizinhas validas (hex grid).

        No grid hexagonal, a fisica muda se a linha eh par ou impar:
          - Linha PAR: 6 vizinhos -> (0,-1),(0,1),(-1,-1),(-1,0),(1,-1),(1,0)
          - Linha IMPAR: 6 vizinhos -> (0,-1),(0,1),(-1,0),(-1,1),(1,0),(1,1)
        """
        y, x = estado_atual

        if y % 2 == 0:
            movimentos = [(0, -1), (0, 1), (-1, -1), (-1, 0), (1, -1), (1, 0)]
        else:
            movimentos = [(0, -1), (0, 1), (-1, 0), (-1, 1), (1, 0), (1, 1)]

        acoes_validas = []
        for dy, dx in movimentos:
            novo_y, novo_x = y + dy, x + dx

            # 1. Checa limites do mapa
            if 0 <= novo_y < self.linhas and 0 <= novo_x < self.colunas:
                # 2. Checa se nao eh lagoa (%) ou parede (+)
                if self.mapa[novo_y][novo_x] not in ('%', '+'):
                    acoes_validas.append((novo_y, novo_x))

        return acoes_validas

    def is_objetivo(self, estado_atual):
        """Objetivo: cavalo atinge qualquer borda do mapa (fuga)."""
        y, x = estado_atual
        return (y == 0 or y == self.linhas - 1 or
                x == 0 or x == self.colunas - 1)

    def calcular_heuristica(self, estado_atual):
        """
        Heuristica admissivel: distancia minima ate a borda mais proxima.
        Usa-se 'distancia hexagonal simplificada' (min passos ate a borda).
        """
        y, x = estado_atual
        dist_topo = y
        dist_base = (self.linhas - 1) - y
        dist_esquerda = x
        dist_direita = (self.colunas - 1) - x
        return min(dist_topo, dist_base, dist_esquerda, dist_direita)

    # ------------------------------------------------------------------
    # Algoritmos de Busca
    # ------------------------------------------------------------------

    def busca_bfs(self):
        """
        Busca em Largura (BFS).
        Garante caminho minimo. Usa deque para O(1) na fila.
        """
        fila = deque()
        fila.append((self.cavalo, [self.cavalo]))
        visitados = {self.cavalo}
        nos_expandidos = 0
        nos_descobertos = 1

        while fila:
            estado_atual, caminho = fila.popleft()
            nos_expandidos += 1

            if self.is_objetivo(estado_atual):
                return {
                    'caminho': caminho,
                    'expandidos': nos_expandidos,
                    'descobertos': nos_descobertos,
                    'tamanho_caminho': len(caminho) - 1,
                }

            for vizinho in self.pegar_acoes_validas(estado_atual):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    nos_descobertos += 1
                    fila.append((vizinho, caminho + [vizinho]))

        return {
            'caminho': None,
            'expandidos': nos_expandidos,
            'descobertos': nos_descobertos,
            'tamanho_caminho': None,
        }

    def busca_dfs(self):
        """
        Busca em Profundidade (DFS).
        Usa pilha (lista). NAO garante caminho minimo.
        """
        pilha = [(self.cavalo, [self.cavalo])]
        visitados = set()
        nos_expandidos = 0
        nos_descobertos = 1

        while pilha:
            estado_atual, caminho = pilha.pop()
            nos_expandidos += 1

            if self.is_objetivo(estado_atual):
                return {
                    'caminho': caminho,
                    'expandidos': nos_expandidos,
                    'descobertos': nos_descobertos,
                    'tamanho_caminho': len(caminho) - 1,
                }

            if estado_atual not in visitados:
                visitados.add(estado_atual)
                for vizinho in self.pegar_acoes_validas(estado_atual):
                    if vizinho not in visitados:
                        nos_descobertos += 1
                        pilha.append((vizinho, caminho + [vizinho]))

        return {
            'caminho': None,
            'expandidos': nos_expandidos,
            'descobertos': nos_descobertos,
            'tamanho_caminho': None,
        }

    def busca_a_estrela(self):
        """
        Busca A* (A-Estrela) com heuristica admissivel.
        Garante caminho minimo se a heuristica for admissivel e consistente.
        """
        fila_prioridade = []
        estado_inicial = self.cavalo
        g_inicial = 0
        h_inicial = self.calcular_heuristica(estado_inicial)
        f_inicial = g_inicial + h_inicial

        heapq.heappush(fila_prioridade, (f_inicial, g_inicial, estado_inicial, [estado_inicial]))
        visitados = set()
        nos_expandidos = 0
        nos_descobertos = 1

        while fila_prioridade:
            f, g, estado_atual, caminho = heapq.heappop(fila_prioridade)
            nos_expandidos += 1

            if self.is_objetivo(estado_atual):
                return {
                    'caminho': caminho,
                    'expandidos': nos_expandidos,
                    'descobertos': nos_descobertos,
                    'tamanho_caminho': len(caminho) - 1,
                }

            if estado_atual in visitados:
                continue
            visitados.add(estado_atual)

            for vizinho in self.pegar_acoes_validas(estado_atual):
                if vizinho not in visitados:
                    novo_g = g + 1
                    novo_h = self.calcular_heuristica(vizinho)
                    novo_f = novo_g + novo_h
                    nos_descobertos += 1
                    heapq.heappush(fila_prioridade, (novo_f, novo_g, vizinho, caminho + [vizinho]))

        return {
            'caminho': None,
            'expandidos': nos_expandidos,
            'descobertos': nos_descobertos,
            'tamanho_caminho': None,
        }

    # ------------------------------------------------------------------
    # Calcular pontuacao (quando o cavalo esta preso)
    # ------------------------------------------------------------------

    def calcular_pontuacao(self):
        """
        Calcula a pontuacao quando o cavalo NAO consegue fugir:
        - Conta todos os espacos livres acessiveis (BFS a partir do cavalo)
        - Soma modificadores: cereja (+3), maca (+10), abelhas (-5)
        """
        area = 0
        pontuacao = 0
        itens = {'J': 0, 'M': 0, 'A': 0}
        visitados = {self.cavalo}
        fila = deque([self.cavalo])

        while fila:
            y, x = fila.popleft()
            area += 1

            # Verifica modificadores de pontuacao
            celula = self.mapa[y][x]
            if celula == 'J':
                pontuacao += 3
                itens['J'] += 1
            elif celula == 'M':
                pontuacao += 10
                itens['M'] += 1
            elif celula == 'A':
                pontuacao -= 5
                itens['A'] += 1

            for vizinho in self.pegar_acoes_validas((y, x)):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append(vizinho)

        return area, pontuacao, itens

    # ------------------------------------------------------------------
    # Exibir mapa (terminal)
    # ------------------------------------------------------------------

    def exibir_mapa(self):
        """Exibe o mapa formatado no terminal."""
        print(f"\nMapa: {self.nome_arquivo}  ({self.colunas}x{self.linhas})")
        print("-" * max(self.colunas + 2, 50))
        for y in range(self.linhas):
            linha = ''.join(self.mapa[y])
            # Pequeno offset visual para linhas impares (efeito hexagonal)
            prefixo = ' ' if y % 2 != 0 else ''
            print(f"{prefixo}{linha}")
        print("-" * max(self.colunas + 2, 50))
        print(f"Cavalo na posicao: (y={self.cavalo[0]}, x={self.cavalo[1]})")

        # Mostra legenda
        print("\nLegenda:")
        for char, desc in self.LEGENDA.items():
            print(f"  '{char}' = {desc}")
        print()


# ======================================================================
# FUNCOES AUXILIARES (menus, IO)
# ======================================================================

def listar_arquivos_disponiveis():
    """Procura os ficheiros .txt na pasta 'estados'."""
    # Tenta encontrar a pasta estados relativamente ao script
    dir_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_estados = os.path.join(dir_atual, 'estados-e1-ia-20261', 'estados')

    # Se nao encontrar, tenta a partir do diretorio corrente
    if not os.path.isdir(pasta_estados):
        pasta_estados = os.path.join(os.getcwd(), 'estados-e1-ia-20261', 'estados')

    if not os.path.isdir(pasta_estados):
        return None, []

    ficheiros = sorted([
        f for f in os.listdir(pasta_estados)
        if f.endswith('.txt')
    ])
    return pasta_estados, ficheiros


def selecionar_arquivo():
    """Menu para selecionar qual ficheiro de estado carregar."""
    pasta_estados, ficheiros = listar_arquivos_disponiveis()

    if not ficheiros or pasta_estados is None:
        print("\n" + "=" * 50)
        print("   ERRO: PASTA DE ESTADOS NAO ENCONTRADA!")
        print("=" * 50)
        print("Nao foi possivel localizar a pasta:")
        print("  'estados-e1-ia-20261/estados/'")
        print("\nCertifique-se de que o script esta no mesmo diretorio")
        print("da pasta 'estados-e1-ia-20261'.")
        print("=" * 50)
        return None, None

    print("\n" + "=" * 50)
    print("   SELECIONE O ARQUIVO DE ESTADO")
    print("=" * 50)
    for i, ficheiro in enumerate(ficheiros, 1):
        tipo = "(ORIGINAL)" if "resolvido" not in ficheiro.lower() else "(RESOLVIDO)"
        print(f"  [{i}] {ficheiro}  {tipo}")
    print(f"  [{len(ficheiros) + 1}] Sair")
    print("=" * 50)

    while True:
        try:
            escolha = int(input(f"\nEscolha (1-{len(ficheiros) + 1}): "))
            if escolha == len(ficheiros) + 1:
                print("Saindo...")
                return None, None
            if 1 <= escolha <= len(ficheiros):
                caminho = os.path.join(pasta_estados, ficheiros[escolha - 1])
                return caminho, ficheiros[escolha - 1]
            print(f"Opcao invalida! Escolha entre 1 e {len(ficheiros) + 1}.")
        except ValueError:
            print("Digite um numero valido.")


def executar_busca(jogo, algoritmo):
    """Executa um algoritmo de busca e exibe os resultados."""
    algoritmos = {
        'bfs': ('BFS (Busca em Largura)', jogo.busca_bfs),
        'dfs': ('DFS (Busca em Profundidade)', jogo.busca_dfs),
        'a_estrela': ('A* (A-Estrela)', jogo.busca_a_estrela),
    }

    nome, funcao = algoritmos[algoritmo]
    print(f"\n--- Executando {nome}... ---")
    resultado = funcao()

    print(f"\n>>> Resultados: {nome} <<<")
    print(f"  Nos expandidos:  {resultado['expandidos']}")
    print(f"  Nos descobertos: {resultado['descobertos']}")

    if resultado['caminho']:
        print(f"  -> CAVALO CONSEGUIU FUGIR!")
        print(f"  Tamanho do caminho: {resultado['tamanho_caminho']} passos")
        print(f"  Caminho (y, x): {resultado['caminho']}")
    else:
        print(f"  -> CAVALO ESTA PRESO!")
        area, pontuacao, itens = jogo.calcular_pontuacao()
        print(f"  Area acessivel:     {area} celulas")
        print(f"  Pontuacao total:    {pontuacao} pontos")
        print(f"  Itens coletados:")
        print(f"    Cerejas (J):  {itens['J']} x +3 = {itens['J'] * 3}")
        print(f"    Macas (M):    {itens['M']} x +10 = {itens['M'] * 10}")
        print(f"    Abelhas (A):  {itens['A']} x -5 = {itens['A'] * -5}")

    return resultado


def executar_todos(jogo):
    """Executa todos os algoritmos e mostra comparacao."""
    print("\n" + "=" * 60)
    print("   COMPARATIVO DE ALGORITMOS")
    print("=" * 60)

    resultados = {}
    for alg in ['bfs', 'dfs', 'a_estrela']:
        resultados[alg] = executar_busca(jogo, alg)

    print("\n" + "=" * 60)
    print("   TABELA COMPARATIVA")
    print("=" * 60)
    print(f"{'Algoritmo':<15} {'Expandidos':<15} {'Descobertos':<15} {'Caminho':<10}")
    print("-" * 60)

    for alg, nome in [('bfs', 'BFS'), ('dfs', 'DFS'), ('a_estrela', 'A*')]:
        r = resultados[alg]
        tam = str(r['tamanho_caminho']) if r['tamanho_caminho'] is not None else 'PRESO'
        print(f"{nome:<15} {r['expandidos']:<15} {r['descobertos']:<15} {tam:<10}")

    print("=" * 60)


# ======================================================================
# FUNCOES DE VISUALIZACAO GRAFICA
# ======================================================================

def perguntar_visualizar(jogo, resultado, nome_algoritmo):
    """Pergunta ao usuario se deseja visualizar o resultado."""
    if not VISUALIZACAO_DISPONIVEL:
        return
    try:
        resp = input("\nVisualizar graficamente? (s/N): ").strip().lower()
        if resp == 's':
            visualizar_resultado(jogo, resultado, nome_algoritmo, mostrar=True)
    except (KeyboardInterrupt, EOFError):
        pass


def menu_visualizacao(jogo):
    """Menu de visualizacao grafica."""
    if not VISUALIZACAO_DISPONIVEL:
        print("Visualizacao nao disponivel (instale matplotlib).")
        return

    print("\n--- VISUALIZACAO GRAFICA ---")
    print("  [1] Mapa completo")
    print("  [2] Mapa + BFS")
    print("  [3] Mapa + DFS")
    print("  [4] Mapa + A*")
    print("  [5] Todos os caminhos (lado a lado)")
    print("  [0] Voltar")

    escolha = input("Opcao: ").strip()

    if escolha == '1':
        desenhar_mapa(jogo, titulo=f'Mapa: {jogo.nome_arquivo}', mostrar=True)
    elif escolha == '2':
        resultado = jogo.busca_bfs()
        visualizar_resultado(jogo, resultado, 'BFS', mostrar=True)
    elif escolha == '3':
        resultado = jogo.busca_dfs()
        visualizar_resultado(jogo, resultado, 'DFS', mostrar=True)
    elif escolha == '4':
        resultado = jogo.busca_a_estrela()
        visualizar_resultado(jogo, resultado, 'A*', mostrar=True)
    elif escolha == '5':
        visualizar_todos_caminhos(jogo)


def menu_animacao(jogo):
    """Menu de animacao do caminho."""
    if not VISUALIZACAO_DISPONIVEL:
        print("Animacao nao disponivel (instale matplotlib).")
        return

    print("\n--- ANIMACAO DO CAMINHO ---")
    print("  [1] Animacao BFS")
    print("  [2] Animacao DFS")
    print("  [3] Animacao A*")
    print("  [0] Voltar")

    escolha = input("Opcao: ").strip()

    alg_map = {'1': 'bfs', '2': 'dfs', '3': 'a_estrela'}
    nome_map = {'1': 'BFS', '2': 'DFS', '3': 'A*'}

    if escolha in alg_map:
        func = getattr(jogo, f'busca_{alg_map[escolha]}')
        resultado = func()
        if resultado['caminho']:
            animar_caminho(jogo, resultado['caminho'], nome_map[escolha])
        else:
            print("Cavalo esta preso! Nao ha caminho para animar.")
            visualizar_resultado(jogo, resultado, nome_map[escolha], mostrar=True)


def visualizar_todos_caminhos(jogo):
    """Mostra os 3 algoritmos lado a lado."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    algoritmos = [
        ('BFS', jogo.busca_bfs),
        ('DFS', jogo.busca_dfs),
        ('A*', jogo.busca_a_estrela),
    ]

    tam = 0.45
    altura_hex = np.sqrt(3) * tam
    largura_hex = 2 * tam
    linhas = jogo.linhas
    colunas = jogo.colunas

    for ax, (nome, func) in zip(axes, algoritmos):
        resultado = func()
        caminho = resultado.get('caminho')

        if caminho:
            titulo = f'{nome} | {len(caminho)-1} passos\n{resultado["expandidos"]} expandidos'
        else:
            titulo = f'{nome} | PRESO\n{resultado["expandidos"]} expandidos'

        # Desenha o mapa neste subplot
        for y in range(linhas):
            for x in range(colunas):
                celula = jogo.mapa[y][x]
                offset_x = 0.5 * tam if y % 2 != 0 else 0.0
                cx = x * largura_hex * 0.75 + offset_x + 0.5
                cy = -y * altura_hex * 0.75 + 0.5

                cor = VIS_CORES.get(celula, (0.8, 0.8, 0.8, 1.0))
                verts = calcular_vertices_hexagono(cy, cx, tam)
                hex_poly = mpatches.Polygon(verts, closed=True,
                                            facecolor=cor, edgecolor='gray',
                                            linewidth=0.3)
                ax.add_patch(hex_poly)

        # Desenhar caminho
        if caminho:
            pontos_x = []
            pontos_y = []
            for (y, x) in caminho:
                offset_x = 0.5 * tam if y % 2 != 0 else 0.0
                px = x * largura_hex * 0.75 + offset_x + 0.5
                py = -y * altura_hex * 0.75 + 0.5
                pontos_x.append(px)
                pontos_y.append(py)
            ax.plot(pontos_x, pontos_y, color='blue', linewidth=2,
                    marker='o', markersize=3, zorder=5)
            ax.plot(pontos_x[0], pontos_y[0], 'gs', markersize=6, zorder=6)
            ax.plot(pontos_x[-1], pontos_y[-1], 'r*', markersize=8, zorder=6)

        ax.set_title(titulo, fontsize=10, fontweight='bold')
        ax.set_xlim(-0.5, colunas * largura_hex * 0.75 + 1)
        ax.set_ylim(-linhas * altura_hex * 0.75, 1)
        ax.set_aspect('equal')
        ax.axis('off')

    plt.suptitle(f'Comparativo: {jogo.nome_arquivo}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()


def animar_caminho(jogo, caminho, nome_algoritmo):
    """Anima o caminho passo a passo."""
    from matplotlib.animation import FuncAnimation

    tam = 0.5
    altura_hex = np.sqrt(3) * tam
    largura_hex = 2 * tam
    linhas = jogo.linhas
    colunas = jogo.colunas

    fig, ax = plt.subplots(figsize=(10, 8))

    # Desenhar mapa estatico
    for y in range(linhas):
        for x in range(colunas):
            celula = jogo.mapa[y][x]
            offset_x = 0.5 * tam if y % 2 != 0 else 0.0
            cx = x * largura_hex * 0.75 + offset_x + 0.5
            cy = -y * altura_hex * 0.75 + 0.5

            cor = VIS_CORES.get(celula, (0.8, 0.8, 0.8, 1.0))
            verts = calcular_vertices_hexagono(cy, cx, tam)
            hex_poly = mpatches.Polygon(verts, closed=True,
                                        facecolor=cor, edgecolor='gray',
                                        linewidth=0.5)
            ax.add_patch(hex_poly)

    ax.set_xlim(-0.5, colunas * largura_hex * 0.75 + 1)
    ax.set_ylim(-linhas * altura_hex * 0.75, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'{nome_algoritmo} - Animacao do Caminho', fontsize=14, fontweight='bold')

    # Inicializar linha do caminho
    linha_caminho, = ax.plot([], [], color='blue', linewidth=3,
                              marker='o', markersize=6, zorder=5)
    ponto_atual, = ax.plot([], [], 'ro', markersize=10, zorder=6)

    # Converter coordenadas do caminho
    pontos_x = []
    pontos_y = []
    for (y, x) in caminho:
        offset_x = 0.5 * tam if y % 2 != 0 else 0.0
        px = x * largura_hex * 0.75 + offset_x + 0.5
        py = -y * altura_hex * 0.75 + 0.5
        pontos_x.append(px)
        pontos_y.append(py)

    def init():
        linha_caminho.set_data([], [])
        ponto_atual.set_data([], [])
        return linha_caminho, ponto_atual

    def update(frame):
        linha_caminho.set_data(pontos_x[:frame+1], pontos_y[:frame+1])
        if frame < len(pontos_x):
            ponto_atual.set_data([pontos_x[frame]], [pontos_y[frame]])
        return linha_caminho, ponto_atual

    ani = FuncAnimation(fig, update, frames=len(caminho),
                        init_func=init, blit=True,
                        interval=500, repeat=False)

    plt.tight_layout()
    plt.show()
    return ani


# ======================================================================
# MENU PRINCIPAL
# ======================================================================

def menu_principal(jogo):
    """Menu principal para selecionar o algoritmo de busca."""
    while True:
        print("\n" + "=" * 55)
        print("   ENCLOSE.HORSE - SOLUCIONADOR DE CAVALOS")
        print("=" * 55)
        print(f"   Arquivo:  {jogo.nome_arquivo}")
        print(f"   Mapa:     {jogo.colunas}x{jogo.linhas}")
        print(f"   Cavalo:   (y={jogo.cavalo[0]}, x={jogo.cavalo[1]})")
        print("=" * 55)
        print("  [1] Busca em Largura (BFS)")
        print("  [2] Busca em Profundidade (DFS)")
        print("  [3] Busca A* (A-Estrela)")
        print("  [4] Executar TODOS os algoritmos")
        print("  [5] Exibir mapa (terminal)")
        if VISUALIZACAO_DISPONIVEL:
            print("  [V] Visualizacao grafica")
            print("  [A] Animacao do caminho")
        print("  [6] Voltar ao menu de arquivos")
        print("  [7] Sair")
        print("=" * 55)

        escolha = input("Opcao: ").strip()

        if escolha == '1':
            resultado = executar_busca(jogo, 'bfs')
            perguntar_visualizar(jogo, resultado, 'BFS (Busca em Largura)')
        elif escolha == '2':
            resultado = executar_busca(jogo, 'dfs')
            perguntar_visualizar(jogo, resultado, 'DFS (Busca em Profundidade)')
        elif escolha == '3':
            resultado = executar_busca(jogo, 'a_estrela')
            perguntar_visualizar(jogo, resultado, 'A* (A-Estrela)')
        elif escolha == '4':
            executar_todos(jogo)
        elif escolha == '5':
            jogo.exibir_mapa()
        elif escolha.lower() == 'v' and VISUALIZACAO_DISPONIVEL:
            menu_visualizacao(jogo)
        elif escolha.lower() == 'a' and VISUALIZACAO_DISPONIVEL:
            menu_animacao(jogo)
        elif escolha == '6':
            return  # Volta ao menu de arquivos
        elif escolha == '7':
            print("Saindo...")
            exit()
        else:
            print("Opcao invalida! Tente novamente.")


# ======================================================================
# MAIN
# ======================================================================

def main():
    """Funcao principal com loop de menus."""
    while True:
        caminho, nome_arquivo = selecionar_arquivo()
        if caminho is None:
            break

        try:
            jogo = JogoCavalo(caminho)
            menu_principal(jogo)
        except FileNotFoundError:
            print(f"\nErro: Arquivo '{caminho}' nao encontrado.")
        except Exception as e:
            print(f"\nErro ao carregar o arquivo: {e}")


if __name__ == "__main__":
    main()
