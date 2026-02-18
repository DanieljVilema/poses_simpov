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
    
    Args:
        kp: Keypoints del cuerpo (numpy array)
        conf: Confianza de los keypoints (numpy array)
    
    Returns:
        str: Orientación detectada ('PERFIL_DERECHO', 'PERFIL_IZQUIERDO', 'DESCONOCIDO')
    """
    dist_hombros_x = abs(kp[H_I][0] - kp[H_D][0])
    
    # Si el hombro derecho se ve mejor y la distancia X es corta (oclusión) = DERECHA
    if conf[H_D] > 0.5 and (conf[H_D] > conf[H_I] or dist_hombros_x <= 50):
        return "PERFIL_DERECHO"
    # Si el hombro izquierdo domina = IZQUIERDA
    elif conf[H_I] > 0.5 and (conf[H_I] > conf[H_D] or dist_hombros_x <= 50):
        return "PERFIL_IZQUIERDO"
    else:
        return "DESCONOCIDO"


def extraer_angulos(kp, orientacion):
    """
    Extrae los ángulos del cuerpo según la orientación actual.
    
    Args:
        kp: Keypoints del cuerpo (numpy array)
        orientacion: Orientación actual ('PERFIL_DERECHO' o 'PERFIL_IZQUIERDO')
    
    Returns:
        tuple: (brazo, torso, codo_hombro_cadera) - los tres ángulos principales
    """
    if orientacion == "PERFIL_DERECHO":
        brazo = calcular_angulo(kp[H_D], kp[C_D], kp[M_D])
        torso = calcular_angulo(kp[H_D], kp[CAD_D], kp[ROD_D])
        codo_hombro_cadera = calcular_angulo(kp[C_D], kp[H_D], kp[CAD_D])
    elif orientacion == "PERFIL_IZQUIERDO":
        brazo = calcular_angulo(kp[H_I], kp[C_I], kp[M_I])
        torso = calcular_angulo(kp[H_I], kp[CAD_I], kp[ROD_I])
        codo_hombro_cadera = calcular_angulo(kp[C_I], kp[H_I], kp[CAD_I])
    else:
        brazo = torso = codo_hombro_cadera = 0
    
    return brazo, torso, codo_hombro_cadera


def evaluar_postura(brazo, torso, codo_hombro_cadera, patron, tolerancia):
    """
    Evalúa si la postura actual coincide con el patrón calibrado.
    
    Args:
        brazo, torso, codo_hombro_cadera: Ángulos actuales
        patron: Diccionario con ángulos calibrados
        tolerancia: Grados de error permitidos
    
    Returns:
        tuple: (color_brazo, color_torso, color_codo_hombro_cadera) - colores BGR para visualización
               Verde (0,255,0) si está dentro de tolerancia, Rojo (0,0,255) si no
    """
    col_b = (0, 255, 0) if abs(brazo - patron["brazo"]) <= tolerancia else (0, 0, 255)
    col_t = (0, 255, 0) if abs(torso - patron["torso"]) <= tolerancia else (0, 0, 255)
    col_chc = (0, 255, 0) if abs(codo_hombro_cadera - patron["codo_hombro_cadera"]) <= tolerancia else (0, 0, 255)
    
    return col_b, col_t, col_chc
