#!/usr/bin/env python3
"""Compara os tres algoritmos de busca sobre todas as instancias em instancias/.

Roda BFS, DFS e A* para cada arquivo .txt e imprime uma tabela com:
resultado (fuga ou preso), tamanho do caminho, nos expandidos, nos descobertos
e tempo de execucao.

Uso:
    python benchmark.py
"""
from __future__ import annotations

import os
import time

from enclose_horse import JogoCavalo, listar_arquivos_disponiveis

ALGORITMOS = [("bfs", "BFS"), ("dfs", "DFS"), ("a_estrela", "A*")]


def main() -> None:
    pasta, arquivos = listar_arquivos_disponiveis()
    if not pasta or not arquivos:
        print("Nenhuma instancia .txt valida encontrada em 'instancias/'.")
        return

    print("=" * 78)
    print("  BENCHMARK - BFS x DFS x A*  |  puzzle enclose.horse")
    print("=" * 78)

    for nome in arquivos:
        jogo = JogoCavalo(os.path.join(pasta, nome))
        print(f"\n{nome}  ({jogo.linhas}x{jogo.colunas}, cavalo em {jogo.cavalo})")
        print(f"  {'algoritmo':<10} {'resultado':<10} {'passos':>7} "
              f"{'expandidos':>11} {'descobertos':>12} {'tempo (ms)':>11}")

        for chave, rotulo in ALGORITMOS:
            t0 = time.perf_counter()
            r = getattr(jogo, f"busca_{chave}")()
            ms = (time.perf_counter() - t0) * 1000

            resultado = "fuga" if r["caminho"] else "preso"
            passos = r["tamanho_caminho"] if r["tamanho_caminho"] is not None else "-"
            print(f"  {rotulo:<10} {resultado:<10} {str(passos):>7} "
                  f"{r['expandidos']:>11} {r['descobertos']:>12} {ms:>11.2f}")

        area, pontuacao, itens = jogo.calcular_pontuacao()
        print(f"  area acessivel ao cavalo: {area} celulas | "
              f"pontuacao da area: {pontuacao} | itens: {itens}")

    print("\n" + "=" * 78)


if __name__ == "__main__":
    main()
