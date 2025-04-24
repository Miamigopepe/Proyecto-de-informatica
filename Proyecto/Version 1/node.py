class Node:
    def __init__(self, name, coordinate_x, coordinate_y):
        self.name = name
        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y
        self.list_of_neighbors = []

def AddNeighbor(n1,n2):

    if n2 not in n1.list_of_neighbors:
            n1.list_of_neighbors.append(n2)
            return True
    else:
            return False

def Distance(n1,n2):
    distance = ((n1.coordinate_x - n2.coordinate_x) ** 2 +
                (n1.coordinate_y - n2.coordinate_y) ** 2) ** 0.5
    return distance



