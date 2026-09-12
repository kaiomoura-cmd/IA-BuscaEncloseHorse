# Agente de Busca — puzzle *enclose.horse*

Agente que resolve o puzzle do [enclose.horse](https://enclose.horse) usando **busca em espaço de
estados** e compara três algoritmos clássicos de IA: **BFS**, **DFS** e **A\*** — todos sobre uma
**grade hexagonal**.

O jogo: um cavalo se move pelo tabuleiro e tenta **escapar para a borda**. Quem joga coloca paredes
para **cercá-lo**. Se o cavalo fica preso, a área cercada pontua com o que estiver dentro dela
(cereja +3, maçã +10, enxame de abelhas −5). O agente responde à pergunta central: **dado este
tabuleiro, o cavalo consegue fugir? Por qual caminho, e quanto custa descobrir isso?**

---

## Modelagem como busca

| Elemento | Definição |
|---|---|
| **Estado** | posição `(y, x)` do cavalo no tabuleiro |
| **Ações** | até 6 vizinhos na grade hexagonal (a vizinhança muda se a linha for par ou ímpar) |
| **Restrições** | paredes (`+`) e lagoas (`%`) bloqueiam o movimento |
| **Teste de objetivo** | o cavalo atingiu **qualquer borda** do mapa (fuga) |
| **Custo do passo** | 1 por movimento |
| **Heurística (A\*)** | distância mínima até a borda mais próxima — **admissível**, pois ignora obstáculos e portanto nunca superestima o custo real |

A grade ser **hexagonal** é o detalhe que dá sabor ao problema: cada célula tem 6 vizinhos, mas
quais 6 depende da paridade da linha. Errar essa física produz caminhos impossíveis.

---

## Resultados

Saída de `python benchmark.py` (Python 3.12, máquina de desenvolvimento):

| Instância | Algoritmo | Resultado | Passos | Nós expandidos | Nós descobertos | Tempo |
|---|---|---|---|---|---|---|
| `geometry.txt` (30×30) | BFS | fuga | **17** | 318 | 361 | 0,66 ms |
| | DFS | fuga | 30 | 31 | 76 | 0,07 ms |
| | **A\*** | fuga | **17** | **194** | 249 | 0,49 ms |
| `entice.txt` (15×15) | BFS | fuga | **7** | 88 | 117 | 0,19 ms |
| | DFS | fuga | 11 | 12 | 34 | 0,03 ms |
| | **A\*** | fuga | **7** | **56** | 130 | 0,21 ms |
| `geometry-resolvido.txt` (30×30) | BFS | fuga | **17** | 302 | 334 | 0,70 ms |
| | DFS | fuga | 29 | 30 | 70 | 0,07 ms |
| | **A\*** | fuga | **17** | **187** | 235 | 0,48 ms |
| `entice-resolvido.txt` (15×15) | BFS | fuga | **7** | 76 | 95 | 0,25 ms |
| | DFS | fuga | 11 | 12 | 33 | 0,03 ms |
| | **A\*** | fuga | **7** | **41** | 84 | 0,15 ms |

As instâncias terminadas em `-resolvido` são tabuleiros com paredes já posicionadas — por isso a
área acessível ao cavalo encolhe (141 → 128 células na `entice`; 535 → 526 na `geometry`), enquanto
o caminho ótimo de fuga permanece o mesmo.

### O que a comparação mostra

- **BFS** encontra o caminho **mínimo** (17 passos na `geometry`, 7 na `entice`) — é a linha de base.
- **A\*** encontra **o mesmo caminho mínimo**, expandindo **39% menos nós** na `geometry`
  (194 contra 318) e **36% menos** na `entice` (56 contra 88). É exatamente o que a heurística
  admissível deveria entregar: **solução ótima com menos esforço**.
- **DFS** é o mais "barato" em nós expandidos (31 contra 318) e o mais rápido — mas devolve
  caminhos **não-ótimos** (30 passos em vez de 17). Ilustra o trade-off clássico: velocidade de
  exploração não é a mesma coisa que qualidade da solução.
- Os tempos são **sub-milissegundo** em todas as instâncias: o gargalo aqui é qualidade de
  heurística, não poder de processamento.

---

## Visualização

`visualizacao.py` desenha o tabuleiro hexagonal com `matplotlib`: paredes, lagoas, itens e o
caminho encontrado, além de uma **animação** passo a passo do cavalo fugindo. É opcional — sem
`numpy`/`matplotlib` instalados, as buscas e o benchmark continuam funcionando normalmente no
terminal.

---

## Estrutura do repositório

```
.
├── enclose_horse.py      # ambiente do jogo + os 3 algoritmos + menu interativo
├── visualizacao.py       # renderização do tabuleiro hexagonal e animação (matplotlib)
├── benchmark.py          # roda BFS/DFS/A* em todas as instâncias e imprime a comparação
├── instancias/           # tabuleiros de exemplo (.txt) + LEIA-ME com o formato
├── requirements.txt
└── LICENSE
```

---

## Como executar

```bash
git clone https://github.com/kaiomoura-cmd/IA-BuscaEncloseHorse.git
cd IA-BuscaEncloseHorse

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt      # opcional: só para a visualização gráfica

# Comparação dos 3 algoritmos em todas as instâncias (execução não-interativa)
python benchmark.py

# Modo interativo: escolher instância, algoritmo e ver a animação
python enclose_horse.py
```

No modo interativo:

```
[1] Busca em Largura (BFS)        [5] Exibir mapa (terminal)
[2] Busca em Profundidade (DFS)   [V] Visualização gráfica
[3] Busca A* (A-Estrela)          [A] Animação do caminho
[4] Executar TODOS os algoritmos
```

---

## Formato das instâncias

Cada `.txt` em `instancias/` é um estado do tabuleiro. A primeira linha traz as dimensões `H V`;
as `V` linhas seguintes descrevem o mapa com `H` caracteres cada:

| Símbolo | Significado |
|---|---|
| ` ` | espaço livre |
| `%` | lagoa (obstáculo) |
| `C` | cavalo |
| `+` | parede colocada pelo jogador |
| `J` | cereja (+3 pontos) |
| `M` | maçã (+10 pontos) |
| `A` | enxame de abelhas (−5 pontos) |

A última linha do arquivo traz o link para jogar a instância original no site.
A documentação completa está em [`instancias/LEIA-ME.txt`](instancias/LEIA-ME.txt).

---

## Limitações e próximos passos

- **A heurística ignora obstáculos.** É admissível (nunca superestima), mas poderia ser muito mais
  informada se usasse a distância real até a borda considerando paredes e lagoas — pré-calculável
  uma vez com uma BFS reversa a partir de todas as células de borda. Aí o A* expandiria ainda menos.
- **Todas as instâncias atuais terminam em fuga.** Falta um caso em que o cavalo esteja de fato
  cercado — é o cenário em que `calcular_pontuacao()` importa, e hoje ele não é exercitado pela
  suíte de exemplos.
- **Sem suíte de testes automatizada.** O `benchmark.py` relata, mas não afirma; testes que
  garantissem "BFS e A* sempre dão o mesmo custo" protegeriam o código contra regressão.
- **DFS não garante otimalidade** — é intencional e didático, não um defeito.

---

## Autor

- **Kaio Moura Pontes** — kaio.moura@ufrrj.br

## Contexto acadêmico

- **Disciplina:** Inteligência Artificial (TN724) — Universidade Federal Rural do Rio de Janeiro
- **Professor:** Ronaldo e Silva Vieira
- **Período:** 2026.1

---

## Licença

[MIT](LICENSE) — use, copie, modifique e distribua à vontade, mantendo o aviso de copyright.
