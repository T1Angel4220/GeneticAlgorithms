import threading
import tkinter as tk
from tkinter import ttk, messagebox

from nucleo.ambiente import AmbienteIluminacion
from algoritmos.ascenso_colinas_estocastico import busqueda_ascenso_colinas_estocastico
from algoritmos.algoritmo_genetico import ejecutar_algoritmo_genetico

class AplicacionIluminacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Agente de Optimización de Iluminación y Costo - 6 Focos (7x8m)")
        self.root.geometry("1150x780")
        self.root.configure(bg="#1e1e2e")

        self.estado_actual = AmbienteIluminacion.generar_estado_aleatorio()
        self.historial_estados = [self.estado_actual]
        self.historial_fitness = []
        self.indice_animacion = 0
        self.animando = False

        self._configurar_estilos()
        self._crear_interfaz()
        self._redibujar_plano(self.estado_actual)

    def _configurar_estilos(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TNotebook", background="#1e1e2e", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#313244", foreground="#cdd6f4", padding=[14, 7], font=("Segoe UI", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", "#45475a")], foreground=[("selected", "#89b4fa")])

        self.style.configure("TLabelframe", background="#1e1e2e", foreground="#cdd6f4", borderwidth=1, relief="solid")
        self.style.configure("TLabelframe.Label", background="#1e1e2e", foreground="#89b4fa", font=("Segoe UI", 11, "bold"))

        self.style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 15, "bold"), foreground="#cdd6f4")
        self.style.configure("Metric.TLabel", font=("Segoe UI", 10, "bold"), foreground="#a6e3a1")

        self.style.configure("TButton", background="#45475a", foreground="#cdd6f4", font=("Segoe UI", 10, "bold"), borderwidth=0, padding=6)
        self.style.map("TButton", background=[("active", "#585b70")])

        self.style.configure("Primary.TButton", background="#89b4fa", foreground="#11111b", font=("Segoe UI", 10, "bold"), padding=8)
        self.style.map("Primary.TButton", background=[("active", "#b4befe")])

        self.style.configure("Treeview", background="#313244", foreground="#cdd6f4", fieldbackground="#313244", rowheight=28, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", background="#45475a", foreground="#89b4fa", font=("Segoe UI", 10, "bold"))

    def _crear_interfaz(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        tab_simulador = ttk.Frame(notebook)
        tab_comparativa = ttk.Frame(notebook)

        notebook.add(tab_simulador, text="Simulador 2D & Algoritmos")
        notebook.add(tab_comparativa, text="Matriz Comparativa de Métricas")

        self._crear_pestana_simulador(tab_simulador)
        self._crear_pestana_comparativa(tab_comparativa)

    def _crear_pestana_simulador(self, parent):
        frame_izq = ttk.Frame(parent)
        frame_izq.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        frame_der = ttk.Frame(parent)
        frame_der.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        lbl_titulo = ttk.Label(frame_izq, text="Plano 2D del Área (7m x 8m - 56 Celdas)", style="Header.TLabel")
        lbl_titulo.pack(pady=(0, 5))

        self.canvas_plano = tk.Canvas(frame_izq, width=455, height=520, bg="#181825", highlightthickness=2, highlightbackground="#45475a")
        self.canvas_plano.pack(pady=5)

        frame_anim = ttk.LabelFrame(frame_izq, text="Control de Animación de Optimización")
        frame_anim.pack(fill="x", pady=5)

        btn_prev = ttk.Button(frame_anim, text="Anterior", command=self._paso_anterior)
        btn_prev.pack(side="left", padx=5, pady=5)

        self.btn_play = ttk.Button(frame_anim, text="Reproducir", command=self._toggle_animacion)
        self.btn_play.pack(side="left", padx=5, pady=5)

        btn_next = ttk.Button(frame_anim, text="Siguiente", command=self._paso_siguiente)
        btn_next.pack(side="left", padx=5, pady=5)

        btn_reset = ttk.Button(frame_anim, text="Reiniciar", command=self._reiniciar_animacion)
        btn_reset.pack(side="left", padx=5, pady=5)

        self.lbl_paso_actual = ttk.Label(frame_anim, text="Paso: 0 / 0", style="Metric.TLabel")
        self.lbl_paso_actual.pack(side="right", padx=10)

        frame_config = ttk.LabelFrame(frame_der, text="Configuración de Parámetros")
        frame_config.pack(fill="x", pady=(0, 10))

        btn_aleatorio = ttk.Button(frame_config, text="Generar Configuración Aleatoria de 6 Focos", command=self._generar_aleatorio)
        btn_aleatorio.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_config, text="Algoritmo de Optimización:").pack(anchor="w", padx=10, pady=(5, 2))
        self.combo_algoritmo = ttk.Combobox(
            frame_config,
            values=["Ascenso de Colinas Estocástico", "Algoritmo Genético"],
            state="readonly"
        )
        self.combo_algoritmo.current(0)
        self.combo_algoritmo.pack(fill="x", padx=10, pady=2)

        frame_params = ttk.Frame(frame_config)
        frame_params.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_params, text="Población / Iteraciones:").grid(row=0, column=0, sticky="w", pady=2)
        self.spin_poblacion = ttk.Spinbox(frame_params, from_=10, to=200, increment=10, width=8)
        self.spin_poblacion.set(20)
        self.spin_poblacion.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame_params, text="Tasa Mutación (%):").grid(row=1, column=0, sticky="w", pady=2)
        self.spin_mutacion = ttk.Spinbox(frame_params, from_=1, to=50, increment=1, width=8)
        self.spin_mutacion.set(10)
        self.spin_mutacion.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(frame_params, text="Generaciones / Pasos:").grid(row=2, column=0, sticky="w", pady=2)
        self.spin_generaciones = ttk.Spinbox(frame_params, from_=10, to=500, increment=10, width=8)
        self.spin_generaciones.set(100)
        self.spin_generaciones.grid(row=2, column=1, padx=5, pady=2)

        self.btn_ejecutar = ttk.Button(frame_config, text="Ejecutar Optimización de Iluminación", style="Primary.TButton", command=self._ejecutar_optimizacion)
        self.btn_ejecutar.pack(fill="x", padx=10, pady=10)

        frame_metricas = ttk.LabelFrame(frame_der, text="Métricas del Algoritmo")
        frame_metricas.pack(fill="x", pady=5)

        self.lbl_cobertura = ttk.Label(frame_metricas, text="Cobertura de Iluminación: - %")
        self.lbl_cobertura.pack(anchor="w", padx=10, pady=2)

        self.lbl_costo = ttk.Label(frame_metricas, text="Consumo Total: - Watts")
        self.lbl_costo.pack(anchor="w", padx=10, pady=2)

        self.lbl_fitness = ttk.Label(frame_metricas, text="Fitness Alcanzado: -")
        self.lbl_fitness.pack(anchor="w", padx=10, pady=2)

        self.lbl_evaluados = ttk.Label(frame_metricas, text="Estados Evaluados: -")
        self.lbl_evaluados.pack(anchor="w", padx=10, pady=2)

        self.lbl_generados = ttk.Label(frame_metricas, text="Estados Generados: -")
        self.lbl_generados.pack(anchor="w", padx=10, pady=2)

        self.lbl_tiempo = ttk.Label(frame_metricas, text="Tiempo de Ejecución: - ms")
        self.lbl_tiempo.pack(anchor="w", padx=10, pady=2)

        self.lbl_exito = ttk.Label(frame_metricas, text="100% Área Iluminada: -")
        self.lbl_exito.pack(anchor="w", padx=10, pady=2)

        frame_detalles = ttk.LabelFrame(frame_der, text="Detalle de Configuración de los 6 Focos")
        frame_detalles.pack(fill="both", expand=True, pady=5)

        self.txt_detalles = tk.Text(frame_detalles, height=6, bg="#313244", fg="#cdd6f4", font=("Consolas", 9), bd=0)
        self.txt_detalles.pack(fill="both", expand=True, padx=5, pady=5)

    def _crear_pestana_comparativa(self, parent):
        frame_top = ttk.Frame(parent)
        frame_top.pack(fill="x", padx=10, pady=10)

        self.btn_comparar = ttk.Button(frame_top, text="Ejecutar Comparativa Completa de Métricas", style="Primary.TButton", command=self._ejecutar_comparativa)
        self.btn_comparar.pack(side="left")

        lbl_info = ttk.Label(frame_top, text="Evalúa Ascenso de Colinas Estocástico y Algoritmo Genético en la misma configuración inicial")
        lbl_info.pack(side="left", padx=15)

        columnas = ("algoritmo", "cobertura", "costo", "fitness", "evaluados", "generados", "tiempo", "exito")
        self.tabla_comparativa = ttk.Treeview(parent, columns=columnas, show="headings", height=12)

        self.tabla_comparativa.heading("algoritmo", text="Algoritmo")
        self.tabla_comparativa.heading("cobertura", text="Cobertura (%)")
        self.tabla_comparativa.heading("costo", text="Consumo (W)")
        self.tabla_comparativa.heading("fitness", text="Fitness Final")
        self.tabla_comparativa.heading("evaluados", text="Estados Evaluados")
        self.tabla_comparativa.heading("generados", text="Estados Generados")
        self.tabla_comparativa.heading("tiempo", text="Tiempo (ms)")
        self.tabla_comparativa.heading("exito", text="100% Luz")

        self.tabla_comparativa.column("algoritmo", width=220, anchor="center")
        self.tabla_comparativa.column("cobertura", width=120, anchor="center")
        self.tabla_comparativa.column("costo", width=110, anchor="center")
        self.tabla_comparativa.column("fitness", width=120, anchor="center")
        self.tabla_comparativa.column("evaluados", width=140, anchor="center")
        self.tabla_comparativa.column("generados", width=140, anchor="center")
        self.tabla_comparativa.column("tiempo", width=120, anchor="center")
        self.tabla_comparativa.column("exito", width=100, anchor="center")

        self.tabla_comparativa.pack(fill="both", expand=True, padx=10, pady=10)

        lbl_explicacion = ttk.Label(
            parent,
            text="Nota Teórica: Ascenso de Colinas Estocástico evita estancamientos deterministas mediante ruleta delta. El Algoritmo Genético explora globalmente el espacio mediante cruzamiento de punto único y ruleta vectorizada de 100 slots.",
            font=("Segoe UI", 9, "italic"),
            foreground="#89b4fa"
        )
        lbl_explicacion.pack(pady=5)

    def _redibujar_plano(self, estado):
        self.canvas_plano.delete("all")
        cell_size = 65

        cob, watts, fit, mapa_celdas = AmbienteIluminacion.evaluar_estado(estado)

        for ix in range(AmbienteIluminacion.CELDAS_X):
            for iy in range(AmbienteIluminacion.CELDAS_Y):
                x1 = ix * cell_size
                y1 = iy * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                cant = mapa_celdas[ix][iy]
                if cant == 0:
                    color_fondo = "#181825"
                elif cant == 1:
                    color_fondo = "#2d4f3e"
                elif cant == 2:
                    color_fondo = "#3d6a52"
                else:
                    color_fondo = "#4f8767"

                self.canvas_plano.create_rectangle(x1, y1, x2, y2, fill=color_fondo, outline="#313244")

        colores_focos = {
            10: "#f9e2af",
            20: "#fab387",
            30: "#89b4fa",
            50: "#cba6f7"
        }

        for idx, (xf, yf, w, o) in enumerate(estado):
            rx, ry = AmbienteIluminacion.CATALOGO_VATIAJES[w]
            if o == 1:
                rx, ry = ry, rx

            cx_px = xf * cell_size
            cy_px = yf * cell_size

            rx_px = rx * cell_size
            ry_px = ry * cell_size

            ex1 = cx_px - rx_px
            ey1 = cy_px - ry_px
            ex2 = cx_px + rx_px
            ey2 = cy_px + ry_px

            color_foco = colores_focos.get(w, "#89b4fa")
            self.canvas_plano.create_oval(ex1, ey1, ex2, ey2, outline=color_foco, width=2, dash=(4, 2))

            r_foco = 10
            self.canvas_plano.create_oval(cx_px - r_foco, cy_px - r_foco, cx_px + r_foco, cy_px + r_foco, fill=color_foco, outline="#11111b", width=2)
            self.canvas_plano.create_text(cx_px, cy_px, text=f"F{idx+1}", fill="#11111b", font=("Segoe UI", 8, "bold"))

        self._actualizar_texto_detalles(estado, cob, watts, fit)

    def _actualizar_texto_detalles(self, estado, cob, watts, fit):
        self.txt_detalles.delete("1.0", tk.END)
        self.txt_detalles.insert(tk.END, f"Resumen: Cobertura={cob:.1f}% | Consumo={watts}W | Fitness={fit:.1f}\n")
        self.txt_detalles.insert(tk.END, "-" * 55 + "\n")
        for i, (x, y, w, o) in enumerate(estado):
            rx, ry = AmbienteIluminacion.CATALOGO_VATIAJES[w]
            orien_str = "Vertical" if o == 1 else "Horizontal"
            self.txt_detalles.insert(
                tk.END,
                f"Foco {i+1}: Pos=({x:.1f}m, {y:.1f}m) | Potencia={w}W | Cobertura=({rx}mx{ry}m) | Orien={orien_str}\n"
            )

    def _generar_aleatorio(self):
        self.animando = False
        self.btn_play.config(text="Reproducir")
        self.estado_actual = AmbienteIluminacion.generar_estado_aleatorio()
        self.historial_estados = [self.estado_actual]
        self.historial_fitness = []
        self.indice_animacion = 0
        self._redibujar_plano(self.estado_actual)
        self.lbl_paso_actual.config(text="Paso: 0 / 0")

    def _ejecutar_optimizacion(self):
        nombre_alg = self.combo_algoritmo.get()
        pob_val = int(self.spin_poblacion.get())
        mut_val = float(self.spin_mutacion.get()) / 100.0
        gen_val = int(self.spin_generaciones.get())

        self.btn_ejecutar.config(state="disabled", text="Calculando optimización...")
        self.btn_comparar.config(state="disabled")

        def _tarea():
            if nombre_alg == "Ascenso de Colinas Estocástico":
                res = busqueda_ascenso_colinas_estocastico(self.estado_actual, max_iteraciones=gen_val)
            else:
                res = ejecutar_algoritmo_genetico(
                    tamano_poblacion=pob_val,
                    num_generaciones=gen_val,
                    tasa_mutacion=mut_val,
                    estado_inicial=self.estado_actual
                )
            self.root.after(0, self._finalizar_optimizacion, res)

        threading.Thread(target=_tarea, daemon=True).start()

    def _finalizar_optimizacion(self, res):
        self.historial_estados = res.historial_estados
        self.historial_fitness = res.historial_fitness
        self.indice_animacion = len(self.historial_estados) - 1

        self.lbl_cobertura.config(text=f"Cobertura de Iluminación: {res.cobertura_porcentaje:.1f} %")
        self.lbl_costo.config(text=f"Consumo Total: {res.costo_watts} Watts")
        self.lbl_fitness.config(text=f"Fitness Alcanzado: {res.fitness_final:.2f}")
        self.lbl_evaluados.config(text=f"Estados Evaluados: {res.nodos_evaluados}")
        self.lbl_generados.config(text=f"Estados Generados: {res.nodos_generados}")
        self.lbl_tiempo.config(text=f"Tiempo de Ejecución: {res.tiempo_ejecucion_ms:.2f} ms")
        self.lbl_exito.config(text=f"100% Área Iluminada: {'SI' if res.exito else 'NO'}")
        self.lbl_paso_actual.config(text=f"Paso: {self.indice_animacion} / {len(self.historial_estados) - 1}")

        if self.historial_estados:
            self.estado_actual = self.historial_estados[-1]
            self._redibujar_plano(self.estado_actual)

        self.btn_ejecutar.config(state="normal", text="Ejecutar Optimización de Iluminación")
        self.btn_comparar.config(state="normal")

    def _paso_siguiente(self):
        if self.indice_animacion < len(self.historial_estados) - 1:
            self.indice_animacion += 1
            self.estado_actual = self.historial_estados[self.indice_animacion]
            self._redibujar_plano(self.estado_actual)
            self.lbl_paso_actual.config(text=f"Paso: {self.indice_animacion} / {len(self.historial_estados) - 1}")

    def _paso_anterior(self):
        if self.indice_animacion > 0:
            self.indice_animacion -= 1
            self.estado_actual = self.historial_estados[self.indice_animacion]
            self._redibujar_plano(self.estado_actual)
            self.lbl_paso_actual.config(text=f"Paso: {self.indice_animacion} / {len(self.historial_estados) - 1}")

    def _reiniciar_animacion(self):
        self.animando = False
        self.btn_play.config(text="Reproducir")
        self.indice_animacion = 0
        if self.historial_estados:
            self.estado_actual = self.historial_estados[0]
            self._redibujar_plano(self.estado_actual)
            self.lbl_paso_actual.config(text=f"Paso: 0 / {len(self.historial_estados) - 1}")

    def _toggle_animacion(self):
        if self.animando:
            self.animando = False
            self.btn_play.config(text="Reproducir")
        else:
            if len(self.historial_estados) <= 1:
                return
            self.animando = True
            self.btn_play.config(text="Pausar")
            self._bucle_animacion()

    def _bucle_animacion(self):
        if not self.animando:
            return
        if self.indice_animacion < len(self.historial_estados) - 1:
            self._paso_siguiente()
            self.root.after(150, self._bucle_animacion)
        else:
            self.animando = False
            self.btn_play.config(text="Reproducir")

    def _ejecutar_comparativa(self):
        for item in self.tabla_comparativa.get_children():
            self.tabla_comparativa.delete(item)

        pob_val = int(self.spin_poblacion.get())
        mut_val = float(self.spin_mutacion.get()) / 100.0
        gen_val = int(self.spin_generaciones.get())

        self.btn_comparar.config(state="disabled", text="Calculando comparativa...")
        self.btn_ejecutar.config(state="disabled")

        estado_inicio = self.estado_actual

        def _tarea():
            res_hc = busqueda_ascenso_colinas_estocastico(estado_inicio, max_iteraciones=gen_val)
            res_ga = ejecutar_algoritmo_genetico(
                tamano_poblacion=pob_val,
                num_generaciones=gen_val,
                tasa_mutacion=mut_val,
                estado_inicial=estado_inicio
            )
            resultados = [
                ("Ascenso de Colinas Estocástico", res_hc),
                ("Algoritmo Genético", res_ga)
            ]
            self.root.after(0, self._finalizar_comparativa, resultados)

        threading.Thread(target=_tarea, daemon=True).start()

    def _finalizar_comparativa(self, resultados):
        for nombre_alg, res in resultados:
            self.tabla_comparativa.insert(
                "",
                "end",
                values=(
                    nombre_alg,
                    f"{res.cobertura_porcentaje:.1f}",
                    res.costo_watts,
                    f"{res.fitness_final:.2f}",
                    res.nodos_evaluados,
                    res.nodos_generados,
                    f"{res.tiempo_ejecucion_ms:.2f}",
                    "SI" if res.exito else "NO"
                )
            )
        self.btn_comparar.config(state="normal", text="Ejecutar Comparativa Completa de Métricas")
        self.btn_ejecutar.config(state="normal")
