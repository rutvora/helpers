import json
import subprocess
import os
from pydot import Node, Edge, Dot, Subgraph, Cluster
import argparse
from copy import deepcopy

colors = {
    "magenta": "#ffadad",
    "orange": "#ffd6a5",
    "yellow": "#fdffb6",
    "green": "#caffbf",
    "cyan": "#9bf6ff",
    "blue": "#a0c4ff",
    "purple": "#bdb2ff",
    "pink": "#ffc6ff",
    "white": "#ffffff",
}
# DO NOT MODIFY THESE VARIABLES
color_iter = iter(colors.values())


class Pydot:
    def __init__(self, config: dict):
        self.graph = Dot(config["title"], graph_type='digraph', bgcolor="transparent", compound="true")
        self.nodes = {}
        self.edges = {}
        self.config = config
        self.common_attr = {
            "fontname": "Arial",
            "fontsize": "20",
            "style": "filled",
        }
        self.default_node_attr = {
            "margin": "0.3",
        }
        self.default_cluster_attr = {
            "margin": "5",
        }
        self.default_edge_attr = {
        }

    def draw_nodes(self, graph, nodes: list):
        color = get_next_color()
        for node in nodes:
            if len(node["children"]) == 0:
                common_attr = deepcopy(self.common_attr)
                node_attr = deepcopy(self.default_node_attr)
                node_attr["labelloc"] = f"{node['title']['vpos']}"
                node_attr["fillcolor"] = color
                drawn_cluster = Node(node["id"], label=node["title"]["text"], shape="box", **common_attr, **node_attr)
                graph.add_node(drawn_cluster)
            else:
                common_attr = deepcopy(self.common_attr)
                cluster_attr = deepcopy(self.default_cluster_attr)
                cluster_attr["labelloc"] = f"{node['title']['vpos']}"
                cluster_attr["labeljust"] = f"{node['title']['hpos']}"
                cluster_attr["fillcolor"] = color
                drawn_cluster = Cluster(node["id"], label=node["title"]["text"], shape="box", **common_attr,
                                        **cluster_attr)
                self.draw_nodes(drawn_cluster, node["children"])
                graph.add_subgraph(drawn_cluster)

    def draw_edges(self, edges: list):
        for edge in edges:
            common_attr = deepcopy(self.common_attr)
            edge_attr = deepcopy(self.default_edge_attr)
            if edge["text"] is not None:
                edge_attr["label"] = edge["text"]
                edge_attr["dir"] = "arrow"
            if "ltail" in edge:
                edge_attr["ltail"] = edge["ltail"]
            if "lhead" in edge:
                edge_attr["lhead"] = edge["lhead"]
            drawn_edge = Edge(edge["start"]["id"], edge["end"]["id"], **common_attr, **edge_attr)
            self.graph.add_edge(drawn_edge)

    def draw(self):
        self.draw_nodes(self.graph, self.config["nodes"])
        self.draw_edges(self.config["edges"])

        return self.graph


def get_next_color():
    global color_iter
    color = next(color_iter, None)
    if color is None:
        color_iter = iter(colors.values())
        color = next(color_iter)
    return color


def execute_program(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e}")
        print(e.output)
        return e.output


def parse_arguments():
    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description='Run multiple experiments with different configurations')

    # Add arguments
    parser.add_argument("-c", "--configs", default="diagrams.json",
                        help='The configuration file for the plot')
    parser.add_argument("-d", "--dir", default=None,
                        help='(Optional) The directory relative to which the paths are in the plot_config')

    # Return the params
    return parser.parse_args()


def check_config(config: dict):
    node_children = {}

    # Define a function to check for nodes
    def check_node(node: dict, parent: str):
        # TODO: Add support for duplicating a node (with new IDs)
        if "id" not in node:
            print("No ID found for node. Skipping node...")
            node.clear()
            return None
        node_id = node["id"]
        if node_id in node_children:
            print(f"Duplicated IDs {node_id}. Skipping the duplicate node...")
            node.clear()
            return None

        # Set this node in node_children with no children
        node_children[node_id] = []
        # Set this node as a child of the parent
        node_children[parent].append(node_id)

        if (
                "title" not in node
                or not isinstance(node["title"], dict)
                or node["title"]["text"] is None
                or node["title"]["text"] == ""
                or not isinstance(node["title"]["text"], str)
        ):
            node["title"] = None
        else:
            if "hpos" not in node["title"] or node["title"]["hpos"] not in ["left", "center", "right"]:
                node["title"]["hpos"] = "center"
            if node["title"]["hpos"] == "left":
                node["title"]["hpos"] = "l"
            elif node["title"]["hpos"] == "center":
                node["title"]["hpos"] = "c"
            elif node["title"]["hpos"] == "right":
                node["title"]["hpos"] = "r"

            if "vpos" not in node["title"] or node["title"]["vpos"] not in ["top", "mid", "bottom"]:
                node["title"]["vpos"] = "top"
            if node["title"]["vpos"] == "top":
                node["title"]["vpos"] = "t"
            elif node["title"]["vpos"] == "mid":
                node["title"]["vpos"] = "c"
            elif node["title"]["vpos"] == "bottom":
                node["title"]["vpos"] = "b"

        if "children" not in node or not isinstance(node["children"], list):
            node["children"] = []
        for child in node["children"]:
            check_node(child, node_id)
        node["children"] = [child for child in node["children"] if child]

    # Define a function to check for edges
    def check_edge(edge: dict):

        def is_child(node_id: str, children: list):
            if node_id in children:
                return True
            for child in children:
                if is_child(node_id, node_children[child]):
                    return True
            return False

        if (
                "start" not in edge
                or not isinstance(edge["start"], dict)
                or "id" not in edge["start"]
                or edge["start"]["id"] not in node_children
        ):
            print(f"No start node {edge['start']['id']} found for edge. Skipping edge...")
            edge.clear()
            return None
        if (
                "end" not in edge
                or not isinstance(edge["end"], dict)
                or "id" not in edge["end"]
                or edge["end"]["id"] not in node_children
        ):
            print(f"No end node {edge['end']['id']} found for edge. Skipping edge...")
            edge.clear()
            return None

        if is_child(edge["start"]["id"], node_children[edge["end"]["id"]]) or is_child(edge["end"]["id"], node_children[
            edge["start"]["id"]]):
            print("You are trying to draw an edge between a parent and its child. Skipping edge...")
            edge.clear()
            return None

        # Set lhead and ltail if start or end are clusters
        if len(node_children[edge["start"]["id"]]) > 0:
            edge["ltail"] = "cluster_" + edge["start"]["id"]
            edge["start"]["id"] = node_children[edge["start"]["id"]][0]
        if len(node_children[edge["end"]["id"]]) > 0:
            edge["lhead"] = "cluster_" + edge["end"]["id"]
            edge["end"]["id"] = node_children[edge["end"]["id"]][0]

        if "text" not in edge or not isinstance(edge["text"], str) or edge["text"] == "":
            edge["text"] = None

        if "pos" in edge["start"] and edge["start"]["pos"] in ['n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw']:
            edge["start"]["id"] += ":" + edge["start"]["pos"]
        if "pos" in edge["end"] and edge["end"]["pos"] in ['n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw']:
            edge["end"]["id"] += ":" + edge["end"]["pos"]

        if "arrow" not in edge or edge["arrow"] not in [0, 1, 2]:
            edge["arrow"] = 0
        if edge["arrow"] == 0:
            edge["arrow"] = "none"
        elif edge["arrow"] == 1:
            edge["arrow"] = "forward"
        elif edge["arrow"] == 2:
            edge["arrow"] = "both"

    node_children["root"] = []
    for node in config["nodes"]:
        check_node(node, "root")
    for edge in config["edges"]:
        check_edge(edge)

    # Remove all empty nodes and edges (which were cleared, as they were invalid)
    config["nodes"] = [node for node in config["nodes"] if node]
    config["edges"] = [edge for edge in config["edges"] if edge]


def main():
    global root_dir
    args = parse_arguments()
    if args.dir is not None:
        root_dir = args.dir
    os.chdir(root_dir)
    with open(args.configs, "r") as f:
        configs = json.load(f)

    if not isinstance(configs, list):
        configs = [configs]
    for config in configs:
        if "title" not in config:
            print("One of your configs is missing a title. Skipping diagram...")
        print(f"\nStarting diagram {config['title']}")
        if check_config(config) == -1:
            print("No results file found. Skipping plot...")
            continue
        diagram = Pydot(config).draw()
        if not os.path.exists(os.path.join(root_dir, "diagrams")):
            os.makedirs("diagrams")
        diagram.write(path=f"{os.path.join('diagrams', config['title'])}.svg", format="svg")


if __name__ == "__main__":
    # Set the working directory
    root_dir = execute_program(["git", "rev-parse", "--show-superproject-working-tree"])
    if root_dir == "":
        root_dir = execute_program(["git", "rev-parse", "--show-toplevel"])
    root_dir = root_dir.strip('\n')
    main()
