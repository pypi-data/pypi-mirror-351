import matplotlib.pyplot as plt
import networkx as nx

def visualize_graph(graph, output_file):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_size=500, node_color="skyblue", font_size=8, arrows=True)
    plt.savefig(output_file)
    plt.close()
