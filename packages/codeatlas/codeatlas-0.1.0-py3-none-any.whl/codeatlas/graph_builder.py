import os
import networkx as nx

def build_graph(analysis):
    G = nx.DiGraph()
    for file in analysis:
        file_node = file["file"]
        G.add_node(file_node, type="file")

        for cls in file["classes"]:
            cls_node = f"{file_node}:{cls}"
            G.add_node(cls_node, type="class")
            G.add_edge(file_node, cls_node)

        for fn in file["functions"]:
            fn_node = f"{file_node}:{fn}"
            G.add_node(fn_node, type="function")
            G.add_edge(file_node, fn_node)

    return G

def analyze_project(path):
    """
    Analyze the Python project folder to extract files, classes, and functions.
    Returns a list of dictionaries with file, classes, and functions info.
    """
    analysis = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                classes = []
                functions = []

                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                for line in lines:
                    line = line.strip()
                    if line.startswith("class "):
                        cls_name = line.split()[1].split("(")[0]
                        classes.append(cls_name)
                    elif line.startswith("def "):
                        fn_name = line.split()[1].split("(")[0]
                        functions.append(fn_name)

                analysis.append({
                    "file": file_path,
                    "classes": classes,
                    "functions": functions
                })

    return analysis

def build_project_graph(path):
    """
    Main function called from CLI to build graph from project path.
    """
    analysis = analyze_project(path)
    graph = build_graph(analysis)
    return graph
