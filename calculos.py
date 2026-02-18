"""
Módulo de Operaciones Matemáticas y Cálculos
Contiene todas las funciones de cálculo de ángulos y detección de orientación
"""
import math
import numpy as np

# Índices COCO
H_I, H_D = 5, 6
C_I, C_D = 7, 8
M_I, M_D = 9, 10
CAD_I, CAD_D = 11, 12
ROD_I, ROD_D = 13, 14


def calcular_angulo(p1, p2, p3):
    """
    Calcula el ángulo entre tres puntos.
    
    Args:
        p1, p2, p3: Coordenadas de los puntos (numpy array o tuple)
    
    Returns:
        int: Ángulo en grados (0-360)
    """
    rad = math.atan2(p3[1] - p2[1], p3[0] - p2[0]) - math.atan2(p1[1] - p2[1], p1[0] - p2[0])
    ang = abs(rad * 180.0 / math.pi)
    return int(360.0 - ang if ang > 180.0 else ang)


def detectar_orientacion(kp, conf):
    """
    Detecta automáticamente la orientación del cuerpo (PERFIL_DERECHO, PERFIL_IZQUIERDO o DESCONOCIDO).

    Usa múltiples señales: separación de hombros, posición relativa de hombros y caderas,
    y confianza de keypoints para una detección robusta de perfiles.

    Args:
        kp: Keypoints del cuerpo (numpy array)
        conf: Confianza de los keypoints (numpy array)

    Returns:
        str: Orientación detectada ('PERFIL_DERECHO', 'PERFIL_IZQUIERDO', 'DESCONOCIDO')
    """
    # Verificar que hay suficientes keypoints visibles
    if conf[H_I] < 0.3 and conf[H_D] < 0.3:
        return "DESCONOCIDO"

    dist_hombros_x = abs(kp[H_I][0] - kp[H_D][0])
    dist_caderas_x = abs(kp[CAD_I][0] - kp[CAD_D][0])

    # Si hombros y caderas están muy separados, es vista frontal, no perfil
    if dist_hombros_x > 100 and dist_caderas_x > 80:
        return "DESCONOCIDO"

    # Sistema de votación para determinar orientación
    votos_derecho = 0
    votos_izquierdo = 0

    # Señal 1: ¿Qué hombro tiene mayor confianza? (el visible es el que da nombre al perfil)
    if conf[H_D] > conf[H_I] + 0.1:
        votos_derecho += 2
    elif conf[H_I] > conf[H_D] + 0.1:
        votos_izquierdo += 2

    # Señal 2: ¿Qué codo tiene mayor confianza?
    if conf[C_D] > conf[C_I] + 0.1:
        votos_derecho += 1
    elif conf[C_I] > conf[C_D] + 0.1:
        votos_izquierdo += 1

    # Señal 3: ¿Qué cadera tiene mayor confianza?
    if conf[CAD_D] > conf[CAD_I] + 0.1:
        votos_derecho += 1
    elif conf[CAD_I] > conf[CAD_D] + 0.1:
        votos_izquierdo += 1

    # Señal 4: Posición relativa en X (en perfil derecho, el hombro derecho está más al frente)
    if dist_hombros_x <= 80 and conf[H_D] > 0.4 and conf[H_I] > 0.4:
        if kp[H_D][0] > kp[H_I][0]:
            votos_derecho += 1
        else:
            votos_izquierdo += 1

    # Decisión final
    if votos_derecho > votos_izquierdo and votos_derecho >= 2:
        return "PERFIL_DERECHO"
    elif votos_izquierdo > votos_derecho and votos_izquierdo >= 2:
        return "PERFIL_IZQUIERDO"
    else:
        # Fallback: si los hombros están juntos, usar la confianza como desempate
        if dist_hombros_x <= 60:
            if conf[H_D] >= conf[H_I]:
                return "PERFIL_DERECHO"
            else:
                return "PERFIL_IZQUIERDO"
        return "DESCONOCIDO"


def _keypoints_confiables(conf, indices, umbral=0.3):
    """
    Verifica si todos los keypoints de una lista tienen confianza suficiente.

    Args:
        conf: Array de confianzas
        indices: Lista de índices a verificar
        umbral: Confianza mínima requerida

    Returns:
        bool: True si todos superan el umbral
    """
    return all(conf[i] >= umbral for i in indices)


def extraer_angulos(kp, orientacion, conf=None):
    """
    Extrae los ángulos del cuerpo según la orientación actual.
    Calcula ángulos del brazo dominante y del brazo de soporte si es visible.

    Args:
        kp: Keypoints del cuerpo (numpy array)
        orientacion: Orientación actual ('PERFIL_DERECHO' o 'PERFIL_IZQUIERDO')
        conf: Confianza de los keypoints (numpy array, opcional)

    Returns:
        dict: Diccionario con ángulos extraídos:
            - brazo, torso, codo_hombro_cadera: ángulos del lado dominante
            - brazo_soporte: ángulo del brazo del lado opuesto (None si no es visible)
    """
    resultado = {
        "brazo": 0, "torso": 0, "codo_hombro_cadera": 0,
        "brazo_soporte": None
    }

    if orientacion == "PERFIL_DERECHO":
        dom_h, dom_c, dom_m = H_D, C_D, M_D
        dom_cad, dom_rod = CAD_D, ROD_D
        sop_h, sop_c, sop_m = H_I, C_I, M_I
    elif orientacion == "PERFIL_IZQUIERDO":
        dom_h, dom_c, dom_m = H_I, C_I, M_I
        dom_cad, dom_rod = CAD_I, ROD_I
        sop_h, sop_c, sop_m = H_D, C_D, M_D
    else:
        return resultado

    # Ángulos del lado dominante (siempre se calculan)
    resultado["brazo"] = calcular_angulo(kp[dom_h], kp[dom_c], kp[dom_m])
    resultado["torso"] = calcular_angulo(kp[dom_h], kp[dom_cad], kp[dom_rod])
    resultado["codo_hombro_cadera"] = calcular_angulo(kp[dom_c], kp[dom_h], kp[dom_cad])

    # Brazo de soporte (umbral más bajo porque está parcialmente ocluido en perfil)
    if conf is not None and _keypoints_confiables(conf, [sop_h, sop_c, sop_m], umbral=0.15):
        resultado["brazo_soporte"] = calcular_angulo(kp[sop_h], kp[sop_c], kp[sop_m])

    return resultado


def evaluar_postura(angulos, patron, tolerancia):
    """
    Evalúa si la postura actual coincide con el patrón calibrado.

    Args:
        angulos: Diccionario con ángulos actuales (de extraer_angulos)
        patron: Diccionario con ángulos calibrados
        tolerancia: Grados de error permitidos

    Returns:
        dict: Colores BGR para cada ángulo evaluado.
              Verde (0,255,0) si está dentro de tolerancia, Rojo (0,0,255) si no.
              Incluye 'col_brazo_soporte' si hay brazo de soporte calibrado.
    """
    col_b = (0, 255, 0) if abs(angulos["brazo"] - patron["brazo"]) <= tolerancia else (0, 0, 255)
    col_t = (0, 255, 0) if abs(angulos["torso"] - patron["torso"]) <= tolerancia else (0, 0, 255)
    col_chc = (0, 255, 0) if abs(angulos["codo_hombro_cadera"] - patron["codo_hombro_cadera"]) <= tolerancia else (0, 0, 255)

    resultado = {"col_b": col_b, "col_t": col_t, "col_chc": col_chc, "col_bs": None}

    # Evaluar brazo de soporte
    if angulos.get("brazo_soporte") is not None:
        if patron.get("brazo_soporte") is not None:
            # Tiene calibración: evaluar verde/rojo
            resultado["col_bs"] = (0, 255, 0) if abs(angulos["brazo_soporte"] - patron["brazo_soporte"]) <= tolerancia else (0, 0, 255)
        else:
            # Visible pero sin calibración: mostrar en amarillo (neutro)
            resultado["col_bs"] = (0, 255, 255)

    return resultado
