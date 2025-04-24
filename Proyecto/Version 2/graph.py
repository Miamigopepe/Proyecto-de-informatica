import matplotlib.pyplot as plt
from node import Node, Distance
from segment import Segment
from path import Path


class Graph:
    def __init__(self):
        self.nodes = []
        self.segments = []

    def add_node(self, node):
        if any(n.name == node.name for n in self.nodes):
            return False
        self.nodes.append(node)
        return True

    def add_segment(self, segment_name, name_origin, name_destination):
        origin = next((n for n in self.nodes if n.name == name_origin), None)
        destination = next((n for n in self.nodes if n.name == name_destination), None)

        if not origin or not destination:
            return False

        if any(s.name == segment_name for s in self.segments):
            return False

        new_segment = Segment(segment_name, origin, destination)
        self.segments.append(new_segment)
        return True

    def get_reachable_nodes(self, start_node_name):
        start_node = next((n for n in self.nodes if n.name == start_node_name), None)
        if not start_node:
            return None

        visited = set()
        queue = [start_node]
        reachable = []

        while queue:
            current = queue.pop(0)
            if current not in visited:
                visited.add(current)
                reachable.append(current)
                for neighbor in current.list_of_neighbors:
                    if neighbor not in visited:
                        queue.append(neighbor)

        return reachable

    def find_shortest_path(self, origin_name, destination_name):
        origin = next((n for n in self.nodes if n.name == origin_name), None)
        destination = next((n for n in self.nodes if n.name == destination_name), None)

        if not origin or not destination:
            return None

        # A* algorithm
        open_set = {origin}
        came_from = {}
        g_score = {n: float('inf') for n in self.nodes}
        g_score[origin] = 0
        f_score = {n: float('inf') for n in self.nodes}
        f_score[origin] = Distance(origin, destination)

        while open_set:
            current = min(open_set, key=lambda n: f_score[n])

            if current == destination:
                path_nodes = []
                while current in came_from:
                    path_nodes.insert(0, current)
                    current = came_from[current]
                path_nodes.insert(0, origin)
                return Path(path_nodes)

            open_set.remove(current)

            for neighbor in current.list_of_neighbors:
                tentative_g_score = g_score[current] + Distance(current, neighbor)

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + Distance(neighbor, destination)
                    if neighbor not in open_set:
                        open_set.add(neighbor)

        return None

    def plot(self, highlight_nodes=None, highlight_path=None):
        fig, ax = plt.subplots(figsize=(10, 8))

        # Plot all nodes
        for node in self.nodes:
            color = 'gray'  # Default color
            if highlight_nodes and node in highlight_nodes:
                color = 'blue' if node == highlight_nodes[0] else 'green'
            elif highlight_path and node in highlight_path.nodes:
                color = 'red'

            ax.plot(node.coordinate_x, node.coordinate_y, 'o', markersize=10, color=color)
            ax.text(node.coordinate_x, node.coordinate_y + 0.5, node.name,
                    ha='center', va='center', fontsize=9)

        # Ponerlos con flechas
        for segment in self.segments:
            x = [segment.origin.coordinate_x, segment.destination.coordinate_x]
            y = [segment.origin.coordinate_y, segment.destination.coordinate_y]

            # Determine line color
            line_color = 'black'
            if highlight_path and highlight_path.nodes:
                for i in range(len(highlight_path.nodes) - 1):
                    if (segment.origin == highlight_path.nodes[i] and
                            segment.destination == highlight_path.nodes[i + 1]):
                        line_color = 'red'
                        break
            elif highlight_nodes:
                if (segment.origin in highlight_nodes and
                        segment.destination in highlight_nodes):
                    line_color = 'green'
                elif (segment.origin == highlight_nodes[0] or
                      segment.destination == highlight_nodes[0]):
                    line_color = 'blue'

            ax.annotate('', xy=(x[1], y[1]), xytext=(x[0], y[0]),
                        arrowprops=dict(arrowstyle='->', color=line_color, alpha=0.7))

            # Pone nombre y coste
            mid_x = sum(x) / 2
            mid_y = sum(y) / 2
            ax.text(mid_x, mid_y, f"{segment.name}\n{segment.cost:.2f}",
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
                    ha='center', va='center')

        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_title("Graph Visualization")
        plt.tight_layout()
        plt.show()

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if not parts:
                        continue

                    if parts[0] == "NODE" and len(parts) == 4:
                        name, x, y = parts[1], float(parts[2]), float(parts[3])
                        self.add_node(Node(name, x, y))
                    elif parts[0] == "SEGMENT" and len(parts) == 4:
                        seg_name, origin, dest = parts[1], parts[2], parts[3]
                        self.add_segment(seg_name, origin, dest)
            return True
        except Exception as e:
            print(f"Error loading graph: {str(e)}")
            return False

    def save_to_file(self, filename):
        try:
            with open(filename, 'w') as f:
                # Escribir los nodos
                for node in self.nodes:
                    f.write(f"NODE {node.name} {node.coordinate_x} {node.coordinate_y}\n")

                # segmentos en el doc
                for segment in self.segments:
                    f.write(f"SEGMENT {segment.name} {segment.origin.name} {segment.destination.name}\n")
            return True
        except Exception as e:
            print(f"Error saving graph: {str(e)}")
            return False