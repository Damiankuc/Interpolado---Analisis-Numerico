"""
Componente visual de graficación interactiva personalizado.
Hereda de tkinter.Frame y utiliza un tkinter.Canvas para trazar curvas de
aproximación matemática y puntos de interpolación con cuadrículas dinámicas,
etiquetado automático de ejes y tooltips flotantes al pasar el puntero del mouse.
"""

import tkinter as tk

class CustomPlot(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Color palette (Dark theme matching premium aesthetics)
        self.bg_color = "#121214"       # Deep dark background
        self.plot_bg = "#1e1e24"        # Dark charcoal for the active plot area
        self.axis_color = "#5a5a75"     # Muted slate blue for axes
        self.grid_color = "#282833"     # Very dark slate for gridlines
        self.text_color = "#8a8a9e"     # Soft grey for labels
        self.line_color = "#00adb5"     # Teal for the solution curve
        self.point_color = "#eeeeee"    # Near-white for step points
        self.point_outline = "#00adb5"  # Teal border for step points
        self.interp_color = "#ff5722"   # Bright orange/coral for the interpolation point
        
        self.canvas = tk.Canvas(self, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.points = []       # Lista de tuplas (x, y)
        self.interp_pt = None  # Tupla (x0, y0) o None
        self.x_min, self.x_max = 0.0, 1.0
        self.y_min, self.y_max = 0.0, 1.0
        self.markers = []      # Guarda datos de puntos dibujados para tooltips
        
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Configure>", self.on_resize)
        
    def clear(self):
        """Limpia el gráfico y resetea los datos."""
        self.canvas.delete("all")
        self.points = []
        self.interp_pt = None
        self.markers = []
        
    def set_data(self, points, interp_pt=None):
        """Asigna los datos y redibuja."""
        self.points = points
        self.interp_pt = interp_pt
        self.redraw()
        
    def calculate_bounds(self):
        """Calcula los límites de x e y con un margen del 10%."""
        if not self.points:
            self.x_min, self.x_max = 0.0, 1.0
            self.y_min, self.y_max = 0.0, 1.0
            return
            
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        if self.interp_pt:
            xs.append(self.interp_pt[0])
            ys.append(self.interp_pt[1])
            
        self.x_min, self.x_max = min(xs), max(xs)
        self.y_min, self.y_max = min(ys), max(ys)
        
        # Añadir padding del 10%
        x_range = self.x_max - self.x_min
        y_range = self.y_max - self.y_min
        
        x_pad = x_range * 0.1 if x_range != 0 else 1.0
        y_pad = y_range * 0.1 if y_range != 0 else 1.0
        
        self.x_min -= x_pad
        self.x_max += x_pad
        self.y_min -= y_pad
        self.y_max += y_pad
        
    def to_screen(self, x, y, w, h):
        """Mapea coordenadas matemáticas a coordenadas de pantalla."""
        x_start, x_end = 65, w - 25
        y_start, y_end = 25, h - 50
        
        x_range = self.x_max - self.x_min
        y_range = self.y_max - self.y_min
        
        if x_range == 0: x_range = 1.0
        if y_range == 0: y_range = 1.0
        
        sx = x_start + ((x - self.x_min) / x_range) * (x_end - x_start)
        sy = y_end - ((y - self.y_min) / y_range) * (y_end - y_start)
        return sx, sy
        
    def on_resize(self, event):
        """Controla el redimensionamiento del canvas."""
        self.redraw()
        
    def redraw(self):
        """Dibuja todos los elementos gráficos en el Canvas."""
        self.canvas.delete("all")
        self.markers = []
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        if w < 100 or h < 100:
            return  # Evitar cálculos si aún no se ha renderizado la ventana
            
        self.calculate_bounds()
        
        x_start, x_end = 65, w - 25
        y_start, y_end = 25, h - 50
        
        # Fondo del área activa del gráfico
        self.canvas.create_rectangle(x_start, y_start, x_end, y_end, fill=self.plot_bg, outline="")
        
        # 1. Dibujar Grillas y Etiquetas
        num_divs = 6
        
        # Eje Y: Grilla y etiquetas
        for i in range(num_divs + 1):
            y_val = self.y_min + i * (self.y_max - self.y_min) / num_divs
            sx, sy = self.to_screen(self.x_min, y_val, w, h)
            # Línea de grilla horizontal
            self.canvas.create_line(x_start, sy, x_end, sy, fill=self.grid_color, dash=(2, 4))
            # Texto a la izquierda
            self.canvas.create_text(x_start - 10, sy, text=f"{y_val:.4g}", fill=self.text_color, anchor=tk.E, font=("Segoe UI", 9))
            
        # Eje X: Grilla y etiquetas
        for i in range(num_divs + 1):
            x_val = self.x_min + i * (self.x_max - self.x_min) / num_divs
            sx, sy = self.to_screen(x_val, self.y_min, w, h)
            # Línea de grilla vertical
            self.canvas.create_line(sx, y_start, sx, y_end, fill=self.grid_color, dash=(2, 4))
            # Texto debajo
            self.canvas.create_text(sx, y_end + 15, text=f"{x_val:.4g}", fill=self.text_color, anchor=tk.N, font=("Segoe UI", 9))
            
        # 2. Dibujar Ejes de Coordenadas principales (en 0,0 si están en rango)
        # Eje Y (x = 0)
        if self.x_min <= 0.0 <= self.x_max:
            sx_zero, _ = self.to_screen(0.0, 0.0, w, h)
            self.canvas.create_line(sx_zero, y_start, sx_zero, y_end, fill=self.axis_color, width=2)
        else:
            # Línea de borde izquierdo
            self.canvas.create_line(x_start, y_start, x_start, y_end, fill=self.axis_color, width=1.5)
            
        # Eje X (y = 0)
        if self.y_min <= 0.0 <= self.y_max:
            _, sy_zero = self.to_screen(0.0, 0.0, w, h)
            self.canvas.create_line(x_start, sy_zero, x_end, sy_zero, fill=self.axis_color, width=2)
        else:
            # Línea de borde inferior
            self.canvas.create_line(x_start, y_end, x_end, y_end, fill=self.axis_color, width=1.5)
            
        # Borde exterior del gráfico
        self.canvas.create_rectangle(x_start, y_start, x_end, y_end, outline="#3e3e4a", width=1.5)
        
        # Si no hay puntos, mostrar aviso
        if not self.points:
            self.canvas.create_text(w/2, h/2, text="No hay datos para graficar.\nConfigure los parámetros de la EDO y presione 'Resolver'.", fill="#5a5a75", font=("Segoe UI", 11, "italic"), justify=tk.CENTER)
            return
            
        # 3. Dibujar la curva continua de la EDO
        screen_pts = [self.to_screen(p[0], p[1], w, h) for p in self.points]
        flat_pts = []
        for sx, sy in screen_pts:
            flat_pts.extend([sx, sy])
            
        if len(flat_pts) >= 4:
            self.canvas.create_line(flat_pts, fill=self.line_color, width=3, capstyle=tk.ROUND, joinstyle=tk.ROUND)
            
        # 4. Dibujar puntos de pasos discretos (Markers)
        for i, (x_val, y_val) in enumerate(self.points):
            sx, sy = screen_pts[i]
            r = 4.5
            # Crear círculo del punto
            marker_id = self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill=self.point_color, outline=self.point_outline, width=1.5)
            # Almacenar para tooltips
            self.markers.append((sx, sy, x_val, y_val, f"Paso {i}", marker_id))
            
        # 5. Dibujar punto de interpolación (con líneas de proyección discontinuas)
        if self.interp_pt:
            x0, y0 = self.interp_pt
            sx0, sy0 = self.to_screen(x0, y0, w, h)
            
            # Proyección hacia eje Y
            self.canvas.create_line(sx0, sy0, x_start, sy0, fill=self.interp_color, dash=(3, 3), width=1.2)
            # Proyección hacia eje X
            self.canvas.create_line(sx0, sy0, sx0, y_end, fill=self.interp_color, dash=(3, 3), width=1.2)
            
            # Dibujar un rombo
            r = 6
            marker_id = self.canvas.create_polygon(
                sx0, sy0 - r, 
                sx0 + r, sy0, 
                sx0, sy0 + r, 
                sx0 - r, sy0, 
                fill=self.interp_color, outline="#ffffff", width=1.5
            )
            # Almacenar para tooltips
            self.markers.append((sx0, sy0, x0, y0, f"Interpolación y({x0:.4g})", marker_id))
            
    def on_mouse_move(self, event):
        """Muestra una etiqueta informativa cuando el cursor está cerca de algún punto."""
        if not self.points:
            return
            
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        mx, my = event.x, event.y
        
        x_start, x_end = 65, w - 25
        y_start, y_end = 25, h - 50
        
        # Buscar el punto más cercano dentro de un umbral de 8 píxeles
        hovered = None
        min_dist = 8.0
        
        for sx, sy, dx, dy, label, marker_id in self.markers:
            dist = ((mx - sx)**2 + (my - sy)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                hovered = (sx, sy, dx, dy, label)
                
        # Limpiar tooltip anterior
        self.canvas.delete("tooltip")
        
        if hovered:
            sx, sy, dx, dy, label = hovered
            
            # Formatear el texto a mostrar
            text_str = f"{label}\nx = {dx:.6f}\ny = {dy:.6f}"
            
            # Posición inicial arriba del punto
            tx, ty = sx, sy - 25
            
            box_w = 150
            box_h = 48
            
            # Ajustar para que no se salga de los límites del gráfico
            if tx - box_w/2 < x_start:
                tx = x_start + box_w/2
            elif tx + box_w/2 > x_end:
                tx = x_end - box_w/2
            if ty - box_h/2 < y_start:
                ty = sy + 25 # Mover hacia abajo si toca el borde superior
                
            # Fondo del tooltip
            self.canvas.create_rectangle(
                tx - box_w/2, ty - box_h/2,
                tx + box_w/2, ty + box_h/2,
                fill="#18181f", outline=self.point_outline, width=1.2, tags="tooltip"
            )
            # Texto
            self.canvas.create_text(
                tx, ty,
                text=text_str,
                fill="#ffffff",
                font=("Segoe UI", 9),
                justify=tk.CENTER,
                tags="tooltip"
            )
