from scipy.sparse import lil_matrix
from pyformlang.cfg import CFG, Terminal
import networkx as nx
from typing import Set, Tuple
from project.task6 import cfg_to_weak_normal_form


def cfpq_with_matrix(cfg, graph, start_nodes=None, final_nodes=None):
    wnf = cfg_to_weak_normal_form(cfg)
    mapVarIndex = {
        variable: index
        for index, variable in enumerate(
            {production.head for production in wnf.productions}
        )
    }

    matrices = {}
    n = graph.number_of_nodes()
    for production in wnf.productions:
        matrices[production.head] = lil_matrix((n, n), dtype=bool)
        if len(production.body) == 1 and isinstance(production.body[0], Terminal):
            for start, end, label in graph.edges.data("label"):
                if str(production.body[0]) == str(label):
                    matrices[production.head][start, end] = True

    changed = True
    while changed:
        changed = False
        for production in wnf.productions:
            if (
                len(production.body) == 2
                and production.body[0] in mapVarIndex
                and production.body[1] in mapVarIndex
            ):
                prev = matrices[production.head].nnz
                matrices[production.head] += (
                    matrices[production.body[0]] * matrices[production.body[1]]
                )
                changed = changed or (prev != matrices[production.head].nnz)

    return {
        (row, column)
        for variable, matrix in matrices.items()
        for row, column in zip(matrix.tocoo().row, matrix.tocoo().col)
        if variable == wnf.start_symbol
        and (start_nodes is None or row in start_nodes)
        and (final_nodes is None or column in final_nodes)
    }
