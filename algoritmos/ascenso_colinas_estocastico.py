import time
import random
from nucleo.ambiente import AmbienteIluminacion
from nucleo.metricas import MetricasIluminacion

def busqueda_ascenso_colinas_estocastico(estado_inicial, max_iteraciones=200, num_reinicios=5):
    inicio_tiempo = time.perf_counter()
    metricas = MetricasIluminacion()

    estado_actual = estado_inicial
    cob_actual, watts_actual, fit_actual, _ = AmbienteIluminacion.evaluar_estado(estado_actual)
    metricas.nodos_evaluados += 1
    metricas.nodos_generados += 1

    metricas.historial_fitness.append(fit_actual)
    metricas.historial_estados.append(estado_actual)
    metricas.mejor_estado = estado_actual
    metricas.cobertura_porcentaje = cob_actual
    metricas.costo_watts = watts_actual
    metricas.fitness_final = fit_actual
    if cob_actual >= 100.0:
        metricas.exito = True

    for r_idx in range(num_reinicios + 1):
        if r_idx > 0:
            estado_actual = AmbienteIluminacion.generar_estado_aleatorio()
            cob_actual, watts_actual, fit_actual, _ = AmbienteIluminacion.evaluar_estado(estado_actual)
            metricas.nodos_evaluados += 1
            metricas.nodos_generados += 1
            metricas.historial_fitness.append(fit_actual)
            metricas.historial_estados.append(estado_actual)

            if fit_actual > metricas.fitness_final:
                metricas.fitness_final = fit_actual
                metricas.mejor_estado = estado_actual
                metricas.cobertura_porcentaje = cob_actual
                metricas.costo_watts = watts_actual

            if cob_actual >= 100.0:
                metricas.exito = True

        for _ in range(max_iteraciones):
            sucesores = AmbienteIluminacion.obtener_sucesores(estado_actual)
            metricas.nodos_generados += len(sucesores)

            mejores = []
            for vec in sucesores:
                cob_v, watts_v, fit_v, _ = AmbienteIluminacion.evaluar_estado(vec)
                metricas.nodos_evaluados += 1
                delta = fit_v - fit_actual
                if delta > 0.0001:
                    mejores.append((vec, cob_v, watts_v, fit_v, delta))

            if len(mejores) == 0:
                break

            suma_deltas = sum(item[4] for item in mejores)

            r = random.uniform(0, suma_deltas)
            acumulado = 0.0
            elegido = mejores[0]
            for item in mejores:
                acumulado += item[4]
                if r <= acumulado:
                    elegido = item
                    break

            estado_actual = elegido[0]
            cob_actual = elegido[1]
            watts_actual = elegido[2]
            fit_actual = elegido[3]

            metricas.historial_fitness.append(fit_actual)
            metricas.historial_estados.append(estado_actual)

            if fit_actual > metricas.fitness_final:
                metricas.fitness_final = fit_actual
                metricas.mejor_estado = estado_actual
                metricas.cobertura_porcentaje = cob_actual
                metricas.costo_watts = watts_actual

            if cob_actual >= 100.0:
                metricas.exito = True

    fin_tiempo = time.perf_counter()
    metricas.tiempo_ejecucion_ms = (fin_tiempo - inicio_tiempo) * 1000.0
    return metricas
