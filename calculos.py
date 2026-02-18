"""
Módulo de Operaciones Matemáticas y Cálculos
Contiene todas las funciones de cálculo de ángulos y detección de orientación
"""
import math
import numpy as np
from collections import deque

# Índices COCO
NARIZ = 0
H_I, H_D = 5, 6
C_I, C_D = 7, 8
M_I, M_D = 9, 10
CAD_I, CAD_D = 11, 12
ROD_I, ROD_D = 13, 14
TOB_I, TOB_D = 15, 16

class SuavizadorTemporal:
    """Suaviza keypoints usando promedio de ventana deslizante para eliminar jitter"""
    def __init__(self, ventana=5):
        self.buffer_kp = deque(maxlen=ventana)
        self.buffer_conf = deque(maxlen=ventana)

    def actualizar(self, kp, conf):
        self.buffer_kp.append(kp.copy())
        self.buffer_conf.append(conf.copy())

    def obtener_suavizado(self):
        if not self.buffer_kp:
            return None, None
        return np.mean(self.buffer_kp, axis=0), np.mean(self.buffer_conf, axis=0)

    def limpiar(self):
        self.buffer_kp.clear()
        self.buffer_conf.clear()

def calcular_angulo(p1, p2, p3):
    rad = math.atan2(p3[1] - p2[1], p3[0] - p2[0]) - math.atan2(p1[1] - p2[1], p1[0] - p2[0])
    ang = abs(rad * 180.0 / math.pi)
    return int(360.0 - ang if ang > 180.0 else ang)

def detectar_orientacion(kp, conf):
    if conf[H_I] < 0.3 and conf[H_D] < 0.3:
        return "DESCONOCIDO"

    dist_hombros_x = abs(kp[H_I][0] - kp[H_D][0])
    dist_caderas_x = abs(kp[CAD_I][0] - kp[CAD_D][0])

    if dist_hombros_x > 100 and dist_caderas_x > 80:
        return "DESCONOCIDO"

    votos_derecho = 0
    votos_izquierdo = 0

    if conf[H_D] > conf[H_I] + 0.1: votos_derecho += 2
    elif conf[H_I] > conf[H_D] + 0.1: votos_izquierdo += 2

    if conf[C_D] > conf[C_I] + 0.1: votos_derecho += 1
    elif conf[C_I] > conf[C_D] + 0.1: votos_izquierdo += 1

    if conf[CAD_D] > conf[CAD_I] + 0.1: votos_derecho += 1
    elif conf[CAD_I] > conf[CAD_D] + 0.1: votos_izquierdo += 1

    if dist_hombros_x <= 80 and conf[H_D] > 0.4 and conf[H_I] > 0.4:
        if kp[H_D][0] > kp[H_I][0]: votos_derecho += 1
        else: votos_izquierdo += 1

    if votos_derecho > votos_izquierdo and votos_derecho >= 2:
        return "PERFIL_DERECHO"
    elif votos_izquierdo > votos_derecho and votos_izquierdo >= 2:
        return "PERFIL_IZQUIERDO"
    else:
        if dist_hombros_x <= 60:
            if conf[H_D] >= conf[H_I]: return "PERFIL_DERECHO"
            else: return "PERFIL_IZQUIERDO"
        return "DESCONOCIDO"

def _keypoints_confiables(conf, indices, umbral=0.3):
    return all(conf[i] >= umbral for i in indices)

def extraer_angulos(kp, orientacion, conf=None):
    resultado = {
        "brazo": 0, "torso": 0, "codo_hombro_cadera": 0,
        "brazo_soporte": None, "rodilla": None, "cabeza": None
    }

    if orientacion == "PERFIL_DERECHO":
        dom_h, dom_c, dom_m = H_D, C_D, M_D
        dom_cad, dom_rod, dom_tob = CAD_D, ROD_D, TOB_D
        sop_h, sop_c, sop_m = H_I, C_I, M_I
    elif orientacion == "PERFIL_IZQUIERDO":
        dom_h, dom_c, dom_m = H_I, C_I, M_I
        dom_cad, dom_rod, dom_tob = CAD_I, ROD_I, TOB_I
        sop_h, sop_c, sop_m = H_D, C_D, M_D
    else:
        return resultado

    resultado["brazo"] = calcular_angulo(kp[dom_h], kp[dom_c], kp[dom_m])
    resultado["torso"] = calcular_angulo(kp[dom_h], kp[dom_cad], kp[dom_rod])
    resultado["codo_hombro_cadera"] = calcular_angulo(kp[dom_c], kp[dom_h], kp[dom_cad])

    if conf is not None and _keypoints_confiables(conf, [sop_h, sop_c, sop_m], umbral=0.15):
        resultado["brazo_soporte"] = calcular_angulo(kp[sop_h], kp[sop_c], kp[sop_m])
        
    if conf is not None and _keypoints_confiables(conf, [dom_cad, dom_rod, dom_tob]):
        resultado["rodilla"] = calcular_angulo(kp[dom_cad], kp[dom_rod], kp[dom_tob])
        
    if conf is not None and _keypoints_confiables(conf, [NARIZ, dom_h, dom_cad]):
        resultado["cabeza"] = calcular_angulo(kp[NARIZ], kp[dom_h], kp[dom_cad])

    return resultado

def _tolerancia_adaptativa(std, minimo=8):
    if std is None or std <= 0: return minimo
    return max(std * 2.5, minimo)

PESOS_ANGULOS = {"brazo": 3, "torso": 2, "codo_hombro_cadera": 2, "brazo_soporte": 1.5, "rodilla": 1, "cabeza": 1.5}
ANGULOS_PRINCIPALES = ["brazo", "torso", "codo_hombro_cadera"]
ANGULOS_OPCIONALES = ["brazo_soporte", "rodilla", "cabeza"]

def evaluar_postura(angulos, patron):
    colores = {}
    scores = []

    for key in ANGULOS_PRINCIPALES:
        tol = _tolerancia_adaptativa(patron.get(f"{key}_std"))
        diff = abs(angulos[key] - patron[key])
        colores[f"col_{key}"] = (0, 255, 0) if diff <= tol else (0, 0, 255)
        scores.append((max(0.0, 1.0 - diff / (tol * 2)), PESOS_ANGULOS[key]))

    for key in ANGULOS_OPCIONALES:
        if angulos.get(key) is not None and patron.get(key) is not None:
            tol = _tolerancia_adaptativa(patron.get(f"{key}_std"))
            diff = abs(angulos[key] - patron[key])
            colores[f"col_{key}"] = (0, 255, 0) if diff <= tol else (0, 0, 255)
            scores.append((max(0.0, 1.0 - diff / (tol * 2)), PESOS_ANGULOS[key]))
        elif angulos.get(key) is not None:
            colores[f"col_{key}"] = (0, 255, 255)  # Amarillo (visible pero sin calibrar)

    total_peso = sum(p for _, p in scores) if scores else 1
    colores["score"] = int(sum(s * p for s, p in scores) / total_peso * 100) if scores else 0

    return colores