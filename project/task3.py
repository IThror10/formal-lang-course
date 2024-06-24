from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton as DFA,
    NondeterministicFiniteAutomaton as NFA,
    State,
    Symbol,
)
from networkx import MultiDiGraph
from scipy.sparse import dok_matrix, kron
from typing import Iterable
from functools import reduce

from project.task2 import regex_to_dfa, graph_to_nfa


class FiniteAutomaton:
    def __init__(self, fa=None) -> None:
        self.lbl = True
        self.matrices = {}
        if fa is None:
            self.start_states = set()
            self.final_states = set()
            self.state_to_index = {}
            return

        self.start_states = fa.start_states
        self.final_states = fa.final_states

        self.state_to_index = {state: index for index, state in enumerate(fa.states)}
        self.index_to_state = {
            index: state for state, index in self.state_to_index.items()
        }
        n_states = len(fa.states)

        for from_state, transitions in fa.to_dict().items():
            for symbol, to_states in transitions.items():
                if symbol not in self.matrices.keys():
                    self.matrices[symbol] = dok_matrix((n_states, n_states), dtype=bool)
                if isinstance(fa, DFA):
                    self.matrices[symbol][
                        self.state_to_index[from_state], self.state_to_index[to_states]
                    ] = True
                else:
                    for to_state in to_states:
                        self.matrices[symbol][
                            self.state_to_index[from_state],
                            self.state_to_index[to_state],
                        ] = True

    def to_nfa(self) -> NFA:
        nfa = NFA()

        for state in self.start_states:
            nfa.add_start_state(state)

        for state in self.final_states:
            nfa.add_final_state(state)

        for label, matrix in self.matrices.items():
            n, m = matrix.shape
            for from_state in range(n):
                for to_state in range(m):
                    if matrix[from_state, to_state]:
                        nfa.add_transition(State(from_state), label, State(to_state))

        return nfa

    def set_state_to_index(self, new_state_to_index):
        self.state_to_index = new_state_to_index
        self.index_to_state = {
            index: state for state, index in self.state_to_index.items()
        }

    def set_true(self, label, row, column):
        self.matrices[label][row, column] = True

    def add_label_if_not_exist(self, label, dim=None):
        if label not in self.matrices:
            dim = dim or len(self)
            self.matrices[label] = dok_matrix((dim, dim), dtype=bool)

    def accepts(self, word: Iterable[Symbol]) -> bool:
        return self.to_nfa().accepts(word)

    def is_empty(self) -> bool:
        return self.to_nfa().is_empty()

    def get_index(self, state) -> int:
        return self.state_to_index.get(state, 0)

    def get_state_by_index(self, index: int):
        return self.index_to_state[index]

    def __len__(self):
        return len(self.state_to_index)

    def labels(self):
        return self.state_to_index.keys() if self.lbl else self.matrices.keys()

    def get_transitive_closure(self):
        if len(self.matrices.values()) == 0:
            return dok_matrix((0, 0), dtype=bool)

        closure = reduce(lambda x, y: x + y, self.matrices.values())

        while True:
            prev_zero_count = closure.count_nonzero()
            closure += closure @ closure
            if prev_zero_count == closure.count_nonzero():
                return closure


def intersect_automata(
    auto1: FiniteAutomaton, auto2: FiniteAutomaton, lbl: bool = True
) -> FiniteAutomaton:
    auto1.lbl = auto2.lbl = not lbl
    res = FiniteAutomaton()

    for state1, index1 in auto1.state_to_index.items():
        for state2, index2 in auto2.state_to_index.items():
            index = len(auto2) * index1 + index2
            res.state_to_index[index] = index

            if state1 in auto1.start_states and state2 in auto2.start_states:
                res.start_states.add(State(index))

            if state1 in auto1.final_states and state2 in auto2.final_states:
                res.final_states.add(State(index))

    labels = auto1.labels() & auto2.labels()
    for label in labels:
        res.matrices[label] = kron(auto1.matrices[label], auto2.matrices[label], "csr")

    return res


def paths_ends(
    graph: MultiDiGraph, start: set[int], final: set[int], regex: str
) -> list[tuple[object, object]]:
    dfa = FiniteAutomaton(regex_to_dfa(regex))
    nfa = FiniteAutomaton(graph_to_nfa(graph, start, final))
    intersection = intersect_automata(nfa, dfa, lbl=False)

    if intersection.is_empty():
        return []

    from_states, to_states = intersection.get_transitive_closure().nonzero()
    n = len(dfa)

    return [
        (nfa.get_state_by_index(from_state // n), nfa.get_state_by_index(to_state // n))
        for from_state, to_state in zip(from_states, to_states)
        if from_state in intersection.start_states
        and to_state in intersection.final_states
    ]
