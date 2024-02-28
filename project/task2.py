from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State, Symbol
from networkx import MultiDiGraph


def regex_to_dfa(regex):
    return Regex(regex).to_epsilon_nfa().minimize()


def graph_to_nfa(graph: MultiDiGraph, start_states: set, final_states: set):
    nDfa = NondeterministicFiniteAutomaton()
    graphNodes = set(graph.nodes())

    for cur in start_states.union(graphNodes):
        nDfa.add_start_state(State(cur))
    for cur in final_states.union(graphNodes):
        nDfa.add_final_state(State(cur))

    for start, end, label in graph.edges.data("label"):
        nDfa.add_transition(State(start), Symbol(label), State(end))
    return nDfa
