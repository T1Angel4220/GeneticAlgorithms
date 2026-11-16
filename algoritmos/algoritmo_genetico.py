import time
import random
from nucleo.ambiente import AmbienteIluminacion
from nucleo.metricas import MetricasIluminacion

def ejecutar_algoritmo_genetico(tamano_poblacion=20, num_generaciones=100, tasa_mutacion=0.10, estado_inicial=None):
    inicio_tiempo = time.perf_counter()
    metricas = MetricasIluminacion()

    poblacion = []
    if estado_inicial is not None:
        poblacion.append(estado_inicial)

    while len(poblacion) < tamano_poblacion:
        indiv = AmbienteIluminacion.generar_estado_aleatorio()
        poblacion.append(indiv)
        metricas.nodos_generados += 1

    mejor_global_estado = None
    mejor_global_fit = -999999.0
    mejor_global_cob = 0.0
    mejor_global_watts = 0

    for gen in range(num_generaciones):
        evaluaciones = []
        fits = []
        for indiv in poblacion:
            cob, watts, fit, _ = AmbienteIluminacion.evaluar_estado(indiv)
            metricas.nodos_evaluados += 1
            evaluaciones.append((indiv, cob, watts, fit))
            fits.append(fit)

            if fit > mejor_global_fit:
                mejor_global_fit = fit
                mejor_global_estado = indiv
                mejor_global_cob = cob
                mejor_global_watts = watts

        metricas.historial_fitness.append(mejor_global_fit)
        metricas.historial_estados.append(mejor_global_estado)

        if mejor_global_cob >= 100.0:
            metricas.exito = True

        min_fit = min(fits)
        fits_ajustados = [f - min_fit + 1.0 for f in fits]

        nueva_poblacion = [mejor_global_estado]

        while len(nueva_poblacion) < tamano_poblacion:
            padre1, padre2 = random.choices(poblacion, weights=fits_ajustados, k=2)

            corte = random.randint(1, 5)
            hijo1 = list(padre1[:corte] + padre2[corte:])
            hijo2 = list(padre2[:corte] + padre1[corte:])

            if random.random() < tasa_mutacion:
                k = random.randint(0, 5)
                x = random.choice(AmbienteIluminacion.OPCIONES_X)
                y = random.choice(AmbienteIluminacion.OPCIONES_Y)
                w = random.choice(AmbienteIluminacion.OPCIONES_VATIAJE)
                o = random.choice([0, 1])
                hijo1[k] = (x, y, w, o)

            if random.random() < tasa_mutacion:
                k = random.randint(0, 5)
                x = random.choice(AmbienteIluminacion.OPCIONES_X)
                y = random.choice(AmbienteIluminacion.OPCIONES_Y)
                w = random.choice(AmbienteIluminacion.OPCIONES_VATIAJE)
                o = random.choice([0, 1])
                hijo2[k] = (x, y, w, o)

            nueva_poblacion.append(tuple(hijo1))
            metricas.nodos_generados += 1
            if len(nueva_poblacion) < tamano_poblacion:
                nueva_poblacion.append(tuple(hijo2))
                metricas.nodos_generados += 1

        poblacion = nueva_poblacion

    fin_tiempo = time.perf_counter()
    metricas.tiempo_ejecucion_ms = (fin_tiempo - inicio_tiempo) * 1000.0
    metricas.mejor_estado = mejor_global_estado
    metricas.fitness_final = mejor_global_fit
    metricas.cobertura_porcentaje = mejor_global_cob
    metricas.costo_watts = mejor_global_watts

    return metricas
