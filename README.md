# Proyecto de Análisis Numérico - Examen Integrador

Este repositorio contiene la solución completa para el Examen Integrador de Análisis Numérico de la carrera de Ingeniería en Sistemas de Información (I.S.I.) de la **Universidad de la Cuenca del Plata**.

El proyecto es una aplicación de escritorio desarrollada en **Python** utilizando **Tkinter** para la interfaz gráfica. Cuenta con un diseño moderno (tema oscuro premium), es interactivo y no requiere de dependencias externas complejas (se ejecuta directamente en cualquier instalación de Python 3).

---

## Estructura del Proyecto

El código está estructurado de manera modular y limpia para facilitar su comprensión, mantenimiento y extensión:

*   **[`main.py`](file:///C:/Users/Usuario/Documents/GitHub/Interpolado---Analisis-Numerico/main.py)**: Punto de entrada de la aplicación. Gestiona la interfaz gráfica de usuario (GUI), la validación de los datos ingresados, el manejo de eventos y la renderización de tablas de iteración.
*   **[`numerical_methods.py`](file:///C:/Users/Usuario/Documents/GitHub/Interpolado---Analisis-Numerico/numerical_methods.py)**: Contiene toda la lógica matemática de los algoritmos de resolución. Es un módulo puro independiente de la interfaz gráfica.
*   **[`custom_plot.py`](file:///C:/Users/Usuario/Documents/GitHub/Interpolado---Analisis-Numerico/custom_plot.py)**: Un widget graficador interactivo personalizado desarrollado de manera nativa sobre `tkinter.Canvas`. Grafica grillas, ejes cartesianos, curvas continuas y puntos discretos, e implementa información flotante (*tooltips*) interactiva al pasar el mouse por encima de los puntos de la solución y la interpolación.

---

## Fundamentos Matemáticos y Algorítmicos

### Módulo 1: EDO e Interpolación

#### 1. Ecuaciones Diferenciales Ordinarias (EDO)
El programa permite resolver problemas de valor inicial (PVI) de primer orden de la forma:
$$y' = f(x, y), \quad y(a) = y_a, \quad x \in [a, b]$$
El usuario ingresa la expresión $f(x, y)$ en lenguaje matemático estándar (por ejemplo, `x**2 - y` o `cos(x) - y`), la cual es evaluada de manera segura mediante un entorno controlado que previene inyección de código.

Los métodos numéricos implementados son:

*   **Euler Modificado (Método de Heun)**: Método predictor-corrector de segundo orden.
    *   *Predictor (Euler simple)*:
        $$y_{i+1}^* = y_i + h \cdot f(x_i, y_i)$$
    *   *Corrector (Regla del trapecio)*:
        $$y_{i+1} = y_i + \frac{h}{2} \cdot \left[ f(x_i, y_i) + f(x_{i+1}, y_{i+1}^*) \right]$$
*   **Runge-Kutta de 4.º Orden (RK4)**: Método explícito de alta precisión (cuarto orden). Utiliza cuatro pendientes auxiliares:
    $$k_1 = f(x_i, y_i)$$
    $$k_2 = f\left(x_i + \frac{h}{2}, y_i + \frac{h}{2} k_1\right)$$
    $$k_3 = f\left(x_i + \frac{h}{2}, y_i + \frac{h}{2} k_2\right)$$
    $$k_4 = f(x_i + h, y_i + h k_3)$$
    $$y_{i+1} = y_i + \frac{h}{6} \cdot (k_1 + 2k_2 + 2k_3 + k_4)$$
*   **Método Predictor-Corrector de Milne**: Método multipaso de cuarto orden. Requiere de cuatro puntos iniciales para arrancar.
    *   *Inicialización*: Se calculan $y_0, y_1, y_2, y_3$ mediante RK4.
    *   *Predictor*:
        $$y_{i+1}^* = y_{i-3} + \frac{4h}{3} \cdot \left[ 2f(x_i, y_i) - f(x_{i-1}, y_{i-1}) + 2f(x_{i-2}, y_{i-2}) \right]$$
    *   *Corrector iterativo*: Se itera la siguiente fórmula hasta que converja:
        $$y_{i+1}^{(j+1)} = y_{i-1} + \frac{h}{3} \cdot \left[ f(x_{i+1}, y_{i+1}^{(j)}) + 4f(x_i, y_i) + f(x_{i-1}, y_{i-1}) \right]$$

#### 2. Interpolación
Dado un valor $x_0 \in (a, b)$ que no coincide exactamente con los pasos de la grilla $x_i$, el sistema realiza una **selección inteligente de los $k$ puntos de la grilla más cercanos a $x_0$** (para mitigar el fenómeno de Runge y evitar oscilaciones innecesarias de polinomios de grado muy alto). Luego, aplica uno de los siguientes métodos para aproximar $y(x_0)$:

*   **Polinomio de Lagrange**: Construye los términos cardinales de Lagrange $L_i(x)$:
    $$L_i(x) = \prod_{j \neq i} \frac{x - x_j}{x_i - x_j}$$
    El valor interpolado se calcula como:
    $$P(x_0) = \sum_{i=0}^{k-1} y_i \cdot L_i(x_0)$$
*   **Polinomio de Newton (Diferencias Divididas)**: Construye la tabla de diferencias divididas donde:
    $$f[x_i, x_{i+1}] = \frac{f[x_{i+1}] - f[x_i]}{x_{i+1} - x_i}$$
    $$f[x_i, x_{i+1}, \dots, x_{i+m}] = \frac{f[x_{i+1}, \dots, x_{i+m}] - f[x_i, \dots, x_{i+m-1}]}{x_{i+m} - x_i}$$
    El polinomio interpolador se evalúa como:
    $$P(x_0) = f[x_0] + f[x_0, x_1](x_0 - x_0) + f[x_0, x_1, x_2](x_0 - x_0)(x_0 - x_1) + \dots$$
    La aplicación muestra en pantalla la **tabla de diferencias divididas completa** y los pasos detallados de la evaluación.

---

### Módulo 2: Autovalores y Autovectores (Potencia Inversa con Shift)

El método de la potencia inversa calcula el autovalor y el correspondiente autovector de una matriz $A$ de orden $n \times n$ más cercano a un valor de desplazamiento dado (Shift, $\alpha$).

#### Algoritmo:
1. Se define la matriz desplazada $M = A - \alpha I$.
2. Se inicia con un vector normalizado $v^{(0)}$ (por defecto, el vector de unos $[1, 1, \dots, 1]^T$).
3. Para cada iteración $k = 1, 2, \dots$:
    1.  Se resuelve el sistema lineal:
        $$(A - \alpha I) y^{(k)} = v^{(k-1)}$$
        Este sistema se resuelve mediante **Eliminación Gaussiana con Pivoteo Parcial** y sustitución hacia atrás.
    2.  Se determina la componente de mayor magnitud de $y^{(k)}$, denotada como $\mu_k = \|y^{(k)}\|_\infty$.
    3.  Se estima el autovalor aproximado usando el factor de escala:
        $$\lambda_{escala}^{(k)} = \alpha + \frac{1}{\mu_k}$$
    4.  Se normaliza el vector para la siguiente iteración:
        $$v^{(k)} = \frac{y^{(k)}}{\mu_k}$$
    5.  Se calcula el **Cociente de Rayleigh** para acelerar la convergencia:
        $$\lambda_{Rayleigh}^{(k)} = \frac{(v^{(k)})^T A v^{(k)}}{(v^{(k)})^T v^{(k)}}$$
4.  El algoritmo converge cuando el cambio en la estimación del autovalor es menor que la tolerancia fijada:
    $$|\lambda_{escala}^{(k)} - \lambda_{escala}^{(k-1)}| < \epsilon$$

---

## Cómo Ejecutar el Proyecto

### Requisitos Previos
El proyecto fue diseñado utilizando únicamente la **biblioteca estándar de Python 3** (incluyendo Tkinter). Por lo tanto, no requiere instalar ninguna dependencia de terceros (como NumPy o Matplotlib).

*   Tener instalado Python 3.6 o superior.
*   En sistemas Linux, asegúrese de tener instalado el paquete de soporte de Tkinter (en Ubuntu/Debian: `sudo apt install python3-tk`).

### Ejecución
Abra la terminal en el directorio del proyecto y ejecute:

```bash
python main.py
```

---

## Guía de Uso para el Equipo de Trabajo

### 1. Sección de EDO e Interpolación
1.  **Ingreso de la EDO**: En el campo `Ecuación y' = f(x, y)` ingrese la función usando operadores de Python (ej. `x**2 - y` o `sin(x) - y`).
2.  **Parámetros de Intervalo**: Indique el rango $[a, b]$ y la condición de frontera inicial $y(a)$.
3.  **Partición**: Modifique el número de intervalos `N`. El paso $h$ se calculará automáticamente como $(b-a)/N$.
4.  **Interpolación**: Ingrese el valor de $x_0$ a evaluar (debe estar contenido dentro de $(a, b)$) y la cantidad de puntos de apoyo `k`.
5.  **Método**: Seleccione el método de EDO (Heun, RK4 o Milne) y el de interpolación (Lagrange o Newton).
6.  **Acción**: Presione `RESOLVER Y GRAFICAR`.
    *   *Gráfico Canvas*: Se actualizará mostrando la curva del método y el punto de interpolación destacado. Al mover el puntero por el gráfico, aparecerá un recuadro interactivo indicando las coordenadas exactas de los puntos.
    *   *Resultados de Pasos*: Muestra la tabla detallada de todas las aproximaciones $(x_i, y_i)$ de la grilla.
    *   *Detalle de Interpolación*: Si selecciona el método de Newton, mostrará la matriz completa de diferencias divididas construida a partir de los $k$ puntos más cercanos a $x_0$.

### 2. Sección de Potencia Inversa
1.  **Dimensión**: Seleccione el orden de la matriz $n$ en el selector numérico. La cuadrícula de entradas inferiores se adaptará dinámicamente.
2.  **Coeficientes**: Rellene las casillas de la matriz $A$.
3.  **Configuración**: Ingrese el desplazamiento $\alpha$ (Shift). Si desea buscar el autovalor de menor magnitud absoluta, deje el Shift en `0.0`.
4.  **Parámetros del Solver**: Especifique opcionalmente un vector inicial $v^{(0)}$ separando sus componentes por espacios (ej. `1 0.5 1`). Establezca la tolerancia $\epsilon$ y las iteraciones máximas.
5.  **Acción**: Presione `CALCULAR AUTOVALOR`.
    *   El programa mostrará las estimaciones del autovalor calculadas por factor de escala y por Cociente de Rayleigh, así como el autovector asociado normalizado.
    *   La tabla inferior desglosará iteración por iteración el autovalor y el error, permitiendo ver el proceso de convergencia detalladamente.
