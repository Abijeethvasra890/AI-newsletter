from google.adk.graph import Graph
from google.adk.nodes import Node
from google.adk.conditions import Condition

from agents.collector_agent import collector_node
from agents.ranker import ranker_node
from agents.extractor import extractor_node
from agents.writer import writer_node
from agents.quality import quality_node
from agents.formatter import formatter_node
from agents.sender import sender_node
from agents.archive import archive_node


def quality_below_threshold(state):
    return state.quality_score is not None and state.quality_score < 8


def build_newsletter_graph():

    graph = Graph()

    graph.add_nodes([
        collector_node,
        ranker_node,
        extractor_node,
        writer_node,
        quality_node,
        formatter_node,
        sender_node,
        archive_node
    ])

    graph.connect(collector_node, ranker_node)
    graph.connect(ranker_node, extractor_node)
    graph.connect(extractor_node, writer_node)
    graph.connect(writer_node, quality_node)

    # Conditional edge
    graph.connect(
        quality_node,
        writer_node,
        condition=Condition(quality_below_threshold)
    )

    graph.connect(
        quality_node,
        formatter_node,
        condition=Condition(lambda state: state.quality_score >= 8)
    )

    graph.connect(formatter_node, sender_node)
    graph.connect(sender_node, archive_node)

    return graph
