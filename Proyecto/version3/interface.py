import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from airSpace import AirSpace



class AirspaceGUI:
    def __init__(self, master):
        self.master = master
        self.airspace = AirSpace()
        self.current_path = None

        # Configuración de la ventana
        master.title("Airspace Navigator v3")
        master.geometry("1200x800")

        # Panel de control
        control_frame = ttk.Frame(master)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Botones de carga
        ttk.Button(control_frame, text="Cargar Catalunya",
                   command=lambda: self.load_airspace("Cat")).pack(pady=5)
        ttk.Button(control_frame, text="Cargar España",
                   command=lambda: self.load_airspace("Spain")).pack(pady=5)
        ttk.Button(control_frame, text="Cargar Europa",
                   command=lambda: self.load_airspace("Eur")).pack(pady=5)

        # Selectores de nodos
        ttk.Label(control_frame, text="Nodo Origen:").pack(pady=5)
        self.origin_combo = ttk.Combobox(control_frame)
        self.origin_combo.pack()

        ttk.Label(control_frame, text="Nodo Destino:").pack(pady=5)
        self.dest_combo = ttk.Combobox(control_frame)
        self.dest_combo.pack()

        # Botones de funcionalidad
        ttk.Button(control_frame, text="Mostrar Vecinos",
                   command=self.show_neighbors).pack(pady=5)
        ttk.Button(control_frame, text="Ruta Más Corta",
                   command=self.find_shortest_path).pack(pady=5)

        # Área de gráficos
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def load_airspace(self, region):
        base_path = f"data/{region}_"
        try:
            self.airspace.load_airspace_data(
                f"{base_path}nav.txt",
                f"{base_path}seg.txt",
                f"{base_path}aer.txt"
            )
            # Verificación de carga
            if not self.airspace.NavPoints:
                raise ValueError("No se cargaron puntos de navegación")
            if not self.airspace.NavSegments:
                raise ValueError("No se cargaron segmentos")

            print(f"Cargados: {len(self.airspace.NavPoints)} puntos, {len(self.airspace.NavSegments)} segmentos")
            self.airspace.print_connections()  # Depuración

            self.update_combos()
            self.plot_airspace()
            tk.messagebox.showinfo("Éxito", "Datos cargados correctamente")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error cargando datos: {str(e)}")

    def update_combos(self):
        """Actualiza los combos con nombres de nodos"""
        nodes = []
        for p in self.airspace.NavPoints:
            display_text = f"{p.name} ({p.code})"
            nodes.append(display_text)
            # Depuración: mostrar lo que se está añadiendo al Combobox
            print(f"Añadiendo al Combobox: '{display_text}'")

        self.origin_combo["values"] = nodes
        self.dest_combo["values"] = nodes

    def plot_airspace(self):
        self.ax.clear()

        # Dibujar segmentos primero
        for point in self.airspace.NavPoints:
            for neighbor, distance in point.get_neighbors():
                self.ax.plot(
                    [point.longitude, neighbor.longitude],
                    [point.latitude, neighbor.latitude],
                    'gray', alpha=0.5
                )

        # Luego dibujar nodos
        for point in self.airspace.NavPoints:
            self.ax.plot(
                point.longitude,
                point.latitude,
                'o',
                markersize=8 if any(n for n in point.neighbors) else 5,
                color='blue' if point.neighbors else 'red'
            )

        self.ax.set_xlabel("Longitud")
        self.ax.set_ylabel("Latitud")
        self.canvas.draw()

    def show_neighbors(self):
        """Muestra los vecinos del nodo seleccionado"""
        selection = self.origin_combo.get()
        if not selection:
            tk.messagebox.showwarning("Advertencia", "Seleccione un nodo primero")
            return

        # Extraer el código del nodo de forma más robusta
        try:
            # Buscar el código entre paréntesis
            code = selection.split('(')[-1].split(')')[0].strip()
            if not code:
                raise ValueError
        except:
            tk.messagebox.showerror("Error", "Formato de nodo incorrecto")
            return

        # Depuración: mostrar qué código se está buscando
        print(f"Buscando nodo con código/ID: '{code}'")

        # Intentar encontrar el nodo primero por código (ID numérico)
        try:
            nav_point = self.airspace.get_navpoint_by_name_or_id(int(code))
        except ValueError:
            # Si no es numérico, buscar por nombre
            nav_point = self.airspace.get_navpoint_by_name_or_id(code)

        # Depuración: mostrar resultados de búsqueda
        if nav_point:
            print(f"Nodo encontrado: {nav_point.name} (ID: {nav_point.code})")
        else:
            print("Nodo NO encontrado")
            # Mostrar todos los nodos disponibles para diagnóstico
            print("Nodos disponibles:")
            for point in self.airspace.NavPoints:
                print(f" - {point.name} (ID: {point.code})")

        if not nav_point:
            tk.messagebox.showerror("Error", "Nodo no encontrado")
            return

        # Resto del método permanece igual...
        neighbors = nav_point.get_neighbors()
        self.ax.clear()

        # Dibujar todos los segmentos en gris
        for seg in self.airspace.NavSegments:
            origin = self.airspace.get_navpoint_by_name_or_id(seg.origin)
            dest = self.airspace.get_navpoint_by_name_or_id(seg.destination)
            if origin and dest:
                self.ax.plot(
                    [origin.longitude, dest.longitude],
                    [origin.latitude, dest.latitude],
                    'gray', alpha=0.3
                )

        # Dibujar todos los nodos en azul
        for point in self.airspace.NavPoints:
            self.ax.plot(
                point.longitude,
                point.latitude,
                'o',
                markersize=5,
                color='blue'
            )

        # Resaltar el nodo seleccionado en rojo
        self.ax.plot(
            nav_point.longitude,
            nav_point.latitude,
            'o',
            markersize=7,
            color='red'
        )

        # Dibujar conexiones con vecinos en verde
        for neighbor, distance in neighbors:
            self.ax.plot(
                [nav_point.longitude, neighbor.longitude],
                [nav_point.latitude, neighbor.latitude],
                'green', linewidth=2
            )
            # Resaltar nodos vecinos en amarillo
            self.ax.plot(
                neighbor.longitude,
                neighbor.latitude,
                'o',
                markersize=6,
                color='yellow'
            )

        # Mostrar información de vecinos
        neighbor_info = "\n".join([f"{n.name} ({distance:.2f} km)" for n, distance in neighbors])
        if neighbor_info:
            info_text = f"Vecinos de {nav_point.name}:\n{neighbor_info}"
        else:
            info_text = f"{nav_point.name} no tiene vecinos"

        self.ax.set_title(info_text, fontsize=10)
        self.ax.set_xlabel("Longitud")
        self.ax.set_ylabel("Latitud")
        self.canvas.draw()
        tk.messagebox.showinfo("Vecinos", info_text)

    def find_shortest_path(self):
        """Calcula y muestra la ruta más corta"""
        # Verificar que hay datos cargados
        if not self.airspace.NavPoints:
            tk.messagebox.showerror("Error", "Primero cargue los datos de navegación")
            return

        # Obtener selecciones
        origin_selection = self.origin_combo.get()
        dest_selection = self.dest_combo.get()

        if not origin_selection or not dest_selection:
            tk.messagebox.showerror("Error", "Seleccione origen y destino")
            return

        try:
            # Extraer códigos de forma robusta
            origin_code = origin_selection.split('(')[-1].split(')')[0].strip()
            dest_code = dest_selection.split('(')[-1].split(')')[0].strip()

            # Depuración
            print(f"\nBuscando ruta desde: '{origin_code}' hasta: '{dest_code}'")

            # Intentar convertir a int si es numérico
            try:
                origin_code = int(origin_code)
            except ValueError:
                pass

            try:
                dest_code = int(dest_code)
            except ValueError:
                pass

            # Verificar que existen los nodos
            origin_node = self.airspace.get_navpoint_by_name_or_id(origin_code)
            dest_node = self.airspace.get_navpoint_by_name_or_id(dest_code)

            if not origin_node:
                tk.messagebox.showerror("Error", f"Nodo origen '{origin_code}' no encontrado")
                return
            if not dest_node:
                tk.messagebox.showerror("Error", f"Nodo destino '{dest_code}' no encontrado")
                return

            # Depuración
            print(f"Origen encontrado: {origin_node.name} (ID: {origin_node.code})")
            print(f"Destino encontrado: {dest_node.name} (ID: {dest_node.code})")

            # Buscar ruta
            path, cost = self.airspace.find_shortest_path(origin_code, dest_code)

            # Depuración
            print(f"Resultado de búsqueda: path={path}, cost={cost}")

            if path and cost is not None:
                print("Ruta encontrada:")
                for p in path:
                    print(f" - {p.name} (ID: {p.code})")
                self.highlight_path(path)
                tk.messagebox.showinfo("Ruta Encontrada", f"Distancia total: {cost:.2f} km")
            else:
                tk.messagebox.showerror("Error", "No se encontró ruta entre los puntos seleccionados")

        except Exception as e:
            tk.messagebox.showerror("Error", f"Error al buscar ruta: {str(e)}")
            print(f"Error completo: {e}")

    def highlight_path(self, path):
        """Resalta la ruta en el gráfico mostrando solo distancias y nodo destino"""
        # Limpiar el gráfico antes de dibujar la nueva ruta
        self.ax.clear()

        # Redibujar todo el espacio aéreo
        # Dibujar segmentos primero
        for point in self.airspace.NavPoints:
            for neighbor, distance in point.get_neighbors():
                self.ax.plot(
                    [point.longitude, neighbor.longitude],
                    [point.latitude, neighbor.latitude],
                    'gray', alpha=0.5
                )

        # Dibujar nodos
        for point in self.airspace.NavPoints:
            self.ax.plot(
                point.longitude,
                point.latitude,
                'o',
                markersize=8 if any(n for n in point.neighbors) else 5,
                color='blue' if point.neighbors else 'red'
            )

        # Dibujar la ruta encontrada en verde
        lons = [p.longitude for p in path]
        lats = [p.latitude for p in path]
        self.ax.plot(lons, lats, 'g-', linewidth=3)

        # Resaltar nodos de la ruta (origen en rojo, destino en amarillo)
        if path:
            # Marcar origen (primer nodo)
            self.ax.plot(path[0].longitude, path[0].latitude, 'yo', markersize=8)

            # Marcar destino (último nodo)
            dest = path[-1]
            self.ax.plot(dest.longitude, dest.latitude, 'yo', markersize=8)


        # Mostrar distancias entre nodos consecutivos
        for i in range(len(path) - 1):
            p1 = path[i]
            p2 = path[i + 1]

            # Calcular punto medio para la etiqueta
            mid_lon = (p1.longitude + p2.longitude) / 2
            mid_lat = (p1.latitude + p2.latitude) / 2

            # Obtener distancia
            distance = None
            for neighbor, dist in p1.get_neighbors():
                if neighbor.code == p2.code:
                    distance = dist
                    break

            if distance:
                self.ax.text(mid_lon, mid_lat, f"{distance:.1f} km",
                             fontsize=9, bbox=dict(facecolor='white', alpha=0.8))

        self.ax.set_xlabel("Longitud")
        self.ax.set_ylabel("Latitud")
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = AirspaceGUI(root)
    root.mainloop()