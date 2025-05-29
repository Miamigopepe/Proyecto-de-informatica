import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from airSpace import AirSpace
from kml_generator import export_navpoints_to_kml, export_path_to_kml
from PIL import Image, ImageTk
import os
import pygame
from pygame import mixer
import math
from navSegment import NavSegment

class AirspaceGUI:
    def __init__(self, master):
        self.master = master
        self.airspace = AirSpace()
        self.current_path = None
        self.show_labels = tk.BooleanVar(value=False)
        self.hide_isolated = tk.BooleanVar(value=False)
        self.fake_screen_frame = None
        self.is_hiding = False
        self.fake_label = None
        self.playlist = []
        self.current_track = 0
        self.is_playing = False

        mixer.init()

        master.title("Airspace Navigator v3")
        master.geometry("1200x800")

        # Marco izquierdo para controles
        left_frame = ttk.Frame(master)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        control_frame = ttk.Frame(left_frame)
        control_frame.pack(side=tk.TOP, fill=tk.Y)

        # Marco de edición arriba
        edit_top_frame = ttk.LabelFrame(master, text="🛠️ Edición del Grafo")
        edit_top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        ttk.Button(edit_top_frame, text="Nuevo Grafo", command=self.new_graph).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(edit_top_frame, text="Añadir Nodo", command=self.add_node_dialog).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(edit_top_frame, text="Añadir Segmento", command=self.add_segment_dialog).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(edit_top_frame, text="Eliminar Nodo", command=self.remove_selected_node).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(edit_top_frame, text="Eliminar Segmento", command=self.remove_selected_segment).pack(side=tk.LEFT, padx=5, pady=2)

        # Listbox para ver nodos
        ttk.Label(edit_top_frame, text="Nodos existentes:").pack(side=tk.LEFT, padx=(20, 5))
        self.node_listbox = tk.Listbox(edit_top_frame, height=5, width=5)
        self.node_listbox.pack(side=tk.LEFT, padx=5, pady=2)

        # Listbox para ver segmentos
        ttk.Label(edit_top_frame, text="Segmentos existentes:").pack(side=tk.LEFT, padx=(20, 5))
        self.segment_listbox = tk.Listbox(edit_top_frame, height=5, width=10)
        self.segment_listbox.pack(side=tk.LEFT, padx=5, pady=2)

        # Botones funcionales
        ttk.Button(control_frame, text="Cargar Catalunya", command=lambda: self.load_airspace("Cat")).pack(pady=5)
        ttk.Button(control_frame, text="Cargar España", command=lambda: self.load_airspace("Spain")).pack(pady=5)
        ttk.Button(control_frame, text="Cargar Europa", command=lambda: self.load_airspace("Eur")).pack(pady=5)

        ttk.Label(control_frame, text="Nodo Origen:").pack(pady=5)
        self.origin_combo = ttk.Combobox(control_frame)
        self.origin_combo.pack()

        ttk.Label(control_frame, text="Nodo Destino:").pack(pady=5)
        self.dest_combo = ttk.Combobox(control_frame)
        self.dest_combo.pack()

        ttk.Button(control_frame, text="Mostrar Vecinos", command=self.show_neighbors).pack(pady=5)
        ttk.Button(control_frame, text="Ruta Más Corta", command=self.find_shortest_path).pack(pady=5)
        ttk.Button(control_frame, text="Exportar Puntos a KML", command=self.export_navpoints_kml).pack(pady=5)
        ttk.Button(control_frame, text="Exportar Ruta a KML", command=self.export_path_kml).pack(pady=5)
        ttk.Checkbutton(control_frame, text="Mostrar nombres", variable=self.show_labels, command=self.plot_airspace).pack(pady=5)
        ttk.Checkbutton(control_frame, text="Ocultar nodos sin vecinos", variable=self.hide_isolated, command=self.update_and_plot).pack(pady=5)
        ttk.Button(control_frame, text="Limpiar Ruta", command=self.clear_path).pack(pady=5)
        ttk.Button(control_frame, text="💻 Irse del trabajo", command=self.toggle_fake_screen).pack(pady=5)

        # Reproductor de música
        ttk.Label(control_frame, text="Reproductor de Música").pack(pady=5)
        ttk.Button(control_frame, text="Añadir Música", command=self.add_music).pack(pady=2)
        ttk.Button(control_frame, text="▶ Reproducir", command=self.play_music).pack(pady=2)
        ttk.Button(control_frame, text="⏸ Pausar", command=self.pause_music).pack(pady=2)
        ttk.Button(control_frame, text="⏹ Detener", command=self.stop_music).pack(pady=2)
        ttk.Button(control_frame, text="↪ Siguiente", command=self.next_track).pack(pady=2)
        ttk.Button(control_frame, text="↩ Anterior", command=self.prev_track).pack(pady=2)
        ttk.Button(control_frame, text="Mostrar Nodos Alcanzables", command=self.show_reachable_nodes).pack(pady=5)

        # Botón para mostrar imagen
        show_img_button = tk.Button(master, text="Mostrar Imagen", command=self.mostrar_imagen)
        show_img_button.pack(pady=10)

        # Área de gráficos
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect("button_press_event", self.on_plot_click)

        # Inicializar listas
        self.update_combos()

    def mostrar_imagen(self):
        image_path = os.path.join(os.path.dirname(__file__), "imagen grupazo.jpg")
        if os.path.exists(image_path):
            top = tk.Toplevel(self.master)
            top.title("Imagen")
            img = Image.open(image_path)
            img = img.resize((600, 400), Image.Resampling.LANCZOS)  # Cambiado aquí
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(top, image=photo)
            label.image = photo  # Necesario para evitar que se recolecte la imagen
            label.pack()
        else:
            messagebox.showerror("Error", f"No se encontró la imagen: {image_path}")

    def add_music(self):
        """Añade archivos de música a la playlist"""
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos de música",
            filetypes=[("Archivos de audio", "*.mp3 *.wav *.ogg")]
        )
        if files:
            self.playlist.extend(files)
            messagebox.showinfo("Playlist", f"Se añadieron {len(files)} canciones a la playlist")

    def play_music(self):
        """Reproduce la música actual o la playlist"""
        if not self.playlist:
            messagebox.showwarning("Advertencia", "La playlist está vacía")
            return

        try:
            if not self.is_playing:
                mixer.music.load(self.playlist[self.current_track])
                mixer.music.play()
                self.is_playing = True
                # Configurar un evento para pasar a la siguiente canción cuando termine
                mixer.music.set_endevent(pygame.USEREVENT)
                self.master.bind(pygame.USEREVENT, lambda e: self.next_track())
            else:
                mixer.music.unpause()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reproducir: {str(e)}")

    def pause_music(self):
        """Pausa la reproducción"""
        if self.is_playing:
            mixer.music.pause()
            self.is_playing = False

    def stop_music(self):
        """Detiene la reproducción"""
        mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        """Pasa a la siguiente canción"""
        if not self.playlist:
            return

        self.current_track = (self.current_track + 1) % len(self.playlist)
        self.stop_music()
        self.play_music()

    def prev_track(self):
        """Vuelve a la canción anterior"""
        if not self.playlist:
            return

        self.current_track = (self.current_track - 1) % len(self.playlist)
        self.stop_music()
        self.play_music()
    def load_airspace(self, region):
        self.airspace = AirSpace()  # Reiniciar el objeto airspace
        self.current_path = None  # Limpiar la ruta actual
        self.origin_combo.set('')  # Limpiar combobox origen
        self.dest_combo.set('')
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
            if self.hide_isolated.get() and not p.neighbors:
                continue
            display_text = f"{p.name} ({p.code})"
            nodes.append(display_text)

        # Actualizar listbox de nodos
        if hasattr(self, 'node_listbox'):
            self.node_listbox.delete(0, tk.END)
            for node in nodes:
                self.node_listbox.insert(tk.END, node)

        # Actualizar listbox de segmentos con información más detallada
        if hasattr(self, 'segment_listbox'):
            self.segment_listbox.delete(0, tk.END)
            for seg in self.airspace.NavSegments:
                # Buscar los nodos para mostrar nombres
                origin = self.airspace.get_navpoint_by_name_or_id(seg.origin)
                dest = self.airspace.get_navpoint_by_name_or_id(seg.destination)

                if origin and dest:
                    # Formato: "ID_origen -> ID_destino (nombre_origen -> nombre_destino)"
                    display_text = f"{seg.origin} -> {seg.destination}"
                    self.segment_listbox.insert(tk.END, display_text)
                else:
                    # Si no se encuentran los nodos, mostrar solo los IDs
                    display_text = f"{seg.origin} -> {seg.destination} (NODOS NO ENCONTRADOS)"
                    self.segment_listbox.insert(tk.END, display_text)

        # Actualizar comboboxes
        self.origin_combo["values"] = nodes
        self.dest_combo["values"] = nodes

    def plot_airspace(self):
        self.ax.clear()

        nodes_to_plot = []
        for point in self.airspace.NavPoints:
            if self.hide_isolated.get() and not point.neighbors:
                continue
            nodes_to_plot.append(point)

        # Dibujar segmentos (rutas)
        for point in nodes_to_plot:
            for neighbor, distance in point.get_neighbors():
                if neighbor in nodes_to_plot:
                    self.ax.plot(
                        [point.longitude, neighbor.longitude],
                        [point.latitude, neighbor.latitude],
                        color='lightgray', linewidth=1, alpha=0.6
                    )

        # Dibujar nodos
        for point in nodes_to_plot:
            self.ax.plot(
                point.longitude,
                point.latitude,
                'o',
                markersize=7 if point.neighbors else 5,
                color='#007acc' if point.neighbors else 'gray'
            )
            if self.show_labels.get():
                # Si hay ruta, solo mostrar nombres de nodos en la ruta
                if self.current_path and point in self.current_path:
                    self.ax.text(
                        point.longitude,
                        point.latitude,
                        f" {point.name}",
                        fontsize=8,
                        color='black'
                    )
                elif not self.current_path:
                    # Si no hay ruta activa, mostrar todos
                    self.ax.text(
                        point.longitude,
                        point.latitude,
                        f" {point.name}",
                        fontsize=8,
                        color='black'
                    )

        # Si hay ruta activa, volver a dibujarla
        if self.current_path:
            self.draw_current_path(self.current_path)

        self.ax.set_title("Visualización del Espacio Aéreo")
        self.ax.set_xlabel("Longitud")
        self.ax.set_ylabel("Latitud")
        self.ax.grid(True, linestyle='--', alpha=0.3)
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
                self.current_path = path
                tk.messagebox.showinfo("Ruta Encontrada", f"Distancia total: {cost:.2f} km")
            else:
                tk.messagebox.showerror("Error", "No se encontró ruta entre los puntos seleccionados")

        except Exception as e:
            tk.messagebox.showerror("Error", f"Error al buscar ruta: {str(e)}")
            print(f"Error completo: {e}")

    def highlight_path(self, path):
        self.current_path = path
        self.plot_airspace()

    def export_navpoints_kml(self):
        if not self.airspace.NavPoints:
            tk.messagebox.showwarning("Advertencia", "Primero cargue un espacio aéreo.")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".kml",
                                                filetypes=[("KML files", "*.kml")])
        if not filepath:
            return

        try:
            export_navpoints_to_kml(self.airspace.NavPoints, filepath)
            tk.messagebox.showinfo("Éxito", f"KML guardado en:\n{filepath}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

    def export_path_kml(self):
        if not self.current_path:
            tk.messagebox.showwarning("Advertencia", "Primero calcule una ruta más corta.")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".kml",
                                                filetypes=[("KML files", "*.kml")])
        if not filepath:
            return

        try:
            export_path_to_kml(self.current_path, filepath)
            tk.messagebox.showinfo("Éxito", f"Ruta exportada a:\n{filepath}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

    def update_combos(self):
        nodes = []
        for p in self.airspace.NavPoints:
            if self.hide_isolated.get() and not p.neighbors:
                continue
            display_text = f"{p.name} ({p.code})"
            nodes.append(display_text)

        self.origin_combo["values"] = nodes
        self.dest_combo["values"] = nodes

        if hasattr(self, 'node_listbox'):
            self.node_listbox.delete(0, tk.END)
            for node in nodes:
                self.node_listbox.insert(tk.END, node)

        if hasattr(self, 'segment_listbox'):
            self.segment_listbox.delete(0, tk.END)
            for seg in self.airspace.NavSegments:
                self.segment_listbox.insert(tk.END, f"{seg.origin} -> {seg.destination}")


    def draw_current_path(self, path):
        lons = [p.longitude for p in path]
        lats = [p.latitude for p in path]
        self.ax.plot(lons, lats, 'g-', linewidth=3)

        self.ax.plot(path[0].longitude, path[0].latitude, 'yo', markersize=8)  # Origen
        self.ax.plot(path[-1].longitude, path[-1].latitude, 'yo', markersize=8)  # Destino

        for i in range(len(path) - 1):
            p1, p2 = path[i], path[i + 1]
            mid_lon = (p1.longitude + p2.longitude) / 2
            mid_lat = (p1.latitude + p2.latitude) / 2

            for neighbor, dist in p1.get_neighbors():
                if neighbor.code == p2.code:
                    self.ax.text(mid_lon, mid_lat, f"{dist:.1f} km",
                                 fontsize=9, bbox=dict(facecolor='white', alpha=0.8))

        if self.show_labels.get():
            for p in path:
                self.ax.text(
                    p.longitude,
                    p.latitude,
                    f" {p.name}",
                    fontsize=9,
                    color='white',
                    bbox=dict(facecolor='green', edgecolor='black', boxstyle='round,pad=0.2', alpha=0.85)
                )
    def update_and_plot(self):
        self.update_combos()
        self.plot_airspace()
    def clear_path(self):
        self.current_path = None
        self.plot_airspace()

    def toggle_fake_screen(self):
        if not self.is_hiding:
            try:
                # Ocultar todo
                for widget in self.master.winfo_children():
                    widget.pack_forget()

                # Cargar imagen
                if not os.path.exists("fake_update.png"):
                    tk.messagebox.showerror("Error", "No se encuentra la imagen 'fake_update.png'")
                    return

                img = Image.open("fake_update.png")
                screen_width = self.master.winfo_screenwidth()
                screen_height = self.master.winfo_screenheight()
                img = img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
                self.fake_img = ImageTk.PhotoImage(img)

                self.fake_label = tk.Label(self.master, image=self.fake_img)
                self.fake_label.pack(fill=tk.BOTH, expand=True)

                # Salir al hacer clic o presionar Esc
                self.fake_label.bind("<Button-1>", lambda e: self.restore_interface())
                self.master.bind("<Escape>", lambda e: self.restore_interface())

                self.is_hiding = True
            except Exception as e:
                tk.messagebox.showerror("Error", str(e))
        else:
            self.restore_interface()

    def restore_interface(self):
        if self.fake_label:
            self.fake_label.destroy()

        for child in self.master.winfo_children():
            child.pack_forget()

        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        for child in self.master.winfo_children():
            if isinstance(child, ttk.Frame):
                child.pack(side=tk.LEFT, fill=tk.Y)

        self.is_hiding = False
        self.plot_airspace()

    def on_plot_click(self, event):
        if not self.airspace.NavPoints:
            return

        # Obtener coordenadas del clic (en escala de gráfico, no de píxeles)
        click_lon, click_lat = event.xdata, event.ydata
        if click_lon is None or click_lat is None:
            return  # Clic fuera del área gráfica

        # Buscar el nodo más cercano al clic
        closest_point = None
        min_dist = float("inf")

        for point in self.airspace.NavPoints:
            if self.hide_isolated.get() and not point.neighbors:
                continue
            dist = ((point.longitude - click_lon) ** 2 + (point.latitude - click_lat) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest_point = point

        if closest_point:
            self.show_neighbors_by_click(closest_point)

    def show_neighbors_by_click(self, nav_point):
        neighbors = nav_point.get_neighbors()
        self.ax.clear()

        # Dibujar todos los segmentos en gris
        for seg in self.airspace.NavSegments:
            origin = self.airspace.get_navpoint_by_name_or_id(seg.origin)
            dest = self.airspace.get_navpoint_by_name_or_id(seg.destination)
            if origin and dest:
                if self.hide_isolated.get() and (not origin.neighbors or not dest.neighbors):
                    continue
                self.ax.plot(
                    [origin.longitude, dest.longitude],
                    [origin.latitude, dest.latitude],
                    'gray', alpha=0.3
                )

        # Dibujar todos los nodos
        for point in self.airspace.NavPoints:
            if self.hide_isolated.get() and not point.neighbors:
                continue
            self.ax.plot(
                point.longitude,
                point.latitude,
                'o',
                markersize=5,
                color='blue'
            )
            if self.show_labels.get():
                self.ax.text(
                    point.longitude,
                    point.latitude,
                    f" {point.name}",
                    fontsize=8,
                    color='black'
                )

        # Resaltar nodo clicado en rojo
        self.ax.plot(nav_point.longitude, nav_point.latitude, 'o', markersize=7, color='red')

        # Dibujar conexiones con vecinos en verde
        for neighbor, distance in neighbors:
            self.ax.plot(
                [nav_point.longitude, neighbor.longitude],
                [nav_point.latitude, neighbor.latitude],
                'green', linewidth=2
            )
            self.ax.plot(
                neighbor.longitude,
                neighbor.latitude,
                'o',
                markersize=6,
                color='yellow'
            )
            if self.show_labels.get():
                self.ax.text(
                    neighbor.longitude,
                    neighbor.latitude,
                    f" {neighbor.name}",
                    fontsize=8,
                    color='green'
                )

        self.ax.set_title(f"Vecinos de {nav_point.name}", fontsize=10)
        self.ax.set_xlabel("Longitud")
        self.ax.set_ylabel("Latitud")
        self.canvas.draw()

    def new_graph(self):
        self.airspace = AirSpace()
        self.current_path = None
        self.update_and_plot()
        tk.messagebox.showinfo("Nuevo grafo", "Se ha creado un nuevo grafo vacío.")

    def add_node_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Añadir Nodo")

        tk.Label(dialog, text="Nombre:").pack()
        name_entry = tk.Entry(dialog)
        name_entry.pack()

        tk.Label(dialog, text="Latitud:").pack()
        lat_entry = tk.Entry(dialog)
        lat_entry.pack()

        tk.Label(dialog, text="Longitud:").pack()
        lon_entry = tk.Entry(dialog)
        lon_entry.pack()

        def add_node():
            name = name_entry.get().strip()

            # Validación básica
            if not name:
                tk.messagebox.showerror("Error", "El nombre es obligatorio.")
                return

            try:
                lat = float(lat_entry.get())
                lon = float(lon_entry.get())

                # Verificar que no exista ya un nodo con ese nombre
                if self.airspace.get_navpoint_by_name_or_id(name):
                    tk.messagebox.showerror("Error", "Ya existe un nodo con ese nombre.")
                    return

                self.airspace.add_navpoint(name, name, lat, lon)  # Usar el mismo nombre como código
                dialog.destroy()
                self.update_and_plot()
                tk.messagebox.showinfo("Éxito", f"Nodo '{name}' añadido correctamente.")

            except ValueError:
                tk.messagebox.showerror("Error", "Latitud y longitud deben ser números válidos.")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error al añadir nodo: {str(e)}")

        ttk.Button(dialog, text="Añadir", command=add_node).pack(pady=5)

    def remove_selected_node(self):
        selection = self.node_listbox.curselection()
        if not selection:
            tk.messagebox.showwarning("Advertencia", "Seleccione un nodo de la lista.")
            return

        node_text = self.node_listbox.get(selection[0])

        try:
            # Extraer el código/ID del texto mostrado
            if "(" in node_text and ")" in node_text:
                code = node_text.split("(")[-1].split(")")[0].strip()
            else:
                # Si no tiene paréntesis, usar todo el texto
                code = node_text.strip()

            # Intentar convertir a int si es numérico
            try:
                code = int(code)
            except ValueError:
                pass  # Mantener como string

            # Buscar y eliminar el nodo
            point = self.airspace.get_navpoint_by_name_or_id(code)
            if point:
                self.airspace.remove_navpoint(point.code)  # Usar el ID real del punto
                self.update_and_plot()
                tk.messagebox.showinfo("Éxito", f"Nodo eliminado correctamente.")
            else:
                tk.messagebox.showerror("Error", f"Nodo '{code}' no encontrado.")

        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo eliminar el nodo: {str(e)}")


    def add_segment_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Añadir Segmento")
        dialog.geometry("400x300")

        ttk.Label(dialog, text="Selecciona nodo origen:").pack(pady=5)
        origin_combo = ttk.Combobox(dialog, width=40)

        # Obtener la lista actualizada de nodos
        node_values = []
        for p in self.airspace.NavPoints:
            display_text = f"{p.name} ({p.code})"
            node_values.append(display_text)

        origin_combo["values"] = node_values
        origin_combo.pack(pady=5)

        ttk.Label(dialog, text="Selecciona nodo destino:").pack(pady=5)
        dest_combo = ttk.Combobox(dialog, width=40)
        dest_combo["values"] = node_values
        dest_combo.pack(pady=5)

        # Checkbox para conexión bidireccional
        bidirectional_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dialog, text="Conexión bidireccional", variable=bidirectional_var).pack(pady=5)

        # Mostrar distancia calculada
        distance_label = ttk.Label(dialog, text="Distancia: -")
        distance_label.pack(pady=5)

        def calculate_distance():
            """Calcula y muestra la distancia entre los nodos seleccionados"""
            try:
                origin_text = origin_combo.get()
                dest_text = dest_combo.get()

                if not origin_text or not dest_text:
                    distance_label.config(text="Distancia: -")
                    return

                # Extraer códigos
                origin_code = origin_text.split("(")[-1].split(")")[0].strip()
                dest_code = dest_text.split("(")[-1].split(")")[0].strip()

                # Convertir a int si es numérico
                try:
                    origin_code = int(origin_code)
                except ValueError:
                    pass
                try:
                    dest_code = int(dest_code)
                except ValueError:
                    pass

                # Buscar nodos
                origin = self.airspace.get_navpoint_by_name_or_id(origin_code)
                dest = self.airspace.get_navpoint_by_name_or_id(dest_code)

                if origin and dest:
                    distance = self.haversine_distance(
                        origin.latitude, origin.longitude,
                        dest.latitude, dest.longitude
                    )
                    distance_label.config(text=f"Distancia: {distance:.2f} km")
                else:
                    distance_label.config(text="Distancia: Error")

            except Exception as e:
                distance_label.config(text="Distancia: Error")
                print(f"Error calculando distancia: {e}")

        # Vincular el cálculo de distancia a los cambios en los comboboxes
        origin_combo.bind("<<ComboboxSelected>>", lambda e: calculate_distance())
        dest_combo.bind("<<ComboboxSelected>>", lambda e: calculate_distance())

        def add_segment():
            try:
                origin_text = origin_combo.get().strip()
                dest_text = dest_combo.get().strip()

                if not origin_text or not dest_text:
                    tk.messagebox.showerror("Error", "Debe seleccionar ambos nodos")
                    return

                if origin_text == dest_text:
                    tk.messagebox.showerror("Error", "El origen y destino no pueden ser el mismo nodo")
                    return

                # Extraer códigos de forma robusta
                try:
                    origin_code = origin_text.split("(")[-1].split(")")[0].strip()
                    dest_code = dest_text.split("(")[-1].split(")")[0].strip()
                except:
                    tk.messagebox.showerror("Error", "Formato de nodo incorrecto")
                    return

                print(f"DEBUG: Buscando nodos - Origen: '{origin_code}', Destino: '{dest_code}'")

                # Convertir a int si es numérico
                try:
                    origin_code = int(origin_code)
                except ValueError:
                    pass  # Mantener como string

                try:
                    dest_code = int(dest_code)
                except ValueError:
                    pass  # Mantener como string

                # Buscar los nodos
                origin = self.airspace.get_navpoint_by_name_or_id(origin_code)
                dest = self.airspace.get_navpoint_by_name_or_id(dest_code)

                print(f"DEBUG: Nodos encontrados - Origen: {origin}, Destino: {dest}")

                if not origin:
                    tk.messagebox.showerror("Error", f"Nodo origen '{origin_code}' no encontrado")
                    return
                if not dest:
                    tk.messagebox.showerror("Error", f"Nodo destino '{dest_code}' no encontrado")
                    return

                # Verificar si ya existe conexión
                existing_connection = False
                for neighbor, _ in origin.get_neighbors():
                    if neighbor.code == dest.code:
                        existing_connection = True
                        break

                if existing_connection:
                    result = tk.messagebox.askyesno("Conexión existente",
                                                    f"Ya existe una conexión entre {origin.name} y {dest.name}. ¿Desea actualizarla?")
                    if not result:
                        return

                # Calcular distancia
                distance = self.haversine_distance(
                    origin.latitude, origin.longitude,
                    dest.latitude, dest.longitude
                )

                print(f"DEBUG: Añadiendo segmento - Distancia: {distance:.2f} km")

                # Añadir el segmento
                if bidirectional_var.get():
                    # Conexión bidireccional
                    self.airspace.add_segment(origin.code, dest.code, distance)
                    success_msg = f"Segmento bidireccional añadido:\n{origin.name} ↔ {dest.name}\nDistancia: {distance:.2f} km"
                else:
                    # Conexión unidireccional (solo añadir neighbor en una dirección)
                    origin.add_neighbor((dest, distance))
                    self.airspace.NavSegments.append(NavSegment(origin.code, dest.code, distance))
                    success_msg = f"Segmento unidireccional añadido:\n{origin.name} → {dest.name}\nDistancia: {distance:.2f} km"

                dialog.destroy()
                self.update_and_plot()
                tk.messagebox.showinfo("Éxito", success_msg)

            except Exception as e:
                error_msg = f"No se pudo añadir el segmento: {str(e)}"
                print(f"ERROR: {error_msg}")
                tk.messagebox.showerror("Error", error_msg)

        # Botones
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Añadir Segmento", command=add_segment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_segment(self, origin_code, dest_code, distance):
        """Añade un segmento bidireccional entre dos nodos"""
        origin = self.get_navpoint_by_name_or_id(origin_code)
        dest = self.get_navpoint_by_name_or_id(dest_code)

        if not origin or not dest:
            raise ValueError(f"Nodo no encontrado: origen={origin_code}, destino={dest_code}")

        print(f"DEBUG add_segment: {origin.name} -> {dest.name}, distancia: {distance}")

        # Eliminar conexiones existentes si las hay
        origin.neighbors = [(n, d) for n, d in origin.neighbors if n.code != dest.code]
        dest.neighbors = [(n, d) for n, d in dest.neighbors if n.code != origin.code]

        # Añadir nuevas conexiones bidireccionales
        origin.add_neighbor((dest, distance))
        dest.add_neighbor((origin, distance))

        # Eliminar segmentos existentes entre estos nodos
        self.NavSegments = [s for s in self.NavSegments
                            if not ((s.origin == origin.code and s.destination == dest.code) or
                                    (s.origin == dest.code and s.destination == origin.code))]

        # Añadir nuevos segmentos (bidireccionales)
        self.NavSegments.append(NavSegment(origin.code, dest.code, distance))
        self.NavSegments.append(NavSegment(dest.code, origin.code, distance))

        print(f"DEBUG: Segmento añadido. Vecinos de {origin.name}: {len(origin.neighbors)}")

    def remove_selected_segment(self):
        """Elimina el segmento seleccionado de la lista"""
        selection = self.segment_listbox.curselection()
        if not selection:
            tk.messagebox.showwarning("Advertencia", "Seleccione un segmento de la lista.")
            return

        seg_text = self.segment_listbox.get(selection[0])
        print(f"DEBUG: Intentando eliminar segmento: '{seg_text}'")

        # Parsear el texto del segmento (formato: "origen -> destino")
        try:
            parts = seg_text.split(" -> ")
            if len(parts) != 2:
                tk.messagebox.showerror("Error", "Formato de segmento incorrecto.")
                return

            origin_code = parts[0].strip()
            dest_code = parts[1].strip()

            print(f"DEBUG: Códigos extraídos - Origen: '{origin_code}', Destino: '{dest_code}'")

            # Convertir a int si es numérico
            try:
                origin_code = int(origin_code)
            except ValueError:
                pass  # Mantener como string

            try:
                dest_code = int(dest_code)
            except ValueError:
                pass  # Mantener como string

            # Confirmar eliminación
            result = tk.messagebox.askyesno("Confirmar eliminación",
                                            f"¿Está seguro de que desea eliminar el segmento entre {origin_code} y {dest_code}?")
            if not result:
                return

            # Llamar al método de eliminación
            self.airspace.remove_segment(origin_code, dest_code)
            self.update_and_plot()
            tk.messagebox.showinfo("Éxito", "Segmento eliminado correctamente.")

        except Exception as e:
            error_msg = f"No se pudo eliminar el segmento: {str(e)}"
            print(f"ERROR: {error_msg}")
            tk.messagebox.showerror("Error", error_msg)

    def remove_segment(self, origin_code, dest_code):
        """Elimina un segmento entre dos nodos (bidireccional)"""
        print(f"DEBUG remove_segment: Buscando nodos {origin_code} y {dest_code}")

        # Buscar los nodos
        origin = self.get_navpoint_by_name_or_id(origin_code)
        dest = self.get_navpoint_by_name_or_id(dest_code)

        if not origin:
            raise ValueError(f"Nodo origen '{origin_code}' no encontrado")
        if not dest:
            raise ValueError(f"Nodo destino '{dest_code}' no encontrado")

        print(
            f"DEBUG: Nodos encontrados - Origen: {origin.name} (ID: {origin.code}), Destino: {dest.name} (ID: {dest.code})")

        # Eliminar conexiones entre los nodos (bidireccional)
        # Eliminar dest de los vecinos de origin
        origin.neighbors = [(n, d) for n, d in origin.neighbors if n.code != dest.code]

        # Eliminar origin de los vecinos de dest
        dest.neighbors = [(n, d) for n, d in dest.neighbors if n.code != origin.code]

        # Eliminar segmentos de la lista (usando los IDs reales)
        segments_removed = 0
        original_count = len(self.NavSegments)

        self.NavSegments = [s for s in self.NavSegments if not (
                (s.origin == origin.code and s.destination == dest.code) or
                (s.origin == dest.code and s.destination == origin.code)
        )]

        segments_removed = original_count - len(self.NavSegments)

        print(f"DEBUG: Se eliminaron {segments_removed} segmentos de la lista")
        print(f"DEBUG: Vecinos restantes de {origin.name}: {len(origin.neighbors)}")
        print(f"DEBUG: Vecinos restantes de {dest.name}: {len(dest.neighbors)}")

        if segments_removed == 0:
            print("WARNING: No se eliminaron segmentos. Puede que no existieran.")


    def debug_segments(self):
        """Método para debuggear el estado de los segmentos"""
        print("=== Estado actual de NavSegments ===")
        for i, seg in enumerate(self.NavSegments):
            origin = self.get_navpoint_by_name_or_id(seg.origin)
            dest = self.get_navpoint_by_name_or_id(seg.destination)
            origin_name = origin.name if origin else "UNKNOWN"
            dest_name = dest.name if dest else "UNKNOWN"
            print(f"{i}: {seg.origin}({origin_name}) -> {seg.destination}({dest_name}), distancia: {seg.distance}")

        print(f"\nTotal de segmentos: {len(self.NavSegments)}")

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(
            dlon / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def show_reachable_nodes(self):
        """Muestra todos los nodos alcanzables desde el nodo seleccionado"""
        selection = self.origin_combo.get()
        if not selection:
            tk.messagebox.showwarning("Advertencia", "Seleccione un nodo origen primero")
            return

        try:
            # Extraer el código del nodo de forma robusta
            code = selection.split('(')[-1].split(')')[0].strip()
            if not code:
                raise ValueError
        except:
            tk.messagebox.showerror("Error", "Formato de nodo incorrecto")
            return

        # Intentar encontrar el nodo primero por código (ID numérico)
        try:
            start_node = self.airspace.get_navpoint_by_name_or_id(int(code))
        except ValueError:
            # Si no es numérico, buscar por nombre
            start_node = self.airspace.get_navpoint_by_name_or_id(code)

        if not start_node:
            tk.messagebox.showerror("Error", "Nodo no encontrado")
            return

        # Usar BFS para encontrar todos los nodos alcanzables
        visited = set()
        queue = [start_node]
        visited.add(start_node)

        while queue:
            current_node = queue.pop(0)
            for neighbor, _ in current_node.get_neighbors():
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        # Preparar la lista de nodos alcanzables
        reachable_nodes = sorted([node.name for node in visited])
        total_nodes = len(reachable_nodes)

        # Crear ventana de resultados
        result_window = tk.Toplevel(self.master)
        result_window.title(f"Nodos alcanzables desde {start_node.name}")
        result_window.geometry("400x500")

        # Marco para el texto
        text_frame = ttk.Frame(result_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Etiqueta con el conteo
        count_label = ttk.Label(text_frame, text=f"Total de nodos alcanzables: {total_nodes}")
        count_label.pack(pady=5)

        # Scrollbar y lista
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        node_list = tk.Listbox(text_frame, yscrollcommand=scrollbar.set, width=50)
        for node in reachable_nodes:
            node_list.insert(tk.END, node)
        node_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=node_list.yview)

        # Botón para resaltar en el mapa
        def highlight_reachable():
            self.ax.clear()

            # Dibujar todos los nodos en gris
            for point in self.airspace.NavPoints:
                if self.hide_isolated.get() and not point.neighbors:
                    continue
                self.ax.plot(
                    point.longitude,
                    point.latitude,
                    'o',
                    markersize=5,
                    color='lightgray'
                )
                if self.show_labels.get():
                    self.ax.text(
                        point.longitude,
                        point.latitude,
                        f" {point.name}",
                        fontsize=8,
                        color='gray'
                    )

            # Resaltar nodos alcanzables en verde
            for node in visited:
                self.ax.plot(
                    node.longitude,
                    node.latitude,
                    'o',
                    markersize=7,
                    color='green'
                )
                if self.show_labels.get():
                    self.ax.text(
                        node.longitude,
                        node.latitude,
                        f" {node.name}",
                        fontsize=8,
                        color='darkgreen'
                    )

            # Resaltar nodo origen en rojo
            self.ax.plot(
                start_node.longitude,
                start_node.latitude,
                'o',
                markersize=9,
                color='red'
            )
            self.ax.text(
                start_node.longitude,
                start_node.latitude,
                f" {start_node.name} (Origen)",
                fontsize=9,
                color='darkred'
            )

            self.ax.set_title(f"Nodos alcanzables desde {start_node.name} (Total: {total_nodes})")
            self.canvas.draw()
            result_window.destroy()

        ttk.Button(result_window, text="Mostrar en Mapa", command=highlight_reachable).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = AirspaceGUI(root)
    root.mainloop()
