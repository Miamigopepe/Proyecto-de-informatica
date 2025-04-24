import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from graph import Graph
from node import Node
from segment import Segment
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GraphEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Editor - Version 2")
        self.root.geometry("1200x800")

        self.current_graph = Graph()
        self.setup_ui()
        self.create_example_graph()

    def setup_ui(self):
        self.control_frame = tk.Frame(self.root, padx=10, pady=10, width=300)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.display_frame = tk.Frame(self.root)
        self.display_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.create_graph_management_controls()
        self.create_node_operations_controls()
        self.create_segment_operations_controls()
        self.create_visualization_controls()
        self.create_version2_features()
        self.figure = plt.Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.display_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        self.canvas.mpl_connect('button_press_event', self.on_canvas_click)

    def create_version2_features(self):
        frame = tk.LabelFrame(self.control_frame, text="Version 2 Features", padx=5, pady=5)
        frame.pack(fill=tk.X, pady=5)

        tk.Button(frame, text="Show Reachable Nodes",
                  command=self.show_reachable_nodes).pack(fill=tk.X, pady=2)
        tk.Button(frame, text="Find Shortest Path",
                  command=self.find_shortest_path).pack(fill=tk.X, pady=2)

    def show_reachable_nodes(self):
        selection = self.node_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No node selected")
            return

        node_name = self.node_listbox.get(selection[0]).split()[0]
        reachable = self.current_graph.get_reachable_nodes(node_name)

        if not reachable:
            messagebox.showinfo("Reachable Nodes", "No reachable nodes found")
            return

        self.plot_graph(highlight_nodes=reachable)
        messagebox.showinfo("Reachable Nodes",
                            f"Nodes reachable from {node_name}:\n" +
                            "\n".join([n.name for n in reachable]))

    def find_shortest_path(self):
        if len(self.current_graph.nodes) < 2:
            messagebox.showwarning("Warning", "Need at least 2 nodes to find a path")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Find Shortest Path")
        dialog.geometry("300x200")

        tk.Label(dialog, text="Origin Node:").pack(pady=5)
        origin_var = tk.StringVar(dialog)
        origin_var.set(self.current_graph.nodes[0].name)
        origin_menu = tk.OptionMenu(dialog, origin_var, *[n.name for n in self.current_graph.nodes])
        origin_menu.pack(pady=5)

        tk.Label(dialog, text="Destination Node:").pack(pady=5)
        dest_var = tk.StringVar(dialog)
        dest_var.set(self.current_graph.nodes[1].name if len(self.current_graph.nodes) > 1 else "")
        dest_menu = tk.OptionMenu(dialog, dest_var, *[n.name for n in self.current_graph.nodes])
        dest_menu.pack(pady=5)

        def find_path():
            origin = origin_var.get()
            destination = dest_var.get()

            path = self.current_graph.find_shortest_path(origin, destination)

            if path:
                self.plot_graph(highlight_path=path)
                messagebox.showinfo("Shortest Path",
                                    f"Shortest path found:\n{str(path)}")
            else:
                messagebox.showinfo("Shortest Path",
                                    f"No path exists from {origin} to {destination}")
            dialog.destroy()

        tk.Button(dialog, text="Find Path", command=find_path).pack(pady=10)

    def create_graph_management_controls(self):
        frame = tk.LabelFrame(self.control_frame, text="Graph Management", padx=5, pady=5)
        frame.pack(fill=tk.X, pady=5)

        tk.Button(frame, text="New Graph", command=self.new_graph).pack(fill=tk.X, pady=2)
        tk.Button(frame, text="Load Graph", command=self.load_graph).pack(fill=tk.X, pady=2)
        tk.Button(frame, text="Save Graph", command=self.save_graph).pack(fill=tk.X, pady=2)
        tk.Button(frame, text="Show Example", command=self.show_example).pack(fill=tk.X, pady=2)

    def create_node_operations_controls(self):
        frame = tk.LabelFrame(self.control_frame, text="Node Operations", padx=5, pady=5)
        frame.pack(fill=tk.X, pady=5)

        tk.Button(frame, text="Add Node", command=self.add_node_dialog).pack(fill=tk.X, pady=2)
        tk.Button(frame, text="Delete Node", command=self.delete_node_dialog).pack(fill=tk.X, pady=2)

        self.node_listbox = tk.Listbox(frame, height=8)
        self.node_listbox.pack(fill=tk.X, pady=5)
        self.node_listbox.bind('<<ListboxSelect>>', self.on_node_select)

    def create_segment_operations_controls(self):
        frame = tk.LabelFrame(self.control_frame, text="Segment Operations", padx=5, pady=5)
        frame.pack(fill=tk.X, pady=5)

        tk.Button(frame, text="Add Segment", command=self.add_segment_dialog).pack(fill=tk.X, pady=2)
        tk.Button(frame, text="Delete Segment", command=self.delete_segment_dialog).pack(fill=tk.X, pady=2)

        self.segment_listbox = tk.Listbox(frame, height=8)
        self.segment_listbox.pack(fill=tk.X, pady=5)

    def create_visualization_controls(self):
        frame = tk.LabelFrame(self.control_frame, text="Visualization", padx=5, pady=5)
        frame.pack(fill=tk.X, pady=5)

        tk.Button(frame, text="Highlight Neighbors", command=self.highlight_neighbors).pack(fill=tk.X, pady=2)
        tk.Button(frame, text="Reset View", command=self.plot_graph).pack(fill=tk.X, pady=2)

    def create_example_graph(self):
        #Grafico ejemplo
        self.example_graph = Graph()
        # Add nodes
        self.example_graph.add_node(Node("A", 1, 20))
        self.example_graph.add_node(Node("B", 8, 17))
        self.example_graph.add_node(Node("C", 15, 20))
        self.example_graph.add_node(Node("D", 18, 15))
        self.example_graph.add_node(Node("E", 2, 4))
        self.example_graph.add_node(Node("F", 6, 5))
        # Add segments
        self.example_graph.add_segment("AB", "A", "B")
        self.example_graph.add_segment("BA", "B", "A")
        self.example_graph.add_segment("BC", "B", "C")
        self.example_graph.add_segment("CB", "C", "B")
        self.example_graph.add_segment("CD", "C", "D")
        self.example_graph.add_segment("AE", "A", "E")
        self.example_graph.add_segment("EA", "E", "A")
        self.example_graph.add_segment("EF", "E", "F")
        self.example_graph.add_segment("FE", "F", "E")
        self.example_graph.add_segment("BF", "B", "F")
        self.example_graph.add_segment("FB", "F", "B")

    def new_graph(self):
        """Create a new empty graph"""
        self.current_graph = Graph()
        self.update_lists()
        self.plot_graph()
        messagebox.showinfo("New Graph", "Created new empty graph")

    def load_graph(self):
        """Load graph from file"""
        filepath = filedialog.askopenfilename(title="Select Graph File",
                                              filetypes=[("Text files", "*.txt")])
        if filepath:
            new_graph = Graph()
            if new_graph.load_from_file(filepath):
                self.current_graph = new_graph
                self.update_lists()
                self.plot_graph()
                messagebox.showinfo("Success", f"Graph loaded from {filepath}")
            else:
                messagebox.showerror("Error", "Failed to load graph from file")

    def save_graph(self):
        """Save graph to file"""
        if not self.current_graph.nodes:
            messagebox.showwarning("Warning", "Cannot save empty graph")
            return

        filepath = filedialog.asksaveasfilename(title="Save Graph As",
                                                defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt")])
        if filepath:
            if self.current_graph.save_to_file(filepath):
                messagebox.showinfo("Success", f"Graph saved to {filepath}")
            else:
                messagebox.showerror("Error", "Failed to save graph")

    def show_example(self):
        """Load the example graph"""
        self.current_graph = self.example_graph
        self.update_lists()
        self.plot_graph()
        messagebox.showinfo("Example Graph", "Loaded example graph")

    def add_node_dialog(self):
        """Show dialog to add a new node"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Node")
        dialog.geometry("300x200")

        tk.Label(dialog, text="Node Name:").pack(pady=5)
        name_entry = tk.Entry(dialog)
        name_entry.pack(pady=5)

        tk.Label(dialog, text="X Coordinate:").pack(pady=5)
        x_entry = tk.Entry(dialog)
        x_entry.pack(pady=5)

        tk.Label(dialog, text="Y Coordinate:").pack(pady=5)
        y_entry = tk.Entry(dialog)
        y_entry.pack(pady=5)

        def add_node():
            try:
                name = name_entry.get()
                x = float(x_entry.get())
                y = float(y_entry.get())

                if any(n.name == name for n in self.current_graph.nodes):
                    messagebox.showerror("Error", "Node with this name already exists")
                    return

                self.current_graph.add_node(Node(name, x, y))
                self.update_lists()
                self.plot_graph()
                dialog.destroy()
                messagebox.showinfo("Success", "Node added successfully")
            except ValueError:
                messagebox.showerror("Error", "Invalid coordinates - must be numbers")

        tk.Button(dialog, text="Add Node", command=add_node).pack(pady=10)

    def on_canvas_click(self, event):
        """Handle clicks on the canvas to add nodes"""
        if event.inaxes is None:
            return

        if event.dblclick:  # Double click to add node
            name = simpledialog.askstring("Add Node", "Enter node name:")
            if name:
                if any(n.name == name for n in self.current_graph.nodes):
                    messagebox.showerror("Error", "Node with this name already exists")
                    return

                self.current_graph.add_node(Node(name, event.xdata, event.ydata))
                self.update_lists()
                self.plot_graph()

    def delete_node_dialog(self):
        """Delete the selected node"""
        selection = self.node_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No node selected")
            return

        node_name = self.node_listbox.get(selection[0]).split()[0]

        # Confirm deletion
        if messagebox.askyesno("Confirm", f"Delete node {node_name} and all connected segments?"):
            # Remove segments connected to this node
            self.current_graph.segments = [s for s in self.current_graph.segments
                                           if s.origin.name != node_name and s.destination.name != node_name]

            # Remove the node
            self.current_graph.nodes = [n for n in self.current_graph.nodes if n.name != node_name]

            self.update_lists()
            self.plot_graph()
            messagebox.showinfo("Success", f"Deleted node {node_name}")

    def on_node_select(self, event):
        """Handle node selection"""
        selection = self.node_listbox.curselection()
        if selection:
            node_name = self.node_listbox.get(selection[0]).split()[0]
            self.highlight_neighbors(node_name)

    def add_segment_dialog(self):
        """Show dialog to add a new segment"""
        if len(self.current_graph.nodes) < 2:
            messagebox.showwarning("Warning", "Need at least 2 nodes to create a segment")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Segment")
        dialog.geometry("300x200")

        tk.Label(dialog, text="Segment Name:").pack(pady=5)
        name_entry = tk.Entry(dialog)
        name_entry.pack(pady=5)

        tk.Label(dialog, text="Origin Node:").pack(pady=5)
        origin_var = tk.StringVar(dialog)
        origin_var.set(self.current_graph.nodes[0].name)
        origin_menu = tk.OptionMenu(dialog, origin_var, *[n.name for n in self.current_graph.nodes])
        origin_menu.pack(pady=5)

        tk.Label(dialog, text="Destination Node:").pack(pady=5)
        dest_var = tk.StringVar(dialog)
        dest_var.set(self.current_graph.nodes[1].name if len(self.current_graph.nodes) > 1 else "")
        dest_menu = tk.OptionMenu(dialog, dest_var, *[n.name for n in self.current_graph.nodes])
        dest_menu.pack(pady=5)

        def add_segment():
            name = name_entry.get()
            origin = origin_var.get()
            dest = dest_var.get()

            if origin == dest:
                messagebox.showerror("Error", "Origin and destination cannot be the same")
                return

            if any(s.name == name for s in self.current_graph.segments):
                messagebox.showerror("Error", "Segment with this name already exists")
                return

            if self.current_graph.add_segment(name, origin, dest):
                self.update_lists()
                self.plot_graph()
                dialog.destroy()
                messagebox.showinfo("Success", "Segment added successfully")
            else:
                messagebox.showerror("Error", "Failed to add segment")

        tk.Button(dialog, text="Add Segment", command=add_segment).pack(pady=10)

    def delete_segment_dialog(self):
        #eliminar sgment
        selection = self.segment_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No segment selected")
            return

        segment_name = self.segment_listbox.get(selection[0]).split(':')[0]

        if messagebox.askyesno("Confirm", f"Delete segment {segment_name}?"):
            self.current_graph.segments = [s for s in self.current_graph.segments if s.name != segment_name]
            self.update_lists()
            self.plot_graph()
            messagebox.showinfo("Success", f"Deleted segment {segment_name}")

    def highlight_neighbors(self, node_name=None):
        #Highlight neighbours
        if not node_name:
            selection = self.node_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "No node selected")
                return
            node_name = self.node_listbox.get(selection[0]).split()[0]

        node = next((n for n in self.current_graph.nodes if n.name == node_name), None)
        if not node:
            return

        neighbors = node.list_of_neighbors
        self.plot_graph(highlight_nodes=[node] + neighbors)

    def update_lists(self):
        #Uptade
        self.node_listbox.delete(0, tk.END)
        for node in sorted(self.current_graph.nodes, key=lambda n: n.name):
            self.node_listbox.insert(tk.END, f"{node.name} ({node.coordinate_x}, {node.coordinate_y})")

        self.segment_listbox.delete(0, tk.END)
        for segment in self.current_graph.segments:
            self.segment_listbox.insert(tk.END,
                                        f"{segment.name}: {segment.origin.name}->{segment.destination.name}")

    def plot_graph(self, highlight_nodes=None, highlight_path=None):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not self.current_graph.nodes:
            ax.text(0.5, 0.5, "Empty Graph\nAdd nodes to begin",
                    ha='center', va='center', fontsize=12)
            self.canvas.draw()
            return

        # Nodos
        for node in self.current_graph.nodes:
            color = 'gray'  # Default color

            if highlight_nodes and node in highlight_nodes:
                color = 'blue' if node == highlight_nodes[0] else 'green'
            elif highlight_path and node in highlight_path.nodes:
                color = 'red'

            ax.plot(node.coordinate_x, node.coordinate_y, 'o', markersize=10, color=color)
            ax.text(node.coordinate_x, node.coordinate_y + 0.5, node.name,
                    ha='center', va='center', fontsize=9)

        # Fletchas
        for segment in self.current_graph.segments:
            x = [segment.origin.coordinate_x, segment.destination.coordinate_x]
            y = [segment.origin.coordinate_y, segment.destination.coordinate_y]

            #  line color
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
                        arrowprops=dict(arrowstyle='->', color=line_color, alpha=0.7, linewidth=2))

            # Añadir nombre y coste
            mid_x = sum(x) / 2
            mid_y = sum(y) / 2
            ax.text(mid_x, mid_y, f"{segment.name}\n{segment.cost:.2f}",
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
                    ha='center', va='center')

        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_title("Graph Visualization")
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphEditor(root)
    root.mainloop()