from node import Distance

class Path:
    def __init__(self, nodes=None):
        self.nodes = nodes if nodes else []
        self.cost = 0
        if nodes:
            for i in range(len(nodes)-1):
                self.cost += Distance(nodes[i], nodes[i+1])

    def add_node(self, node):
        if self.nodes:
            self.cost += Distance(self.nodes[-1], node)
        self.nodes.append(node)

    def contains_node(self, node):
        return node in self.nodes

    def cost_to_node(self, node):
        total_cost = 0
        for i in range(len(self.nodes)):
            if self.nodes[i] == node:
                return total_cost
            if i < len(self.nodes)-1:
                total_cost += Distance(self.nodes[i], self.nodes[i+1])
        return -1

    def copy(self):
        return Path(self.nodes.copy())

    def __str__(self):
        return " -> ".join([n.name for n in self.nodes]) + f" (Cost: {self.cost:.2f})"