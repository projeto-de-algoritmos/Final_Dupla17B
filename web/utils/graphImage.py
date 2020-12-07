import networkx as nx
import matplotlib.pyplot as plt
import io

class GraphImage(object): 
  
    # default constructor 
    def __init__(self, adjacency_list): 
        self.graph = nx.Graph()
        self.graph.add_nodes_from(list(adjacency_list.keys()))

        for node in list(adjacency_list.keys()):
            for edge in adjacency_list[node]:
                self.graph.add_edge(node,edge)

    def get_graph(self):
        return self.graph
    def render_graph_image(self):

        plt.figure(figsize=(20,20),dpi=400)
        plt.title("Group's movies and genres", fontsize=20)
        nx.draw_networkx(self.graph)
        img = io.BytesIO()
        plt.savefig(img, bbox_inches='tight')
        img.seek(0)
        plt.clf()
        return img

    def render_bipartide_graph_image(self, movies_list):

        plt.figure(figsize=(15,15),dpi=400)
        plt.title("Bipartide layout", fontsize=20)
        plt.margins(0.3)
        nx.draw_networkx(
            self.graph,
            pos = nx.drawing.layout.bipartite_layout(self.graph, movies_list))
        img = io.BytesIO()
        plt.savefig(img, bbox_inches='tight')
        img.seek(0)
        plt.clf()
        return img