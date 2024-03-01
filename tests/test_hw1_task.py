import pytest

from tempfile import NamedTemporaryFile
from project.hw1.task import createBiSycleGraph, getGraphInfoByName


def test_get_graph_info_by_bzip_name():
    nodes, edge, labels = getGraphInfoByName("bzip")
    assert nodes == 632
    assert edge == 556
    assert labels == {"a", "d"}


def test_get_graph_info_by_biomedical_name():
    nodes, edge, labels = getGraphInfoByName("biomedical")
    assert nodes == 341
    assert edge == 459
    assert labels == {
        "type",
        "label",
        "subClassOf",
        "comment",
        "versionInfo",
        "title",
        "language",
        "publisher",
        "description",
        "creator",
    }


def test_create_bisycle_graph():
    target = ["digraph  {"]
    for i in [1, 2, 3, 0]:
        target.append(f"{i};")
    for j in range(3, 8):
        target.append(f"{(j + 1)};")
    for i in [(1, 2), (2, 3), (3, 0), (0, 1)]:
        target.append(f"{i[0]} -> {i[1]}  [key=0, label=a];")
    for j in [(0, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 0)]:
        target.append(f"{j[0]} -> {j[1]}  [key=0, label=b];")
    target.append("}")
    target.append("")

    with NamedTemporaryFile("w+") as tmp:
        createBiSycleGraph(3, 5, ("a", "b"), tmp.name)
        result = tmp.read()
        assert result == "\n".join(target)
