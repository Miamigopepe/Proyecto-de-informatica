def calculate_distance(origin_node, destination_node):
    dx = origin_node.coordinate_x - destination_node.coordinate_x
    dy = origin_node.coordinate_y - destination_node.coordinate_y
    return (dx**2 + dy**2)**0.5


class Segment:
    def __init__(self, name, origin_node, destination_node):
        self.name = name
        self.origin = origin_node
        self.destination = destination_node
        self.cost = calculate_distance(origin_node, destination_node)

    def __str__(self):
            return f"Segment {self.name}: {self.origin.name} -> {self.destination.name}, Cost: {self.cost:.2f}"

