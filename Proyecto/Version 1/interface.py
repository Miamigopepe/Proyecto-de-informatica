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
        self.root.title("Graph Editor")
        self.root.geometry("1200x800")

        self.current_graph = Graph()
        self.setup_ui()
        self.create_example_graphs()

    def setup_ui(self):
        # Create main frames
        self.control_frame = tk.Frame(self.root, padx=10, pady=10, width=250)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.display_frame = tk.Frame(self.root)
        self.display_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Graph management section
        self.create_graph_management_section()

        # Node operations section
        self.create_node_operations_section()

        # Segment operations section
        self.create_segment_operations_section()

        # Visualization section
        self.create_visualization_section()

    def create_graph_management_section(self):
        frame = tk.LabelFrame(self.control_frame, text="Graph Management", padx=5, pady=5)
        frame.pack(fill=tk.X, pady=5)

        tk.Button(frame, text="New Graph", command=self.new_graph).pack(fill=tk.X, pady=2)
        tk.Button(frame, text="Load Graph", command=self.load_graph).pack(fill=tk.X, pady=2)
        tk.Button(frame, text="Save Graph", command=self.save_graph).pack(fill=tk.X, pady=2)
        tk.Button(frame, text="Show Example", command=self.show_example).pack(fill=tk.X, pady=2)

    def create_node_operations_section(self):
        frame = tk.LabelFrame(self.control_frame, text="Node Operations", padx=5, pady=5)
        frame.pack(fill=tk.X, pady=5)

        tk.Button(frame, text="Add Node", command=self.add_node_dialog).pack(fill=tk.X, pady=2)
        tk.Button(frame, text="Delete Node", command=self.delete_node_dialog).pack(fill=tk.X, pady=2)

        self.node_listbox = tk.Listbox(frame, height=8)
        self.node_listbox.pack(fill=tk.X, pady=5)
        self.node_listbox.bind('<<ListboxSelect>>', self.on_node_select)

    def create_segment_operations_section(self):
        frame = tk.LabelFrame(self.control_frame, text="Segment Operations", padx=5, pady=5)
        frame.pack(fill=tk.X, pady=5)

        tk.Button(frame, text="Add Segment", command=self.add_segment_dialog).pack(fill=tk.X, pady=2)
        tk.Button(frame, text="Delete Segment", command=self.delete_segment_dialog).pack(fill=tk.X, pady=2)

        self.segment_listbox = tk.Listbox(frame, height=8)
        self.segment_listbox.pack(fill=tk.X, pady=5)

    def create_visualization_section(self):
        frame = tk.LabelFrame(self.control_frame, text="Visualization", padx=5, pady=5)
        frame.pack(fill=tk.X, pady=5)

        tk.Button(frame, text="Highlight Neighbors", command=self.highlight_neighbors).pack(fill=tk.X, pady=2)
        tk.Button(frame, text="Reset View", command=self.plot_graph).pack(fill=tk.X, pady=2)

        # Matplotlib canvas
        self.figure = plt.Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.display_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

        # Click event for adding nodes by clicking
        self.canvas.mpl_connect('button_press_event', self.on_canvas_click)

    def create_example_graphs(self):
        """Create example graphs for quick loading"""
        self.example_graph = Graph()
        self.example_graph.AddNode(Node("A", 1, 20))
        self.example_graph.AddNode(Node("B", 8, 17))
        self.example_graph.AddSegment("AB", "A", "B")

    def update_lists(self):
        """Update the node and segment listboxes"""
        self.node_listbox.delete(0, tk.END)
        for node in sorted(self.current_graph.nodes, key=lambda n: n.name):
            self.node_listbox.insert(tk.END, f"{node.name} ({node.coordinate_x}, {node.coordinate_y})")

        self.segment_listbox.delete(0, tk.END)
        for segment in self.current_graph.segments:
            self.segment_listbox.insert(tk.END,
                                        f"{segment.name}: {segment.origin.name}->{segment.destination.name} ({segment.cost:.1f})")

    def plot_graph(self, highlight_node=None):
        """Plot the current graph with optional highlighting"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not self.current_graph.nodes:
            ax.text(0.5, 0.5, "Empty Graph\nAdd nodes to begin",
                    ha='center', va='center', fontsize=12)
            self.canvas.draw()
            return

        # Plot all nodes
        for node in self.current_graph.nodes:
            color = 'gray'  # Default color

            if highlight_node and node.name == highlight_node:
                color = 'blue'
            elif highlight_node and any(n.name == highlight_node for n in node.list_of_neighbors):
                color = 'green'

            ax.plot(node.coordinate_x, node.coordinate_y, 'o', markersize=10,
                    color=color, picker=5)
            ax.text(node.coordinate_x, node.coordinate_y + 0.5, node.name,
                    ha='center', va='center', fontsize=9)

        # Plot all segments
        for segment in self.current_graph.segments:
            x = [segment.origin.coordinate_x, segment.destination.coordinate_x]
            y = [segment.origin.coordinate_y, segment.destination.coordinate_y]

            line_color = 'red' if (highlight_node and
                                   (segment.origin.name == highlight_node or
                                    segment.destination.name == highlight_node)) else 'black'

            ax.plot(x, y, color=line_color, alpha=0.7)

            # Add cost label
            mid_x = sum(x) / 2
            mid_y = sum(y) / 2
            ax.text(mid_x, mid_y, f"{segment.cost:.1f}",
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
                    ha='center', va='center')

        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_title("Graph Visualization", pad=20)
        self.canvas.draw()

    # Graph operations
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
            if new_graph.LoadGraphFromFile(filepath):
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
            try:
                with open(filepath, 'w') as f:
                    # Write nodes
                    for node in self.current_graph.nodes:
                        f.write(f"NODE {node.name} {node.coordinate_x} {node.coordinate_y}\n")

                    # Write segments
                    for segment in self.current_graph.segments:
                        f.write(f"SEGMENT {segment.name} {segment.origin.name} {segment.destination.name}\n")

                messagebox.showinfo("Success", f"Graph saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save graph: {str(e)}")

    def show_example(self):
        """Load the example graph"""
        self.current_graph = self.example_graph
        self.update_lists()
        self.plot_graph()
        messagebox.showinfo("Example Graph", "Loaded example graph")

    # Node operations
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

                self.current_graph.AddNode(Node(name, x, y))
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

                self.current_graph.AddNode(Node(name, event.xdata, event.ydata))
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
            # Find and remove all segments connected to this node
            segments_to_remove = [s for s in self.current_graph.segments
                                  if s.origin.name == node_name or s.destination.name == node_name]

            for segment in segments_to_remove:
                # Remove from neighbors lists
                segment.origin.list_of_neighbors = [n for n in segment.origin.list_of_neighbors
                                                    if n.name != node_name]
                segment.destination.list_of_neighbors = [n for n in segment.destination.list_of_neighbors
                                                         if n.name != node_name]

            # Remove the segments
            self.current_graph.segments = [s for s in self.current_graph.segments
                                           if s not in segments_to_remove]

            # Remove the node
            self.current_graph.nodes = [n for n in self.current_graph.nodes
                                        if n.name != node_name]

            self.update_lists()
            self.plot_graph()
            messagebox.showinfo("Success", f"Deleted node {node_name} and {len(segments_to_remove)} segments")

    def on_node_select(self, event):
        """Handle node selection"""
        selection = self.node_listbox.curselection()
        if selection:
            node_name = self.node_listbox.get(selection[0]).split()[0]
            self.plot_graph(highlight_node=node_name)

    # Segment operations
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
        dest_var.set(self.current_graph.nodes[1].name)
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

            if self.current_graph.AddSegment(name, origin, dest):
                self.update_lists()
                self.plot_graph()
                dialog.destroy()
                messagebox.showinfo("Success", "Segment added successfully")
            else:
                messagebox.showerror("Error", "Failed to add segment")

        tk.Button(dialog, text="Add Segment", command=add_segment).pack(pady=10)

    def delete_segment_dialog(self):
        """Delete the selected segment"""
        selection = self.segment_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No segment selected")
            return

        segment_name = self.segment_listbox.get(selection[0]).split(':')[0]

        if messagebox.askyesno("Confirm", f"Delete segment {segment_name}?"):
            # Find and remove the segment
            segment = next((s for s in self.current_graph.segments if s.name == segment_name), None)

            if segment:
                # Remove from neighbors lists
                segment.origin.list_of_neighbors = [n for n in segment.origin.list_of_neighbors
                                                    if n.name != segment.destination.name]
                segment.destination.list_of_neighbors = [n for n in segment.destination.list_of_neighbors
                                                         if n.name != segment.origin.name]

                # Remove the segment
                self.current_graph.segments = [s for s in self.current_graph.segments
                                               if s.name != segment_name]

                self.update_lists()
                self.plot_graph()
                messagebox.showinfo("Success", f"Deleted segment {segment_name}")

    # Visualization operations
    def highlight_neighbors(self):
        """Highlight neighbors of selected node"""
        selection = self.node_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No node selected")
            return

        node_name = self.node_listbox.get(selection[0]).split()[0]
        self.plot_graph(highlight_node=node_name)


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphEditor(root)
    root.mainloop()