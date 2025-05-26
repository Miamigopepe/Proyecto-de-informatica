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
        ttk.Button(control_frame, text="Exportar Puntos a KML",
                   command=self.export_navpoints_kml).pack(pady=5)
        ttk.Button(control_frame, text="Exportar Ruta a KML",
                   command=self.export_path_kml).pack(pady=5)
        ttk.Checkbutton(control_frame, text="Mostrar nombres",
                        variable=self.show_labels,
                        command=self.plot_airspace).pack(pady=5)

        ttk.Checkbutton(control_frame, text="Ocultar nodos sin vecinos",
                        variable=self.hide_isolated,
                        command=self.update_and_plot).pack(pady=5)
        ttk.Button(control_frame, text="Limpiar Ruta",
                   command=self.clear_path).pack(pady=5)
        ttk.Button(control_frame, text="💻 Irse del trabajo",
                   command=self.toggle_fake_screen).pack(pady=5)

        ttk.Label(control_frame, text="Reproductor de Música").pack(pady=5)
        ttk.Button(control_frame, text="Añadir Música",
                   command=self.add_music).pack(pady=2)
        ttk.Button(control_frame, text="▶ Reproducir",
                   command=self.play_music).pack(pady=2)
        ttk.Button(control_frame, text="⏸ Pausar",
                   command=self.pause_music).pack(pady=2)
        ttk.Button(control_frame, text="⏹ Detener",
                   command=self.stop_music).pack(pady=2)
        ttk.Button(control_frame, text="↪ Siguiente",
                   command=self.next_track).pack(pady=2)
        ttk.Button(control_frame, text="↩ Anterior",
                   command=self.prev_track).pack(pady=2)

        # Área de gráficos
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect("button_press_event", self.on_plot_click)

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
            display_text = f"{p.name} ({p.code})"
            nodes.append(display_text)
            # Depuración: mostrar lo que se está añadiendo al Combobox
            print(f"Añadiendo al Combobox: '{display_text}'")

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


if __name__ == "__main__":
    root = tk.Tk()
    app = AirspaceGUI(root)
    root.mainloop()