import matplotlib.pyplot as plt
import math
from segment import Segment
from node import Node

class Graph:
    def __init__(self):
        self.nodes = []
        self.segments = []

    def AddNode(self, node):
        if any(n.name == node.name for n in self.nodes):
            return False
        else:
            self.nodes.append(node)
            return True

    def AddSegment(self, segment_name, name_origin, name_destination):
        # Encontrar nodos
        origin = None
        destination = None
       #Compravar si esta los nodos
        for node in self.nodes:
            if node.name == name_origin:
                origin = node
            if node.name == name_destination:
                destination = node
      #si no esta decimos q es falso
        if not origin or not destination:
            return False

        # Crear segmento
        new_segment = Segment(segment_name, origin, destination)
        self.segments.append(new_segment)

        # Actualizar vecinos (bidireccional)
        # if destination not in origin.list_of_neighbors:
        #     origin.list_of_neighbors.append(destination)
        # if origin not in destination.list_of_neighbors:
        #     destination.list_of_neighbors.append(origin)

        return True

    def GetClosest(self, x, y):
        """
        Retornar los nodos


        """
        # comprovacion de si esta vacio
        if not self.nodes:
            return None

        closest_node = self.nodes[0]
        # asegurar distancia que sea mas pequeños
        min_distance = math.inf

        for node in self.nodes:
            # calulo de todas las distancias uno por uno del nodo con el punto
            dx = node.coordinate_x - x
            dy = node.coordinate_y - y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance < min_distance:
                min_distance = distance
                # node es objeto de node.py
                closest_node = node

        return closest_node

    def Plot(self):
        """El grafico"""

        # Plot de los nodos
        for node in self.nodes:
            # Marca de bola azul b=blue o de circulo
            plt.plot(node.coordinate_x, node.coordinate_y, 'bo', markersize=10)
            plt.text(node.coordinate_x, node.coordinate_y + 0.5, node.name,
                     ha='center', va='center', fontsize=9, fontweight='bold')

        # Plot de segmentos
        for segment in self.segments:

            x_values = [segment.origin.coordinate_x, segment.destination.coordinate_x]
            y_values = [segment.origin.coordinate_y, segment.destination.coordinate_y]
            # Lineals negras k- con opacidad 0.7 para que no se note tanto
            plt.plot(x_values, y_values, 'k-', alpha=0.7)

            # Add cost label at midpoint
            mid_x = sum(x_values) / 2
            mid_y = sum(y_values) / 2
            # cajas de texto
            plt.text(mid_x, mid_y, f"{segment.cost:.1f}",
                     bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
                     ha='center', va='center')

        #Creamos Rejillas
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.title("Grafico de la ostia", pad=20)
        plt.tight_layout()
        plt.show()

    def PlotNode(self, node_name):
        """
        Cosas a cumplir:
        - Origin node in blue
        - Neighbors in green
        - Other nodes in gray
        - Connecting segments in red with costs
        Returns False if node doesn't exist, True otherwise

        """
        #Asignamos uno origin el node

        origin = None
        for node in self.nodes:
            if node.name == node_name:
                origin = node
                break

        # Si no existe el nodo, retornar False
        if not origin:
            return False


        # Plot todos en remarca gris
        for node in self.nodes:
            plt.plot(node.coordinate_x, node.coordinate_y, 'o',
                     markersize=8, color='gray', alpha=0.3)
            plt.text(node.coordinate_x, node.coordinate_y + 0.5, node.name,
                     ha='center', va='center', fontsize=9)

        # REmarcar las origenes en azul
        plt.plot(origin.coordinate_x, origin.coordinate_y, 'o',
                 markersize=12, color='blue')
        plt.text(origin.coordinate_x, origin.coordinate_y + 0.7, origin.name,
                 ha='center', va='center', fontweight='bold', fontsize=10)

        # Remarcar neighbor en green
        for neighbor in origin.list_of_neighbors:
            plt.plot(neighbor.coordinate_x, neighbor.coordinate_y, 'o',
                     markersize=12, color='green')
            plt.text(neighbor.coordinate_x, neighbor.coordinate_y + 0.7, neighbor.name,
                     ha='center', va='center', fontweight='bold', fontsize=10)

        # segmentos rayas discontinuas
        for segment in self.segments:
            x_values = [segment.origin.coordinate_x, segment.destination.coordinate_x]
            y_values = [segment.origin.coordinate_y, segment.destination.coordinate_y]
            plt.plot(x_values, y_values, 'k-', alpha=0.2)

        # Los segmentos connectados remarcados con linia continua rojo
        for segment in self.segments:
            if (segment.origin == origin or segment.destination == origin):
                x_values = [segment.origin.coordinate_x, segment.destination.coordinate_x]
                y_values = [segment.origin.coordinate_y, segment.destination.coordinate_y]
                plt.plot(x_values, y_values, 'r-', linewidth=2)

                # adir los label del cost
                mid_x = sum(x_values) / 2
                mid_y = sum(y_values) / 2
                plt.text(mid_x, mid_y, f"{segment.cost:.1f}",
                         bbox=dict(facecolor='white', alpha=0.8, edgecolor='red'),
                         ha='center', va='center')

        plt.grid(True, linestyle='--', alpha=0.5)
        plt.title(f"Graph Visualization - Node {node_name} and its Neighbors", pad=20)
        plt.tight_layout()
        plt.show()
        return True


"""
def LoadGraphFromFile(self, filename):
  
    try:
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if not parts:
                    continue

                if parts[0] == "NODE" and len(parts) == 4:
                    name, x, y = parts[1], float(parts[2]), float(parts[3])
                    self.AddNode(Node(name, x, y))

                elif parts[0] == "SEGMENT" and len(parts) == 4:
                    seg_name, origin, dest = parts[1], parts[2], parts[3]
                    self.AddSegment(seg_name, origin, dest)

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return False
    except Exception as e:
        print(f"Error loading graph: {str(e)}")
        return False

    return True



   


"""
#Loads graph data from a text file with format:
  #NODE <name> <x> <y>
  #SEGMENT <name> <origin> <destination>