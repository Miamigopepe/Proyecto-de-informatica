from node import Distance, AddNeighbor

class Segment:
    def __init__(self, name, origin_node, destination_node):
        self.name = name
        self.origin = origin_node
        self.destination = destination_node
        self.cost = Distance(origin_node, destination_node)
        AddNeighbor(origin_node, destination_node)

    def __str__(self):
        return f"Segment {self.name}: {self.origin.name}->{self.destination.name} (Cost: {self.cost:.2f})"
