class MetricasIluminacion:
    def __init__(self):
        self.nodos_evaluados = 0
        self.nodos_generados = 0
        self.tiempo_ejecucion_ms = 0.0
        self.cobertura_porcentaje = 0.0
        self.costo_watts = 0
        self.fitness_final = 0.0
        self.exito = False
        self.historial_estados = []
        self.historial_fitness = []
        self.mejor_estado = None
