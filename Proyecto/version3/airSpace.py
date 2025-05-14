from navPoint import NavPoint
from navAirport import NavAirport
from navSegment import NavSegment
from heapq import heappush, heappop

class AirSpace:
    def __init__(self):
        self.NavPoints = []  # List of NavPoint objects
        self.NavSegments = []  # List of NavSegment objects
        self.NavAirports = []  # List of NavAirport objects
        self._nav_points_dict = {}  # Internal lookup by name and ID

    def load_airspace_data(self, nav_file, seg_file, aer_file):
        """Load all airspace data from the three files"""
        self._load_nav_points(nav_file)
        self._load_segments(seg_file)
        self._load_airports(aer_file)
        self._validate_airspace()

    def _load_nav_points(self, nav_file):
        """Load navigation points from file"""
        with open(nav_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 4:
                    point_id = int(parts[0])
                    name = parts[1]
                    lat = float(parts[2])
                    lon = float(parts[3])
                    nav_point = NavPoint(point_id, name, lat, lon)
                    self.NavPoints.append(nav_point)
                    self._nav_points_dict[point_id] = nav_point
                    self._nav_points_dict[name] = nav_point  # Also index by name

    def _load_segments(self, seg_file):
        with open(seg_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    origin_id = int(parts[0])
                    dest_id = int(parts[1])
                    distance = float(parts[2])

                    if origin_id in self._nav_points_dict and dest_id in self._nav_points_dict:
                        segment = NavSegment(origin_id, dest_id, distance)
                        self.NavSegments.append(segment)

                        origin_point = self._nav_points_dict[origin_id]
                        dest_point = self._nav_points_dict[dest_id]
                        # Cambiar esta línea:
                        origin_point.add_neighbor((dest_point, distance))
                        # Asegurarse que add_neighbor recibe una tupla (NavPoint, distancia)

    def _load_airports(self, aer_file):
        """Load airport data with SIDs and STARs"""
        current_airport = None

        with open(aer_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Detect airport lines (ICAO codes are 4 uppercase letters)
                if len(line) == 4 and line.isupper():
                    current_airport = NavAirport(line)
                    self.NavAirports.append(current_airport)
                    continue

                if current_airport is None:
                    continue  # Skip lines before first airport

                # Process SIDs and STARs
                if '.' in line:  # SID or STAR indicator
                    point_name = line.split('.')[0]

                    # Find the nav point by name or ID
                    nav_point = self._nav_points_dict.get(point_name)
                    if nav_point is None:
                        # Try to find by partial name match (some names might have suffixes)
                        for name, point in self._nav_points_dict.items():
                            if isinstance(name, str) and name.startswith(point_name):
                                nav_point = point
                                break

                    if nav_point:
                        if line.endswith('.D'):  # Departure (SID)
                            current_airport.addSid(nav_point)
                        elif line.endswith('.A'):  # Arrival (STAR)
                            current_airport.addSTARs(nav_point)

    def _validate_airspace(self):
        """Validate the loaded airspace data"""
        # Check all segments reference existing points
        for segment in self.NavSegments:
            if segment.origin not in self._nav_points_dict:
                print(f"Warning: Segment references unknown origin ID {segment.origin}")
            if segment.destination not in self._nav_points_dict:
                print(f"Warning: Segment references unknown destination ID {segment.destination}")

        # Check all airports have at least one SID
        for airport in self.NavAirports:
            if not airport.SIDs:
                print(f"Warning: Airport {airport.name} has no SIDs")
            if not airport.STARs:
                print(f"Warning: Airport {airport.name} has no STARs")

    def get_airport_by_name(self, name):
        """Get airport by its ICAO code"""
        for airport in self.NavAirports:
            if airport.name == name:
                return airport
        return None

    def get_navpoint_by_name_or_id(self, identifier):
        """Get navigation point by either its name or ID"""
        return self._nav_points_dict.get(identifier)

    def get_neighbors(self, navpoint_id):
        """Obtiene los vecinos de un punto de navegación"""
        navpoint = self.get_navpoint_by_name_or_id(navpoint_id)
        if navpoint:
            return navpoint.neighbors
        return []

    def find_shortest_path(self, origin_name, destination_name):
        """Implementación mejorada del algoritmo A*"""
        start = self.get_navpoint_by_name_or_id(origin_name)
        goal = self.get_navpoint_by_name_or_id(destination_name)

        if not start or not goal:
            print("Error: Nodo origen o destino no encontrado")
            return [], None

        # Depuración
        print(f"\nIniciando búsqueda de ruta desde {start.name} a {goal.name}")
        print(f"Vecinos de origen: {[(n.name, d) for n, d in start.get_neighbors()]}")

        frontier = []
        heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        path_found = False

        while frontier:
            current = heappop(frontier)[1]

            if current == goal:
                path_found = True
                break

            for next_node, distance in current.get_neighbors():
                new_cost = cost_so_far[current] + distance
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + self._heuristic(goal, next_node)
                    heappush(frontier, (priority, next_node))
                    came_from[next_node] = current

        if not path_found:
            print("No se encontró ruta: el destino no fue alcanzado")
            return [], None

        path = self._reconstruct_path(came_from, start, goal)
        if not path:
            print("No se pudo reconstruir la ruta")
            return [], None

        print(f"Ruta encontrada con costo {cost_so_far[goal]:.2f} km")
        return path, cost_so_far[goal]

        if not path_found:
            # Verificar si los nodos están en componentes conexas diferentes
            reachable_from_start = set()
            stack = [start]
            while stack:
                node = stack.pop()
                if node not in reachable_from_start:
                    reachable_from_start.add(node)
                    for neighbor, _ in node.get_neighbors():
                        stack.append(neighbor)

            if goal not in reachable_from_start:
                print("Error: Origen y destino no están conectados")
                return [], None


    def _heuristic(self, a, b):
        """Distancia euclidiana entre dos puntos"""
        return ((a.latitude - b.latitude) ** 2 + (a.longitude - b.longitude) ** 2) ** 0.5

    def plot_airspace(self):
        """Genera un gráfico del espacio aéreo"""
        # Usar matplotlib para visualizar los puntos y conexiones
        pass

    def print_connections(self):
        """Método de depuración para ver las conexiones"""
        for point in self.NavPoints:
            print(f"Punto {point.name} ({point.code}) tiene {len(point.neighbors)} vecinos:")
            for neighbor, dist in point.neighbors:
                print(f"  -> {neighbor.name} ({dist} km)")

    def _reconstruct_path(self, came_from, start, goal):
        current = goal
        path = []

        # Protección contra bucles infinitos
        max_steps = len(came_from) * 2
        steps = 0

        while current != start:
            path.append(current)
            current = came_from.get(current)
            steps += 1

            if current is None:
                print("Error: Camino interrumpido, falta conexión")
                return None

            if steps > max_steps:
                print("Error: Posible bucle en la reconstrucción del camino")
                return None

        path.append(start)
        path.reverse()
        return path








