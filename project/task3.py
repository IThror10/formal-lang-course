from scipy.sparse import dok_matrix, kron
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton as DFA,
    NondeterministicFiniteAutomaton as NDFA,
    State,
)


class FiniteAutomaton:
    def __init__(self, dfa=None):
        if not isinstance(dfa, DFA) and not isinstance(dfa, NDFA):
            return

        states = dfa.to_dict()
        self.mapping = {v: i for i, v in enumerate(dfa.states)}
        self.sparse = dict()

        for label in dfa.symbols:
            self.sparse[label] = dok_matrix(
                (len(dfa.states), len(dfa.states)), dtype=bool
            )
            for u, edges in states.items():
                if label in edges:
                    for v in (
                        edges[label]
                        if isinstance(edges[label], set)
                        else {edges[label]}
                    ):
                        self.sparse[label][self.mapping[u], self.mapping[v]] = True

        self.start_states = dfa.start_states
        self.final_states = dfa.final_states

    def accepts(self, word):
        return self.to_ndfa().accepts("".join(list(word)))

    def is_empty(self):
        return len(self.sparse) == 0

    def mapping_for(self, u):
        return self.mapping[State(u)]

    def to_ndfa(self):
        ndfa = NDFA()
        for label in self.sparse.keys():
            m_size = self.sparse[label].shape[0]
            for u in range(m_size):
                for v in range(m_size):
                    if self.sparse[label][u, v]:
                        ndfa.add_transition(
                            self.mapping_for(u), label, self.mapping_for(v)
                        )

        for s in self.start_states:
            ndfa.add_start_state(self.mapping_for(s))
        for s in self.final_states:
            ndfa.add_final_state(self.mapping_for(s))
        return ndfa


def intersect_automata(fa1: FiniteAutomaton, fa2: FiniteAutomaton):
    labels = fa1.sparse.keys() & fa2.sparse.keys()
    fa = FiniteAutomaton()
    fa.sparse = dict()
    fa.start_states = set()
    fa.final_states = set()
    fa.mapping = dict()

    for label in labels:
        fa.sparse[label] = kron(fa1.sparse[label], fa2.sparse[label], "csr")

    for u, i in fa1.mapping.items():
        for v, j in fa2.mapping.items():

            k = len(fa2.mapping) * i + j
            fa.mapping[k] = k

            if u in fa1.start_states and v in fa2.start_states:
                fa.start_states.add(State(k))

            if u in fa1.final_states and v in fa2.final_states:
                fa.final_states.add(State(k))

    return fa
