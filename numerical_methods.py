"""
Módulo matemático que implementa los algoritmos de análisis numérico para:
1. Solucionadores de Ecuaciones Diferenciales Ordinarias (EDO):
   - Euler Modificado (Heun)
   - Runge-Kutta de 4.º orden (RK4)
   - Método predictor-corrector de Milne
2. Interpolación polinómica:
   - Polinomio de Lagrange
   - Polinomio de Newton (con tabla de diferencias divididas)
3. Álgebra Lineal:
   - Resolución de sistemas lineales mediante Eliminación Gaussiana con Pivoteo Parcial
   - Método de la Potencia Inversa con desplazamiento (shift) y Cociente de Rayleigh
4. Utilidades:
   - Evaluador seguro de expresiones matemáticas en formato de cadena de caracteres.
"""

import math
import re

# Diccionario seguro con funciones matemáticas de la biblioteca estándar
SAFE_MATH = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    'exp': math.exp,
    'log': math.log,
    'log10': math.log10,
    'sqrt': math.sqrt,
    'pi': math.pi,
    'e': math.e,
    'abs': abs,
    'pow': pow,
}

def validate_expression(expr: str) -> None:
    """
    Valida que la expresión matemática solo contenga caracteres seguros para evitar ejecución de código.
    """
    # Permitir letras, números, espacios y operadores básicos de matemáticas
    allowed_pattern = re.compile(r'^[a-zA-Z0-9\s\+\-\*\/\(\)\.\,\^]+$')
    if not allowed_pattern.match(expr):
        raise ValueError("La expresión contiene caracteres no permitidos.")
    
    # Prevenir uso de palabras clave sospechosas
    for keyword in ['__', 'import', 'eval', 'exec', 'getattr', 'globals', 'locals', 'sys', 'os']:
        if keyword in expr:
            raise ValueError(f"La expresión contiene términos prohibidos: '{keyword}'")

def parse_and_eval(expr: str, x: float, y: float) -> float:
    """
    Evalúa una expresión matemática dada como string en el punto (x, y) de forma segura.
    Soporta notación estándar de Python. También reemplaza '^' por '**' por conveniencia.
    """
    expr_clean = expr.replace('^', '**')
    validate_expression(expr_clean)
    
    context = dict(SAFE_MATH)
    context['x'] = float(x)
    context['y'] = float(y)
    
    try:
        # Se evalúa en un entorno limpio sin acceso a __builtins__
        val = float(eval(expr_clean, {"__builtins__": {}}, context))
        return val
    except ZeroDivisionError:
        raise ValueError(f"División por cero al evaluar f({x}, {y})")
    except ValueError as ve:
        raise ValueError(f"Error matemático al evaluar f({x}, {y}): {str(ve)}")
    except Exception as e:
        raise ValueError(f"Error al evaluar la expresión '{expr}' en ({x}, {y}): {str(e)}")


# =====================================================================
# 1. MÉTODOS DE SOLUCIÓN DE ECUACIONES DIFERENCIALES ORDINARIAS (EDO)
# =====================================================================

def solve_heun(f_expr: str, a: float, b: float, y_a: float, h: float):
    """
    Resuelve el PVI y' = f(x,y) en [a,b] con y(a)=y_a usando el método de Euler Modificado (Heun).
    """
    N = int(round((b - a) / h))
    if N <= 0:
        raise ValueError("El paso 'h' es demasiado grande para el intervalo proporcionado.")
    
    h_actual = (b - a) / N
    x = [a + i * h_actual for i in range(N + 1)]
    y = [0.0] * (N + 1)
    y[0] = y_a
    
    for i in range(N):
        xi = x[i]
        yi = y[i]
        x_next = x[i+1]
        
        # Evaluamos la pendiente en el punto actual
        f_curr = parse_and_eval(f_expr, xi, yi)
        
        # Predictor (Paso de Euler estándar)
        y_pred = yi + h_actual * f_curr
        
        # Corrector (Regla del trapecio usando la pendiente predicha)
        f_next = parse_and_eval(f_expr, x_next, y_pred)
        y[i+1] = yi + (h_actual / 2.0) * (f_curr + f_next)
        
    return x, y, h_actual


def solve_rk4(f_expr: str, a: float, b: float, y_a: float, h: float):
    """
    Resuelve el PVI y' = f(x,y) en [a,b] con y(a)=y_a usando el método de Runge-Kutta de 4.º orden (RK4).
    """
    N = int(round((b - a) / h))
    if N <= 0:
        raise ValueError("El paso 'h' es demasiado grande para el intervalo proporcionado.")
    
    h_actual = (b - a) / N
    x = [a + i * h_actual for i in range(N + 1)]
    y = [0.0] * (N + 1)
    y[0] = y_a
    
    for i in range(N):
        xi = x[i]
        yi = y[i]
        
        k1 = parse_and_eval(f_expr, xi, yi)
        k2 = parse_and_eval(f_expr, xi + h_actual / 2.0, yi + (h_actual / 2.0) * k1)
        k3 = parse_and_eval(f_expr, xi + h_actual / 2.0, yi + (h_actual / 2.0) * k2)
        k4 = parse_and_eval(f_expr, xi + h_actual, yi + h_actual * k3)
        
        y[i+1] = yi + (h_actual / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        
    return x, y, h_actual


def solve_milne(f_expr: str, a: float, b: float, y_a: float, h: float):
    """
    Resuelve el PVI y' = f(x,y) en [a,b] con y(a)=y_a usando el método Predictor-Corrector de Milne.
    Requiere al menos 4 puntos para arrancar (N >= 3). Los primeros 3 pasos se obtienen mediante RK4.
    """
    N = int(round((b - a) / h))
    if N < 3:
        raise ValueError("El método de Milne requiere al menos 3 intervalos (N >= 3, es decir, 4 puntos) para inicializarse. Aumente el número de pasos o reduzca 'h'.")
    
    h_actual = (b - a) / N
    x = [a + i * h_actual for i in range(N + 1)]
    y = [0.0] * (N + 1)
    y[0] = y_a
    
    # 1. Inicializar los primeros 3 pasos (y1, y2, y3) usando RK4
    for i in range(3):
        xi = x[i]
        yi = y[i]
        
        k1 = parse_and_eval(f_expr, xi, yi)
        k2 = parse_and_eval(f_expr, xi + h_actual / 2.0, yi + (h_actual / 2.0) * k1)
        k3 = parse_and_eval(f_expr, xi + h_actual / 2.0, yi + (h_actual / 2.0) * k2)
        k4 = parse_and_eval(f_expr, xi + h_actual, yi + h_actual * k3)
        
        y[i+1] = yi + (h_actual / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        
    # Guardamos los valores evaluados de f
    f_val = [0.0] * (N + 1)
    for i in range(4):
        f_val[i] = parse_and_eval(f_expr, x[i], y[i])
        
    # 2. Iteraciones del método de Milne
    for i in range(3, N):
        # Predictor de Milne:
        y_pred = y[i-3] + (4.0 * h_actual / 3.0) * (2.0 * f_val[i] - f_val[i-1] + 2.0 * f_val[i-2])
        
        # Corrector iterativo (hasta estabilidad o máx 5 iteraciones)
        y_curr = y_pred
        for _ in range(5):
            f_pred = parse_and_eval(f_expr, x[i+1], y_curr)
            y_next = y[i-1] + (h_actual / 3.0) * (f_pred + 4.0 * f_val[i] + f_val[i-1])
            if abs(y_next - y_curr) < 1e-11:
                y_curr = y_next
                break
            y_curr = y_next
            
        y[i+1] = y_curr
        f_val[i+1] = parse_and_eval(f_expr, x[i+1], y[i+1])
        
    return x, y, h_actual


# =====================================================================
# 2. MÉTODOS DE INTERPOLACIÓN
# =====================================================================

def select_nearest_points(x: list[float], y: list[float], x0: float, k: int = 4):
    """
    Selecciona los k puntos más cercanos a x0 de entre los conjuntos x e y para la interpolación.
    Ordena los puntos resultantes ascendentemente por su coordenada x.
    """
    k = min(k, len(x))
    if k < 2:
        raise ValueError("Se necesitan al menos 2 puntos para interpolar.")
        
    # Calculamos distancias a x0
    indexed_distances = [(i, abs(x[i] - x0)) for i in range(len(x))]
    # Ordenamos por distancia
    indexed_distances.sort(key=lambda item: item[1])
    # Obtenemos los k índices más cercanos y los ordenamos para mantener la secuencia de x
    selected_indices = [item[0] for item in indexed_distances[:k]]
    selected_indices.sort()
    
    x_sel = [x[idx] for idx in selected_indices]
    y_sel = [y[idx] for idx in selected_indices]
    return x_sel, y_sel


def interpolate_lagrange(x_pts: list[float], y_pts: list[float], x0: float):
    """
    Aplica interpolación polinómica de Lagrange para estimar y(x0).
    Retorna el valor interpolado y la lista de coeficientes L_i(x0) con fines educativos.
    """
    n = len(x_pts)
    y_interp = 0.0
    terms = []
    
    for i in range(n):
        num = 1.0
        den = 1.0
        for j in range(n):
            if i != j:
                num *= (x0 - x_pts[j])
                den *= (x_pts[i] - x_pts[j])
        l_i = num / den
        y_interp += y_pts[i] * l_i
        terms.append((x_pts[i], y_pts[i], l_i))
        
    return y_interp, terms


def interpolate_newton(x_pts: list[float], y_pts: list[float], x0: float):
    """
    Aplica interpolación polinómica de Newton (Diferencias Divididas).
    Retorna:
      - y_interp: el valor estimado en x0.
      - formatted_table: la tabla de diferencias divididas para mostrar en interfaz.
      - steps: la descripción paso a paso del cálculo matemático.
    """
    n = len(x_pts)
    table = [[0.0] * n for _ in range(n)]
    
    # Primera columna es f[x_i] = y_i
    for i in range(n):
        table[i][0] = y_pts[i]
        
    # Construcción de la tabla de diferencias divididas
    for j in range(1, n):
        for i in range(n - j):
            table[i][j] = (table[i+1][j-1] - table[i][j-1]) / (x_pts[i+j] - x_pts[i])
            
    # Evaluación del polinomio en x0: P(x0) = f[x0] + f[x0, x1](x0 - x0) + ...
    y_interp = table[0][0]
    mult = 1.0
    steps = [f"P(x0) = f[x_0] ({table[0][0]:.6f})"]
    
    for j in range(1, n):
        mult *= (x0 - x_pts[j-1])
        term = table[0][j] * mult
        y_interp += term
        steps.append(f" + f[x_0..x_{j}] * Π(x0 - x_i) = {table[0][j]:+.6f} * {mult:.6f} ({term:+.6f})")
        
    # Dar formato a la tabla para la GUI
    formatted_table = []
    for i in range(n):
        row = [x_pts[i]]
        for j in range(n - i):
            row.append(table[i][j])
        formatted_table.append(row)
        
    return y_interp, formatted_table, steps


# =====================================================================
# 3. ALGORITMOS DE ÁLGEBRA LINEAL Y MÉTODO DE LA POTENCIA INVERSA
# =====================================================================

def solve_linear_system(A_mat: list[list[float]], b_vec: list[float]) -> list[float]:
    """
    Resuelve el sistema lineal A * x = b utilizando Eliminación Gaussiana con Pivoteo Parcial.
    """
    n = len(A_mat)
    # Crear matriz aumentada [A | b] trabajando con copias para no mutar el original
    B = [row[:] + [b_val] for row, b_val in zip(A_mat, b_vec)]
    
    # Eliminación hacia adelante
    for i in range(n):
        # Búsqueda del pivote parcial
        pivot_row = i
        max_val = abs(B[i][i])
        for r in range(i + 1, n):
            val = abs(B[r][i])
            if val > max_val:
                max_val = val
                pivot_row = r
                
        # Intercambiar filas si es necesario
        if pivot_row != i:
            B[i], B[pivot_row] = B[pivot_row], B[i]
            
        # Validar si es singular o casi singular
        if abs(B[i][i]) < 1e-12:
            raise ValueError("El sistema no tiene solución única (matriz singular o mal condicionada).")
            
        # Anular elementos inferiores de la columna
        for r in range(i + 1, n):
            factor = B[r][i] / B[i][i]
            for c in range(i, n + 1):
                B[r][c] -= factor * B[i][c]
                
    # Sustitución hacia atrás
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = sum(B[i][c] * x[c] for c in range(i + 1, n))
        x[i] = (B[i][n] - s) / B[i][i]
        
    return x


def mat_vec_mul(A: list[list[float]], v: list[float]) -> list[float]:
    """Multiplica una matriz de n x n por un vector de dimensión n."""
    n = len(A)
    return [sum(A[i][j] * v[j] for j in range(n)) for i in range(n)]


def dot_product(u: list[float], v: list[float]) -> float:
    """Calcula el producto punto entre dos vectores."""
    return sum(ui * vi for ui, vi in zip(u, v))


def inverse_power_method(A: list[list[float]], shift: float, v0: list[float] = None, tol: float = 1e-6, max_iter: int = 100):
    """
    Calcula el autovalor más cercano a 'shift' y su autovector correspondiente usando el Método de la Potencia Inversa.
    Retorna una lista de diccionarios con el historial de cada iteración.
    """
    n = len(A)
    if v0 is None:
        v = [1.0] * n
    else:
        v = [float(x) for x in v0]
        
    # Normalizar vector inicial (usando norma infinito)
    v_norm = max(abs(x) for x in v)
    if v_norm < 1e-12:
        raise ValueError("El vector inicial no puede ser el vector nulo.")
    v = [x / v_norm for x in v]
    
    # Construir la matriz desplazada M = A - shift * I
    M = [[A[i][j] - (shift if i == j else 0.0) for j in range(n)] for i in range(n)]
    
    iterations = []
    prev_lambda = None
    
    for k in range(1, max_iter + 1):
        try:
            # Resolvemos (A - shift*I) * y = v
            y = solve_linear_system(M, v)
        except ValueError as e:
            raise ValueError(f"Error al resolver el sistema en la iteración {k}: {str(e)}. Intente usar otro shift o revise los datos.")
            
        # Determinar el elemento de mayor magnitud de y (norma infinito)
        y_max_val = y[0]
        for val in y:
            if abs(val) > abs(y_max_val):
                y_max_val = val
                
        if abs(y_max_val) < 1e-15:
            raise ValueError("El vector calculado colapsó al vector nulo en la iteración.")
            
        # El autovalor estimado por factor de escala es: shift + 1 / y_max_val
        lambda_scale = shift + (1.0 / y_max_val)
        
        # Normalizar vector para el siguiente paso: v_next = y / y_max_val
        v_next = [val / y_max_val for val in y]
        
        # Cociente de Rayleigh para aproximar con mayor orden de convergencia: Ray = (v^T * A * v) / (v^T * v)
        Av_next = mat_vec_mul(A, v_next)
        num = dot_product(v_next, Av_next)
        den = dot_product(v_next, v_next)
        lambda_rayleigh = num / den if den != 0.0 else shift
        
        # Error estimado como la diferencia de la estimación del autovalor
        if prev_lambda is not None:
            error = abs(lambda_scale - prev_lambda)
        else:
            error = float('inf')
            
        # Guardamos información de esta iteración
        iterations.append({
            'k': k,
            'v': v_next[:],
            'y_solve': y[:],
            'lambda_scale': lambda_scale,
            'lambda_rayleigh': lambda_rayleigh,
            'error': error
        })
        
        # Criterio de parada
        if error < tol:
            break
            
        v = v_next
        prev_lambda = lambda_scale
        
    return iterations
