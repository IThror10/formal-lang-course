from project.lang.project.languageVisitor import languageVisitor
from project.lang.project.languageLexer import languageLexer
from project.lang.project.languageParser import languageParser

from antlr4 import *
from antlr4.InputStream import InputStream


class NodeCounter(languageVisitor):
    def __init__(self):
        super().__init__()
        self.counter = 0

    def enterEveryRule(self, _):
        self.counter += 1


class TreeToProgVisitor(languageVisitor):
    def __init__(self):
        super().__init__()
        self.visits = []

    def enterEveryRule(self, rule):
        self.visits.append(rule.get_text())


def nodes_count(tree: ParserRuleContext) -> int:
    visitor = NodeCounter()
    tree.accept(visitor)
    return visitor.counter


def tree_to_prog(tree: ParserRuleContext) -> str:
    visitor = TreeToProgVisitor()
    tree.accept(visitor)
    return "".join(visitor.visits)


def prog_to_tree(program: str) -> tuple[ParserRuleContext, bool]:
    parser = languageParser(CommonTokenStream(languageLexer(InputStream(program))))
    return parser.prog(), parser.getNumberOfSyntaxErrors() == 0
