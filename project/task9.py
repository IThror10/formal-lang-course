from pyformlang.rsa import RecursiveAutomaton
from pyformlang.cfg import CFG
from pyformlang.finite_automaton import State, Symbol
import networkx as nx

from copy import deepcopy

from project.task8 import cfg_to_rsm


def cfpq_with_gll(
    rsm: CFG | RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes=None,
    final_nodes=None,
):

    if not isinstance(rsm, RecursiveAutomaton):
        rsm = cfg_to_rsm(rsm)

    start_nodes = graph.nodes if start_nodes is None else start_nodes
    final_nodes = graph.nodes if final_nodes is None else final_nodes

    result = set()
    label = "S" if rsm.initial_label.value is None else rsm.initial_label.value

    dfa_state = rsm.boxes[label].dfa.start_state.value
    dfa = rsm.boxes[label].dfa.to_dict()
    dfa.setdefault(State(dfa_state), dict())

    stack = {(v, label): set() for v in start_nodes}
    visited = {(v, (dfa_state, label), (v, label)) for v in start_nodes}
    queue = deepcopy(visited)

    def addVisit(node, rsm_context, stack_context):
        s = (node, rsm_context, stack_context)
        if s not in visited:
            visited.add(s)
            queue.add(s)

    while len(queue) > 0:
        v, (_, _), (stack_node, stack_label) = queue.pop()
        stack_state = (stack_node, stack_label)

        if stack_node in start_nodes and stack_label == dfa_state and v in final_nodes:
            result.add((stack_node, v))

        for states in stack.setdefault(stack_state, set()):
            addVisit(v, states[0], states[1])

        for symbol, _ in dfa.items():
            if symbol in rsm.labels:
                start_sym_state = rsm.boxes[symbol].dfa.start_state.value
                rsm_state_ = (start_sym_state, symbol.value)
                stack_state_ = (v, symbol.value)
                addVisit(v, rsm_state_, stack_state_)
    return result
