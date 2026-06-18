"""
Proyecto Integrador de Análisis Numérico - UCP
Aplicación principal en Tkinter.
Presenta una interfaz de usuario avanzada con soporte de tema oscuro moderno (charcoal/teal),
para interactuar con solucionadores de ecuaciones diferenciales ordinarias, interpolación polinómica
y cálculo de autovalores/autovectores mediante el método de la potencia inversa con shift.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import sys

# Habilitar nitidez de fuentes en Windows (High DPI scaling)
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Importar módulos propios
import numerical_methods as nm
from custom_plot import CustomPlot


class NumericApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Análisis Numérico - Proyecto Integrador")
        self.geometry("1100x750")
        self.minimum_size(1000, 650)
        self.configure(bg="#121214")
        
        # Centrar la ventana en la pantalla
        self.center_window(1100, 750)
        
        # Configurar estilos generales
        self.setup_styles()
        
        # Crear componentes
        self.create_widgets()
        
        # Cargar valores iniciales por defecto en ambos módulos
        self.load_default_edo()
        self.load_default_matrix()
        
    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
    def minimum_size(self, width, height):
        self.minsize(width, height)
        
    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Colores principales
        bg_dark = "#121214"
        card_bg = "#1e1e24"
        accent_color = "#00adb5"
        
        # Configuración del Notebook (Pestañas)
        style.configure("TNotebook", background=bg_dark, borderwidth=0)
        style.configure("TNotebook.Tab", background=card_bg, foreground="#a0a0b0",
                        font=("Segoe UI", 10, "bold"), borderwidth=0, padding=[18, 8])
        style.map("TNotebook.Tab",
                  background=[("selected", accent_color)],
                  foreground=[("selected", "#ffffff")])
        
        # Configuración de Treeview (Tablas)
        style.configure("Treeview",
                        background=card_bg,
                        foreground="#ffffff",
                        fieldbackground=card_bg,
                        rowheight=26,
                        font=("Segoe UI", 9))
        style.map("Treeview",
                  background=[("selected", accent_color)],
                  foreground=[("selected", "#ffffff")])
        style.configure("Treeview.Heading",
                        background="#282832",
                        foreground="#eeeeee",
                        relief="flat",
                        font=("Segoe UI", 9, "bold"))
        
        # Configuración de Comboboxes y Spinboxes de ttk
        style.configure("TCombobox", fieldbackground="#282830", background="#282830", foreground="#ffffff")
        style.map("TCombobox", fieldbackground=[("readonly", "#282830")], foreground=[("readonly", "#ffffff")])
        
    def create_widgets(self):
        # Título superior de la App
        header_frame = tk.Frame(self, bg="#1a1a22", height=60, bd=0)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="PROYECTO INTEGRADOR DE ANÁLISIS NUMÉRICO",
                               bg="#1a1a22", fg="#00adb5", font=("Segoe UI", 15, "bold"))
        title_label.pack(side=tk.LEFT, padx=20)
        
        subtitle_label = tk.Label(header_frame, text="Universidad de la Cuenca del Plata",
                                  bg="#1a1a22", fg="#8a8a9e", font=("Segoe UI", 10, "italic"))
        subtitle_label.pack(side=tk.RIGHT, padx=20)
        
        # Contenedor de pestañas principal
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestañas
        self.tab_edo = tk.Frame(self.notebook, bg="#121214")
        self.tab_eigen = tk.Frame(self.notebook, bg="#121214")
        self.tab_doc = tk.Frame(self.notebook, bg="#121214")
        
        self.notebook.add(self.tab_edo, text="  EDO & Interpolación  ")
        self.notebook.add(self.tab_eigen, text="  Método Potencia Inversa  ")
        self.notebook.add(self.tab_doc, text="  Documentación  ")
        
        # Inicializar contenido de pestañas
        self.build_tab_edo()
        self.build_tab_eigen()
        self.build_tab_doc()
        
    # =====================================================================
    # PESTAÑA 1: EDO E INTERPOLACIÓN
    # =====================================================================
    def build_tab_edo(self):
        # Layout: Split en Izquierda (Parámetros) y Derecha (Gráfico/Resultados)
        main_pane = tk.PanedWindow(self.tab_edo, orient=tk.HORIZONTAL, bg="#121214", bd=0, sashwidth=4)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # --- Panel Izquierdo (Entradas) ---
        left_panel = tk.Frame(main_pane, bg="#121214", width=340)
        left_panel.pack_propagate(False)
        main_pane.add(left_panel, minsize=320)
        
        # Tarjeta 1: Configuración de la EDO
        card_edo = tk.LabelFrame(left_panel, text=" Configuración EDO ", bg="#1e1e24", fg="#eeeeee",
                                 font=("Segoe UI", 10, "bold"), bd=1, relief="flat", padx=10, pady=10)
        card_edo.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(card_edo, text="Ecuación y' = f(x, y):", bg="#1e1e24", fg="#a0a0b0", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4)
        self.eq_entry = tk.Entry(card_edo, bg="#282830", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#3e3e4a")
        self.eq_entry.grid(row=0, column=1, sticky="we", padx=5, pady=4)
        
        tk.Label(card_edo, text="Extremo Inicial (a):", bg="#1e1e24", fg="#a0a0b0", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=4)
        self.a_entry = tk.Entry(card_edo, bg="#282830", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#3e3e4a")
        self.a_entry.grid(row=1, column=1, sticky="we", padx=5, pady=4)
        
        tk.Label(card_edo, text="Extremo Final (b):", bg="#1e1e24", fg="#a0a0b0", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=4)
        self.b_entry = tk.Entry(card_edo, bg="#282830", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#3e3e4a")
        self.b_entry.grid(row=2, column=1, sticky="we", padx=5, pady=4)
        
        tk.Label(card_edo, text="Valor Inicial y(a):", bg="#1e1e24", fg="#a0a0b0", font=("Segoe UI", 9)).grid(row=3, column=0, sticky="w", pady=4)
        self.y_a_entry = tk.Entry(card_edo, bg="#282830", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#3e3e4a")
        self.y_a_entry.grid(row=3, column=1, sticky="we", padx=5, pady=4)
        
        tk.Label(card_edo, text="Intervalos (N):", bg="#1e1e24", fg="#a0a0b0", font=("Segoe UI", 9)).grid(row=4, column=0, sticky="w", pady=4)
        self.n_steps_spin = tk.Spinbox(card_edo, from_=2, to=500, bg="#282830", fg="#ffffff", buttonbackground="#282830", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#3e3e4a")
        self.n_steps_spin.grid(row=4, column=1, sticky="we", padx=5, pady=4)
        
        card_edo.columnconfigure(1, weight=1)
        
        # Tarjeta 2: Configuración de Métodos e Interpolación
        card_interp = tk.LabelFrame(left_panel, text=" Métodos e Interpolación ", bg="#1e1e24", fg="#eeeeee",
                                    font=("Segoe UI", 10, "bold"), bd=1, relief="flat", padx=10, pady=10)
        card_interp.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(card_interp, text="Método EDO:", bg="#1e1e24", fg="#a0a0b0", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4)
        self.edo_method_combo = ttk.Combobox(card_interp, values=["Euler Modificado (Heun)", "Runge-Kutta 4 (RK4)", "Milne (Predictor-Corrector)"], state="readonly")
        self.edo_method_combo.grid(row=0, column=1, sticky="we", padx=5, pady=4)
        self.edo_method_combo.set("Runge-Kutta 4 (RK4)")
        
        tk.Label(card_interp, text="Método Interp:", bg="#1e1e24", fg="#a0a0b0", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=4)
        self.interp_method_combo = ttk.Combobox(card_interp, values=["Lagrange", "Newton (Diferencias Divididas)"], state="readonly")
        self.interp_method_combo.grid(row=1, column=1, sticky="we", padx=5, pady=4)
        self.interp_method_combo.set("Newton (Diferencias Divididas)")
        
        tk.Label(card_interp, text="Punto x0 a evaluar:", bg="#1e1e24", fg="#a0a0b0", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=4)
        self.x0_entry = tk.Entry(card_interp, bg="#282830", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#3e3e4a")
        self.x0_entry.grid(row=2, column=1, sticky="we", padx=5, pady=4)
        
        tk.Label(card_interp, text="Puntos de apoyo (k):", bg="#1e1e24", fg="#a0a0b0", font=("Segoe UI", 9)).grid(row=3, column=0, sticky="w", pady=4)
        self.k_points_spin = tk.Spinbox(card_interp, from_=2, to=20, bg="#282830", fg="#ffffff", buttonbackground="#282830", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#3e3e4a")
        self.k_points_spin.grid(row=3, column=1, sticky="we", padx=5, pady=4)
        self.k_points_spin.delete(0, tk.END)
        self.k_points_spin.insert(0, "4")
        
        card_interp.columnconfigure(1, weight=1)
        
        # Botones de Acción
        btn_frame = tk.Frame(left_panel, bg="#121214")
        btn_frame.pack(fill=tk.X, padx=5, pady=15)
        
        self.btn_resolve = tk.Button(btn_frame, text="RESOLVER Y GRAFICAR", bg="#00adb5", fg="#ffffff",
                                     font=("Segoe UI", 10, "bold"), relief="flat", bd=0, height=2,
                                     activebackground="#00c4cf", activeforeground="#ffffff",
                                     command=self.solve_and_update_edo)
        self.btn_resolve.pack(fill=tk.X, pady=4)
        
        self.btn_load_edo_ex = tk.Button(btn_frame, text="Cargar Ejemplo (y' = x - y)", bg="#282832", fg="#a0a0b0",
                                         font=("Segoe UI", 9), relief="flat", bd=0, height=1,
                                         activebackground="#3e3e4d", activeforeground="#ffffff",
                                         command=self.load_default_edo)
        self.btn_load_edo_ex.pack(fill=tk.X, pady=4)
        
        # Tarjeta 3: Resultado de Interpolación Rápido
        card_res = tk.LabelFrame(left_panel, text=" Resultado Interpolado ", bg="#1e1e24", fg="#eeeeee",
                                  font=("Segoe UI", 10, "bold"), bd=1, relief="flat", padx=10, pady=10)
        card_res.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.interp_result_var = tk.StringVar(value="y(x0) = ---")
        lbl_res = tk.Label(card_res, textvariable=self.interp_result_var, bg="#1e1e24", fg="#ff5722",
                           font=("Consolas", 12, "bold"), justify=tk.CENTER)
        lbl_res.pack(fill=tk.BOTH, expand=True)
        
        # --- Panel Derecho (Visualización) ---
        right_panel = tk.Frame(main_pane, bg="#121214")
        main_pane.add(right_panel, minsize=500)
        
        # Configurar proporciones de cuadrícula en el panel derecho
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=4)
        right_panel.rowconfigure(1, weight=3)
        
        # Graficador interactivo
        self.plot_widget = CustomPlot(right_panel, bd=0, relief="flat")
        self.plot_widget.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Notebook de resultados tabulares e información adicional
        self.edo_results_notebook = ttk.Notebook(right_panel)
        self.edo_results_notebook.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Pestaña resultados de pasos
        tab_pasos = tk.Frame(self.edo_results_notebook, bg="#1e1e24")
        self.edo_results_notebook.add(tab_pasos, text=" Resultados de Pasos ")
        
        pasos_scroll_y = tk.Scrollbar(tab_pasos)
        pasos_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.pasos_tree = ttk.Treeview(tab_pasos, columns=("Paso", "x", "y", "f(x,y)"), show="headings", yscrollcommand=pasos_scroll_y.set)
        self.pasos_tree.pack(fill=tk.BOTH, expand=True)
        pasos_scroll_y.config(command=self.pasos_tree.yview)
        
        self.pasos_tree.heading("Paso", text="Paso")
        self.pasos_tree.heading("x", text="x_i")
        self.pasos_tree.heading("y", text="y_i (Aproximación)")
        self.pasos_tree.heading("f(x,y)", text="y'_i = f(x_i, y_i)")
        
        self.pasos_tree.column("Paso", width=60, anchor=tk.CENTER)
        self.pasos_tree.column("x", width=120, anchor=tk.CENTER)
        self.pasos_tree.column("y", width=160, anchor=tk.CENTER)
        self.pasos_tree.column("f(x,y)", width=160, anchor=tk.CENTER)
        
        # Pestaña tabla de diferencias divididas (para Newton) / Detalles (Lagrange)
        self.tab_interp_details = tk.Frame(self.edo_results_notebook, bg="#1e1e24")
        self.edo_results_notebook.add(self.tab_interp_details, text=" Detalle de Interpolación ")
        
        self.interp_details_text = tk.Text(self.tab_interp_details, bg="#1e1e24", fg="#ffffff",
                                           insertbackground="white", font=("Consolas", 9), bd=0, wrap=tk.NONE)
        
        det_scroll_y = tk.Scrollbar(self.tab_interp_details, orient=tk.VERTICAL, command=self.interp_details_text.yview)
        det_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        det_scroll_x = tk.Scrollbar(self.tab_interp_details, orient=tk.HORIZONTAL, command=self.interp_details_text.xview)
        det_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.interp_details_text.pack(fill=tk.BOTH, expand=True)
        self.interp_details_text.config(yscrollcommand=det_scroll_y.set, xscrollcommand=det_scroll_x.set)
        
    def load_default_edo(self):
        self.eq_entry.delete(0, tk.END)
        self.eq_entry.insert(0, "x - y")
        self.a_entry.delete(0, tk.END)
        self.a_entry.insert(0, "0.0")
        self.b_entry.delete(0, tk.END)
        self.b_entry.insert(0, "2.0")
        self.y_a_entry.delete(0, tk.END)
        self.y_a_entry.insert(0, "1.0")
        self.n_steps_spin.delete(0, tk.END)
        self.n_steps_spin.insert(0, "10")
        self.x0_entry.delete(0, tk.END)
        self.x0_entry.insert(0, "0.75")
        self.k_points_spin.delete(0, tk.END)
        self.k_points_spin.insert(0, "4")
        
    def solve_and_update_edo(self):
        try:
            # Lectura y Validación de Inputs
            f_expr = self.eq_entry.get().strip()
            if not f_expr:
                raise ValueError("La expresión de la EDO no puede estar vacía.")
                
            a = float(self.a_entry.get())
            b = float(self.b_entry.get())
            if b <= a:
                raise ValueError("El extremo final 'b' debe ser mayor al inicial 'a'.")
                
            y_a = float(self.y_a_entry.get())
            
            N = int(self.n_steps_spin.get())
            if N <= 0:
                raise ValueError("El número de pasos N debe ser mayor a 0.")
            h = (b - a) / N
            
            x0 = float(self.x0_entry.get())
            if not (a < x0 < b):
                raise ValueError(f"El punto a interpolar x0 ({x0}) debe estar estrictamente dentro del intervalo (a, b) = ({a}, {b}).")
                
            k = int(self.k_points_spin.get())
            if k < 2:
                raise ValueError("Se requieren al menos 2 puntos de apoyo para interpolar.")
            if k > N + 1:
                raise ValueError(f"No se pueden usar {k} puntos de apoyo con solo N+1={N+1} puntos disponibles. Reduzca 'k' o aumente 'N'.")
                
            # Validar ecuación compilando/evaluando de prueba en (a, y_a)
            nm.parse_and_eval(f_expr, a, y_a)
            
            # 1. Resolver EDO
            method = self.edo_method_combo.get()
            if "Euler Modificado" in method:
                x_pts, y_pts, h_actual = nm.solve_heun(f_expr, a, b, y_a, h)
            elif "Runge-Kutta 4" in method:
                x_pts, y_pts, h_actual = nm.solve_rk4(f_expr, a, b, y_a, h)
            elif "Milne" in method:
                x_pts, y_pts, h_actual = nm.solve_milne(f_expr, a, b, y_a, h)
            else:
                raise ValueError("Método de EDO no reconocido.")
                
            # 2. Seleccionar puntos cercanos para interpolar y realizar la interpolación
            x_sel, y_sel = nm.select_nearest_points(x_pts, y_pts, x0, k)
            
            interp_method = self.interp_method_combo.get()
            detail_output = ""
            
            if "Lagrange" in interp_method:
                y0, terms = nm.interpolate_lagrange(x_sel, y_sel, x0)
                
                # Generar detalles
                detail_output += f"INTERPOLACIÓN DE LAGRANGE CON {k} PUNTOS DE APOYO\n"
                detail_output += f"Evaluar en x0 = {x0}\n"
                detail_output += "=" * 55 + "\n"
                detail_output += f"{'x_i':^10} | {'y_i':^12} | {'L_i(x0)':^12} | {'Término (y_i*L_i)':^14}\n"
                detail_output += "-" * 55 + "\n"
                for xi, yi, li in terms:
                    term_val = yi * li
                    detail_output += f"{xi:10.5f} | {yi:12.6f} | {li:12.6f} | {term_val:14.6f}\n"
                detail_output += "=" * 55 + "\n"
                detail_output += f"Valor Interpolado y({x0}) = {y0:.8f}\n"
                
            else: # Newton
                y0, formatted_table, steps = nm.interpolate_newton(x_sel, y_sel, x0)
                
                # Generar detalles con la tabla de diferencias divididas
                detail_output += f"INTERPOLACIÓN DE NEWTON (DIFERENCIAS DIVIDIDAS) CON {k} PUNTOS\n"
                detail_output += f"Evaluar en x0 = {x0}\n"
                detail_output += "=" * 75 + "\n"
                
                # Encabezados de la tabla
                headers = ["x_i", "y_i (f[x_i])"]
                for col_idx in range(1, k):
                    headers.append(f"Diff orden {col_idx}")
                
                header_line = "".join(f"{h_name:^14} | " for h_name in headers)
                detail_output += header_line[:-3] + "\n"
                detail_output += "-" * (17 * k) + "\n"
                
                for row in formatted_table:
                    row_line = ""
                    for val in row:
                        row_line += f"{val:14.6f} | "
                    detail_output += row_line[:-3] + "\n"
                    
                detail_output += "=" * 75 + "\n"
                detail_output += "PASOS DE EVALUACIÓN:\n"
                for step in steps:
                    detail_output += f"{step}\n"
                detail_output += "-" * 75 + "\n"
                detail_output += f"Valor Interpolado y({x0}) = {y0:.8f}\n"
                
            # 3. Actualizar GUI
            self.interp_result_var.set(f"y({x0:.4g}) ≈ {y0:.6f}\n(h = {h_actual:.4f})")
            
            # Actualizar tabla de pasos
            for item in self.pasos_tree.get_children():
                self.pasos_tree.delete(item)
                
            for idx, (xi, yi) in enumerate(zip(x_pts, y_pts)):
                f_val = nm.parse_and_eval(f_expr, xi, yi)
                self.pasos_tree.insert("", tk.END, values=(idx, f"{xi:.5f}", f"{yi:.7f}", f"{f_val:.7f}"))
                
            # Actualizar detalles de interpolación
            self.interp_details_text.delete("1.0", tk.END)
            self.interp_details_text.insert("1.0", detail_output)
            
            # Graficar
            self.plot_widget.set_data(list(zip(x_pts, y_pts)), (x0, y0))
            
        except Exception as err:
            messagebox.showerror("Error en EDO / Interpolación", f"Error en el cálculo:\n{str(err)}")

    # =====================================================================
    # PESTAÑA 2: MÉTODO DE LA POTENCIA INVERSA
    # =====================================================================
    def build_tab_eigen(self):
        # Layout: Split en Izquierda (Parámetros/Matriz) y Derecha (Resultados de iteraciones)
        main_pane = tk.PanedWindow(self.tab_eigen, orient=tk.HORIZONTAL, bg="#121214", bd=0, sashwidth=4)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # --- Panel Izquierdo (Entrada de Matriz) ---
        left_panel = tk.Frame(main_pane, bg="#121214", width=380)
        left_panel.pack_propagate(False)
        main_pane.add(left_panel, minsize=350)
        
        # Tarjeta: Tamaño de la Matriz
        card_matrix_size = tk.Frame(left_panel, bg="#1e1e24", padx=10, pady=10)
        card_matrix_size.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(card_matrix_size, text="Dimensión Matriz (n):", bg="#1e1e24", fg="#eeeeee", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.matrix_size_spin = tk.Spinbox(card_matrix_size, from_=2, to=8, width=5, bg="#282830", fg="#ffffff", buttonbackground="#282830", bd=0, highlightthickness=1, highlightbackground="#3e3e4a", command=self.update_matrix_grid)
        self.matrix_size_spin.pack(side=tk.LEFT, padx=10)
        self.matrix_size_spin.delete(0, tk.END)
        self.matrix_size_spin.insert(0, "3")
        
        # Contenedor para la grilla dinámica de la matriz
        self.card_matrix = tk.LabelFrame(left_panel, text=" Matriz A ", bg="#1e1e24", fg="#eeeeee",
                                          font=("Segoe UI", 10, "bold"), bd=1, relief="flat", padx=10, pady=10)
        self.card_matrix.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.matrix_grid_frame = tk.Frame(self.card_matrix, bg="#1e1e24")
        self.matrix_grid_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Tarjeta: Parámetros del Método
        card_params = tk.LabelFrame(left_panel, text=" Parámetros del Método ", bg="#1e1e24", fg="#eeeeee",
                                     font=("Segoe UI", 10, "bold"), bd=1, relief="flat", padx=10, pady=10)
        card_params.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(card_params, text="Desplazamiento (Shift α):", bg="#1e1e24", fg="#a0a0b0", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4)
        self.shift_entry = tk.Entry(card_params, bg="#282830", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#3e3e4a")
        self.shift_entry.grid(row=0, column=1, sticky="we", padx=5, pady=4)
        self.shift_entry.insert(0, "0.0")
        
        tk.Label(card_params, text="Vector Inicial v0 (opcional):", bg="#1e1e24", fg="#a0a0b0", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=4)
        self.v0_entry = tk.Entry(card_params, bg="#282830", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#3e3e4a")
        self.v0_entry.grid(row=1, column=1, sticky="we", padx=5, pady=4)
        
        tk.Label(card_params, text="Tolerancia ε:", bg="#1e1e24", fg="#a0a0b0", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=4)
        self.tol_entry = tk.Entry(card_params, bg="#282830", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#3e3e4a")
        self.tol_entry.grid(row=2, column=1, sticky="we", padx=5, pady=4)
        self.tol_entry.insert(0, "1e-6")
        
        tk.Label(card_params, text="Iteraciones Máximas:", bg="#1e1e24", fg="#a0a0b0", font=("Segoe UI", 9)).grid(row=3, column=0, sticky="w", pady=4)
        self.max_iter_entry = tk.Entry(card_params, bg="#282830", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#3e3e4a")
        self.max_iter_entry.grid(row=3, column=1, sticky="we", padx=5, pady=4)
        self.max_iter_entry.insert(0, "80")
        
        card_params.columnconfigure(1, weight=1)
        
        # Botones Potencia Inversa
        btn_frame_pi = tk.Frame(left_panel, bg="#121214")
        btn_frame_pi.pack(fill=tk.X, padx=5, pady=10)
        
        self.btn_calc_eigen = tk.Button(btn_frame_pi, text="CALCULAR AUTOVALOR", bg="#00adb5", fg="#ffffff",
                                        font=("Segoe UI", 10, "bold"), relief="flat", bd=0, height=2,
                                        activebackground="#00c4cf", activeforeground="#ffffff",
                                        command=self.solve_inverse_power)
        self.btn_calc_eigen.pack(fill=tk.X, pady=4)
        
        self.btn_load_ex_matrix = tk.Button(btn_frame_pi, text="Cargar Matriz Ejemplo (3x3 con Shift)", bg="#282832", fg="#a0a0b0",
                                             font=("Segoe UI", 9), relief="flat", bd=0, height=1,
                                             activebackground="#3e3e4d", activeforeground="#ffffff",
                                             command=self.load_default_matrix)
        self.btn_load_ex_matrix.pack(fill=tk.X, pady=4)
        
        # --- Panel Derecho (Resultados de Potencia Inversa) ---
        right_panel = tk.Frame(main_pane, bg="#121214")
        main_pane.add(right_panel, minsize=550)
        
        # Marco superior de resumen destacado de autovalor
        res_highlight_frame = tk.Frame(right_panel, bg="#1e1e24", padx=15, pady=15)
        res_highlight_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.lbl_eigenval_scale = tk.Label(res_highlight_frame, text="Autovalor (Escala λ): ---", bg="#1e1e24", fg="#ffffff", font=("Segoe UI", 11, "bold"))
        self.lbl_eigenval_scale.pack(anchor="w", pady=2)
        
        self.lbl_eigenval_ray = tk.Label(res_highlight_frame, text="Autovalor (Rayleigh λ_R): ---", bg="#1e1e24", fg="#00adb5", font=("Segoe UI", 11, "bold"))
        self.lbl_eigenval_ray.pack(anchor="w", pady=2)
        
        self.lbl_eigenvector = tk.Label(res_highlight_frame, text="Autovector asociado (v): ---", bg="#1e1e24", fg="#eeeeee", font=("Segoe UI", 10))
        self.lbl_eigenvector.pack(anchor="w", pady=2)
        
        self.lbl_iterations_count = tk.Label(res_highlight_frame, text="Iteraciones requeridas: ---", bg="#1e1e24", fg="#a0a0b0", font=("Segoe UI", 9, "italic"))
        self.lbl_iterations_count.pack(anchor="w", pady=2)
        
        # Tabla de iteraciones
        table_frame = tk.LabelFrame(right_panel, text=" Tabla de Iteraciones y Convergencia ", bg="#1e1e24", fg="#eeeeee",
                                    font=("Segoe UI", 10, "bold"), bd=1, relief="flat", padx=5, pady=5)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tbl_scroll_y = tk.Scrollbar(table_frame)
        tbl_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.eigen_tree = ttk.Treeview(table_frame, columns=("k", "lambda_s", "lambda_r", "error", "vector"), show="headings", yscrollcommand=tbl_scroll_y.set)
        self.eigen_tree.pack(fill=tk.BOTH, expand=True)
        tbl_scroll_y.config(command=self.eigen_tree.yview)
        
        self.eigen_tree.heading("k", text="Iter. (k)")
        self.eigen_tree.heading("lambda_s", text="λ (Escala)")
        self.eigen_tree.heading("lambda_r", text="λ (Rayleigh)")
        self.eigen_tree.heading("error", text="Error (Diferencia)")
        self.eigen_tree.heading("vector", text="Autovector v^(k)")
        
        self.eigen_tree.column("k", width=60, anchor=tk.CENTER)
        self.eigen_tree.column("lambda_s", width=120, anchor=tk.CENTER)
        self.eigen_tree.column("lambda_r", width=120, anchor=tk.CENTER)
        self.eigen_tree.column("error", width=120, anchor=tk.CENTER)
        self.eigen_tree.column("vector", width=240, anchor=tk.W)
        
    def update_matrix_grid(self):
        # Destruir widgets antiguos del frame
        for widget in self.matrix_grid_frame.winfo_children():
            widget.destroy()
            
        try:
            n = int(self.matrix_size_spin.get())
        except ValueError:
            return
            
        if n < 2 or n > 8:
            return
            
        self.matrix_entries = []
        
        # Configurar proporciones iguales para las columnas y filas de la cuadrícula
        for i in range(n):
            self.matrix_grid_frame.columnconfigure(i, weight=1)
            self.matrix_grid_frame.rowconfigure(i, weight=1)
            
        for r in range(n):
            row_entries = []
            for c in range(n):
                entry = tk.Entry(self.matrix_grid_frame, width=8, bg="#282830", fg="#ffffff",
                                 insertbackground="white", justify=tk.CENTER, font=("Consolas", 10),
                                 bd=0, highlightthickness=1, highlightbackground="#3e3e4a")
                entry.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
                
                # Matriz identidad por defecto
                val = "1.0" if r == c else "0.0"
                entry.insert(0, val)
                
                row_entries.append(entry)
            self.matrix_entries.append(row_entries)
            
    def load_default_matrix(self):
        example = [
            [4.0, 1.0, 0.0],
            [1.0, 3.0, -1.0],
            [0.0, -1.0, 2.0]
        ]
        self.matrix_size_spin.delete(0, tk.END)
        self.matrix_size_spin.insert(0, "3")
        self.update_matrix_grid()
        
        for r in range(3):
            for c in range(3):
                self.matrix_entries[r][c].delete(0, tk.END)
                self.matrix_entries[r][c].insert(0, str(example[r][c]))
                
        self.shift_entry.delete(0, tk.END)
        self.shift_entry.insert(0, "1.5")
        self.v0_entry.delete(0, tk.END)
        self.v0_entry.insert(0, "1 1 1")
        self.tol_entry.delete(0, tk.END)
        self.tol_entry.insert(0, "1e-6")
        self.max_iter_entry.delete(0, tk.END)
        self.max_iter_entry.insert(0, "80")
        
    def solve_inverse_power(self):
        try:
            n = int(self.matrix_size_spin.get())
            if n < 2 or n > 8:
                raise ValueError("La dimensión de la matriz debe estar entre 2 y 8.")
                
            # Leer valores de la matriz
            A = []
            for r in range(n):
                row = []
                for c in range(n):
                    cell_val = self.matrix_entries[r][c].get().strip()
                    if not cell_val:
                        raise ValueError(f"Falta ingresar valor en la celda ({r+1}, {c+1}).")
                    row.append(float(cell_val))
                A.append(row)
                
            # Leer parámetros del método
            shift_val = float(self.shift_entry.get())
            
            v0_text = self.v0_entry.get().strip()
            v0 = None
            if v0_text:
                parts = v0_text.split()
                if len(parts) != n:
                    raise ValueError(f"El vector inicial debe contener exactamente n={n} elementos separados por espacios.")
                v0 = [float(x) for x in parts]
                
            tol = float(self.tol_entry.get())
            if tol <= 0:
                raise ValueError("La tolerancia debe ser un número real positivo.")
                
            max_iter = int(self.max_iter_entry.get())
            if max_iter <= 0:
                raise ValueError("Las iteraciones máximas deben ser un número entero positivo.")
                
            # Ejecutar método de la potencia inversa
            iterations = nm.inverse_power_method(A, shift_val, v0, tol, max_iter)
            
            if not iterations:
                raise ValueError("El método no generó ninguna iteración.")
                
            final_it = iterations[-1]
            
            # Formatear el autovector para mostrar en la interfaz
            vec_formatted = "[" + ", ".join(f"{val:.6f}" for val in final_it['v']) + "]"
            
            # Actualizar labels principales
            self.lbl_eigenval_scale.config(text=f"Autovalor por Factor Escala (λ): {final_it['lambda_scale']:.8f}")
            self.lbl_eigenval_ray.config(text=f"Autovalor por Cociente Rayleigh (λ_R): {final_it['lambda_rayleigh']:.8f}")
            self.lbl_eigenvector.config(text=f"Autovector asociado (v): {vec_formatted}")
            self.lbl_iterations_count.config(text=f"Iteraciones requeridas: {len(iterations)} (Tolerancia alcanzada: {final_it['error']:.4e})")
            
            # Actualizar la tabla de iteraciones en la interfaz
            for item in self.eigen_tree.get_children():
                self.eigen_tree.delete(item)
                
            for it in iterations:
                k_step = it['k']
                lamb_s = f"{it['lambda_scale']:.7f}"
                lamb_r = f"{it['lambda_rayleigh']:.7f}"
                err = f"{it['error']:.2e}" if it['error'] != float('inf') else "---"
                v_str = "[" + ", ".join(f"{x:.4f}" for x in it['v']) + "]"
                self.eigen_tree.insert("", tk.END, values=(k_step, lamb_s, lamb_r, err, v_str))
                
        except Exception as err:
            messagebox.showerror("Error en Potencia Inversa", f"Error en el cálculo:\n{str(err)}")

    # =====================================================================
    # PESTAÑA 3: DOCUMENTACIÓN Y AYUDA INTERACTIVA
    # =====================================================================
    def build_tab_doc(self):
        doc_frame = tk.Frame(self.tab_doc, bg="#1a1a20", padx=15, pady=15)
        doc_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra de scroll
        doc_scroll = tk.Scrollbar(doc_frame)
        doc_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Campo de texto enriquecido (lectura)
        doc_text = tk.Text(doc_frame, bg="#1a1a20", fg="#eeeeee", insertbackground="white",
                           font=("Segoe UI", 10), wrap=tk.WORD, bd=0, yscrollcommand=doc_scroll.set)
        doc_text.pack(fill=tk.BOTH, expand=True)
        doc_scroll.config(command=doc_text.yview)
        
        # Redactar la documentación dirigida al equipo de trabajo
        doc_content = """DOCUMENTACIÓN TÉCNICA DEL PROYECTO DE ANÁLISIS NUMÉRICO
--------------------------------------------------------------------------------
Este software ha sido desarrollado para resolver problemas clave del programa de Análisis Numérico, organizados en dos grandes módulos con soporte de visualización gráfica e iteraciones detalladas.

1. MÓDULO DE SOLUCIÓN DE ECUACIONES DIFERENCIALES ORDINARIAS (EDO)
================================================================================
Permite aproximar numéricamente la función y(x) que soluciona el Problema de Valores Iniciales (PVI):
     y' = f(x, y),  con condición inicial y(a) = y_a en el intervalo [a, b].

MÉTODOS NUMÉRICOS DE EDO IMPLEMENTADOS:
--------------------------------------------------------------------------------
A) Euler Modificado (Método de Heun):
   Es un método predictor-corrector de segundo orden.
   - Predice el siguiente punto y*_{i+1} mediante un paso de Euler estándar:
         y*_{i+1} = y_i + h * f(x_i, y_i)
   - Corrige esta aproximación utilizando el promedio de las pendientes:
         y_{i+1} = y_i + (h / 2) * [ f(x_i, y_i) + f(x_{i+1}, y*_{i+1}) ]

B) Runge-Kutta de 4.º Orden (RK4):
   Es un método explícito de alta precisión (cuarto orden). Utiliza cuatro evaluaciones de pendiente ponderadas:
         k1 = f(x_i, y_i)
         k2 = f(x_i + h/2, y_i + (h/2)*k1)
         k3 = f(x_i + h/2, y_i + (h/2)*k2)
         k4 = f(x_i + h, y_i + h*k3)
         y_{i+1} = y_i + (h/6) * (k1 + 2*k2 + 2*k3 + k4)

C) Método de Milne (Predictor-Corrector):
   Método multipaso de cuarto orden. Requiere de 4 puntos iniciales para operar.
   - Inicialización: Se calculan y_0, y_1, y_2, y_3 mediante RK4.
   - Predictor de Milne:
         y*_{i+1} = y_{i-3} + (4h / 3) * [ 2*f_i - f_{i-1} + 2*f_{i-2} ]
   - Corrector de Milne (iterado para estabilidad):
         y_{i+1} = y_{i-1} + (h / 3) * [ f(x_{i+1}, y*_{i+1}) + 4*f_i + f_{i-1} ]


MÉTODOS DE INTERPOLACIÓN APLICADOS:
--------------------------------------------------------------------------------
Dado un punto x0 ∈ (a, b) que no se encuentra exactamente sobre los nodos de la grilla calculada, el software realiza una selección de los 'k' puntos vecinos más cercanos (para prevenir oscilaciones numéricas de Runge) y aplica uno de los siguientes polinomios:

A) Polinomio de Lagrange:
   Construye las bases polinómicas L_j(x):
         L_j(x) = Π_{m ≠ j} [ (x - x_m) / (x_j - x_m) ]
   Y evalúa el polinomio interpolador:
         P(x) = Σ_{j=0}^{k-1} y_j * L_j(x)

B) Polinomio de Newton con Diferencias Divididas:
   Construye de manera óptima la tabla de diferencias divididas donde:
         f[x_i, x_{i+1}] = (f[x_{i+1}] - f[x_i]) / (x_{i+1} - x_i)
   El polinomio se expresa y evalúa recursivamente:
         P(x) = f[x_0] + f[x_0, x_1](x - x_0) + f[x_0, x_1, x_2](x - x_0)(x - x_1) + ...
   El programa expone visualmente la tabla completa de diferencias divididas en la interfaz de usuario.


2. MÓDULO DEL MÉTODO DE LA POTENCIA INVERSA CON SHIFT
================================================================================
Permite encontrar el autovalor (y su autovector asociado) más cercano a un valor de desplazamiento dado (Shift, α) para una matriz cuadrada A de orden n.

ALGORITMO DETALLADO:
--------------------------------------------------------------------------------
1. Se define la matriz desplazada M = A - α * I.
2. Se toma un vector inicial v^(0) (por defecto, todos sus valores son 1.0).
3. En cada iteración k:
   - Se resuelve el sistema lineal: (A - α * I) * y = v^(k-1)
     Este sistema se resuelve mediante una implementación de Eliminación Gaussiana con Pivoteo Parcial desarrollado de forma nativa para máxima robustez.
   - Se busca el elemento de máxima magnitud de y, denominado y_max.
   - Se aproxima el autovalor (Método del factor de escala):
         λ_escala = α + 1 / y_max
   - Se normaliza el vector para la siguiente iteración:
         v^(k) = y / y_max
   - De manera paralela, el programa calcula el Cociente de Rayleigh:
         λ_Rayleigh = (v^T * A * v) / (v^T * v)
         (Este cociente acelera la tasa de convergencia del autovalor).
4. El proceso se detiene cuando el cambio absoluto entre aproximaciones de autovalores sucesivas es inferior a la tolerancia establecida (|λ_k - λ_{k-1}| < ε).


INSTRUCCIONES PARA EL EQUIPO DE TRABAJO (CÓMO USAR LA APP)
================================================================================
- Para EDO:
  1. Escriba la ecuación usando notación de Python (ej. x**2 - y o sin(x) + cos(y)).
  2. Ingrese el intervalo, la condición inicial y el número de pasos deseados.
  3. Indique el punto a evaluar x0 y la cantidad k de puntos que formarán el polinomio.
  4. Presione 'RESOLVER Y GRAFICAR'. Puede mover el mouse sobre el gráfico para ver la información detallada de cada punto en un tooltip flotante.
  5. Navegue por las subpestañas inferiores para ver la tabla de pasos o el desglose matemático detallado con la tabla de diferencias.

- Para Autovalores (Potencia Inversa):
  1. Defina la dimensión de la matriz (n). La interfaz adaptará las celdas automáticamente.
  2. Complete la matriz ingresando coeficientes.
  3. Establezca el valor de desplazamiento de búsqueda (Shift, por defecto 0.0, lo que buscará el autovalor de menor magnitud absoluta).
  4. Ingrese opcionalmente el vector inicial (separado por espacios, ej. '1 0 1') o déjelo en blanco para arrancar con el vector de unos.
  5. Presione 'CALCULAR AUTOVALOR'.
  6. Visualice en la derecha los autovalores finales y la tabla paso a paso que describe la convergencia del método.
"""
        doc_text.insert("1.0", doc_content)
        # Configurar campo como de solo lectura
        doc_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    app = NumericApp()
    app.mainloop()
