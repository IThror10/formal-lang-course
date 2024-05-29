from pyformlang.cfg import CFG, Variable, Terminal, Epsilon

from collections import defaultdict
from typing import Tuple


def cfg_to_weak_normal_form(initCfg, start="S") -> CFG:
    elimCfg = initCfg.eliminate_unit_productions().remove_useless_symbols()
    return CFG(
        productions=set(
            elimCfg._decompose_productions(
                elimCfg._get_productions_with_only_single_terminals()
            )
        ),
        start_symbol=Variable(start),
    )


def cfpq_with_hellings(cfg, graph, start_nodes=None, final_nodes=None):
    terminal, epsilon, mult, temp = defaultdict(set), set(), defaultdict(set), set()
    for prod in cfg_to_weak_normal_form(cfg).productions:
        if len(prod.body) == 2:
            mult[prod.head].add((prod.body[0], prod.body[1]))
        elif len(prod.body) == 1 and isinstance(prod.body[0], Terminal):
            terminal[prod.head].add(prod.body[0])
        elif len(prod.body) == 1 and isinstance(prod.body[0], Epsilon):
            epsilon.add(prod.body[0])

    cur = {
        (n, start, end)
        for (start, end, label) in graph.edges.data("label")
        for n in terminal
        if label in terminal[n]
    }.union({(n, node, node) for n in epsilon for node in graph.nodes})

    copy = cur.copy()
    while len(copy) != 0:
        n1, v1, u1 = copy.pop()
        for n2, v2, u2 in cur:
            if v1 == u2:
                for N_k in mult:
                    if (n2, n1) in mult[N_k] and (N_k, v2, v1) not in r:
                        copy.add((N_k, v2, u1))
                        temp.add((N_k, v2, u1))

    return {
        (start, end)
        for (n, start, end) in cur.union(temp)
        if Variable(n) == cfg.start_symbol
        and (start_nodes is None or start in start_nodes)
        and (final_nodes is None or end in final_nodes)
    }


def read_cfgrammar(filePath, start="S"):
    with open(filePath, "r") as file:
        return CFG.from_text(file.read(), Variable(start))
