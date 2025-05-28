class NavPoint:
    def __init__(self, code, name, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.name = name
        self.code = code
        self.neighbors = []

    def add_neighbor(self, neighbor_info):
       
        if isinstance(neighbor_info, tuple) and len(neighbor_info) == 2:
            neighbor, distance = neighbor_info
        else:
            # Si se llama con dos parámetros separados
            neighbor = neighbor_info
            distance = None

        if distance is None:
            raise ValueError("La distancia es requerida")

        # Verificar que neighbor sea un NavPoint
        if not hasattr(neighbor, 'code') or not hasattr(neighbor, 'name'):
            raise ValueError("El vecino debe ser un objeto NavPoint válido")

        # Eliminar conexión existente si la hay
        self.neighbors = [(n, d) for n, d in self.neighbors if n.code != neighbor.code]

        # Añadir la nueva conexión
        self.neighbors.append((neighbor, distance))

        print(f"DEBUG add_neighbor: {self.name} -> {neighbor.name} ({distance:.2f} km)")


    def get_neighbors(self):
        """Devuelve la lista de vecinos como tuplas (NavPoint, distancia)"""
        return self.neighbors
