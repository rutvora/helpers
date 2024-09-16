import json
import subprocess
import os
import pydot
import argparse

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
            if "vpos" not in node["title"] or node["title"]["vpos"] not in ["top", "mid", "bottom"]:
                node["title"]["vpos"] = "top"

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

        if "start" not in edge or not isinstance(edge["start"], str) or edge["start"] not in node_children:
            print("No start node found for edge. Skipping edge...")
            edge.clear()
            return None
        if "end" not in edge or not isinstance(edge["end"], str) or edge["end"] not in node_children:
            print("No end node found for edge. Skipping edge...")
            edge.clear()
            return None

        if is_child(edge["start"], node_children[edge["end"]]) or is_child(edge["end"], node_children[edge["start"]]):
            print("You are trying to draw an edge between a parent and its child. Skipping edge...")
            edge.clear()
            return None

        if "text" not in edge or not isinstance(edge["text"], str) or edge["text"] == "":
            edge["text"] = None
        if "arrow" not in edge or edge["arrow"] not in [0, 1, 2]:
            edge["arrow"] = 0

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


if __name__ == "__main__":
    # Set the working directory
    root_dir = execute_program(["git", "rev-parse", "--show-superproject-working-tree"])
    if root_dir == "":
        root_dir = execute_program(["git", "rev-parse", "--show-toplevel"])
    root_dir = root_dir.strip('\n')
    main()
