import random

class AmbienteIluminacion:
    ANCHO = 7.0
    LARGO = 8.0
    CELDAS_X = 7
    CELDAS_Y = 8
    NUM_FOCOS = 6
    CATALOGO_VATIAJES = {
        10: (1.5, 1.0),
        20: (2.0, 1.5),
        30: (2.5, 1.8),
        50: (3.2, 2.2)
    }
    OPCIONES_VATIAJE = [10, 20, 30, 50]
    OPCIONES_X = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5]
    OPCIONES_Y = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]

    @staticmethod
    def generar_estado_aleatorio():
        focos = []
        for _ in range(AmbienteIluminacion.NUM_FOCOS):
            x = random.choice(AmbienteIluminacion.OPCIONES_X)
            y = random.choice(AmbienteIluminacion.OPCIONES_Y)
            w = random.choice(AmbienteIluminacion.OPCIONES_VATIAJE)
            o = random.choice([0, 1])
            focos.append((x, y, w, o))
        return tuple(focos)

    @staticmethod
    def evaluar_estado(estado):
        mapa_celdas = [[0 for _ in range(AmbienteIluminacion.CELDAS_Y)] for _ in range(AmbienteIluminacion.CELDAS_X)]
        celdas_iluminadas = 0
        costo_watts = 0
        for (x_f, y_f, w, o) in estado:
            costo_watts += w
            rx, ry = AmbienteIluminacion.CATALOGO_VATIAJES[w]
            if o == 1:
                rx, ry = ry, rx
            for ix in range(AmbienteIluminacion.CELDAS_X):
                cx = ix + 0.5
                dx = cx - x_f
                for iy in range(AmbienteIluminacion.CELDAS_Y):
                    cy = iy + 0.5
                    dy = cy - y_f
                    val = (dx * dx) / (rx * rx) + (dy * dy) / (ry * ry)
                    if val <= 1.0:
                        mapa_celdas[ix][iy] += 1

        for ix in range(AmbienteIluminacion.CELDAS_X):
            for iy in range(AmbienteIluminacion.CELDAS_Y):
                if mapa_celdas[ix][iy] > 0:
                    celdas_iluminadas += 1

        cobertura_porcentaje = (celdas_iluminadas / 56.0) * 100.0
        fitness_val = (cobertura_porcentaje * 10.0) - (0.5 * costo_watts)
        if cobertura_porcentaje < 100.0:
            fitness_val -= (100.0 - cobertura_porcentaje) * 20.0

        return cobertura_porcentaje, costo_watts, fitness_val, mapa_celdas

    @staticmethod
    def obtener_sucesores(estado):
        sucesores = []
        lista_estado = list(estado)
        for i in range(len(lista_estado)):
            x, y, w, o = lista_estado[i]
            
            for dx in [-1.0, 1.0]:
                nx = x + dx
                if 0.5 <= nx <= 6.5:
                    nuevo = list(lista_estado)
                    nuevo[i] = (nx, y, w, o)
                    sucesores.append(tuple(nuevo))

            for dy in [-1.0, 1.0]:
                ny = y + dy
                if 0.5 <= ny <= 7.5:
                    nuevo = list(lista_estado)
                    nuevo[i] = (x, ny, w, o)
                    sucesores.append(tuple(nuevo))

            for nw in AmbienteIluminacion.OPCIONES_VATIAJE:
                if nw != w:
                    nuevo = list(lista_estado)
                    nuevo[i] = (x, y, nw, o)
                    sucesores.append(tuple(nuevo))

            no = 1 if o == 0 else 0
            nuevo = list(lista_estado)
            nuevo[i] = (x, y, w, no)
            sucesores.append(tuple(nuevo))

        return sucesores
