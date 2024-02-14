import cfpq_data
from cfpq_data.graphs.generators import labeled_two_cycles_graph
from networkx.drawing.nx_pydot import write_dot


def getGraphInfoByName(graphName: str):
    graph_csv = cfpq_data.download(graphName)
    graph = cfpq_data.graph_from_csv(graph_csv)
    return (
        graph.number_of_nodes(),
        graph.number_of_edges(),
        set(map(lambda x: x[2]["label"], graph.edges(data=True))),
    )


def createBiSycleGraph(cSize1: int, cSize2: int, labels: set[str], path: str):
    graph = labeled_two_cycles_graph(n=cSize1, m=cSize2, labels=labels)
    print(path)
    write_dot(graph, path)
