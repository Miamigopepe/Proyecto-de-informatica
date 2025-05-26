class NavPoint:
    def __init__(self, code, name, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.name = name
        self.code = code
        self.neighbors = []

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def get_neighbors(self):
        return self.neighbors
