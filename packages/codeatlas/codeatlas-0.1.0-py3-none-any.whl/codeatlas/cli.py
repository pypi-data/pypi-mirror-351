# codeatlas/cli.py

import argparse
from .graph_builder import build_project_graph
from .visualizer import visualize_graph

def main():
    parser = argparse.ArgumentParser(description="Generate a code graph from a Python project.")
    parser.add_argument("--path", type=str, required=True, help="Path to the Python project.")
    parser.add_argument("--output", type=str, required=True, help="Output image filename.")
    args = parser.parse_args()

    graph = build_project_graph(args.path)
    visualize_graph(graph, args.output)
