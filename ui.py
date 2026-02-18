"""
Módulo de Interfaz de Usuario (UI)
Contiene todas las funciones de visualización y renderizado de la pantalla
"""
import cv2

# Índices COCO
H_I, H_D = 5, 6
C_I, C_D = 7, 8
M_I, M_D = 9, 10
CAD_I, CAD_D = 11, 12
ROD_I, ROD_D = 13, 14


def crear_ventana(nombre_ventana, callback):
    """
    Crea una ventana de OpenCV con un callback para eventos de mouse.
    
    Args:
        nombre_ventana: Nombre de la ventana
        callback: Función callback para eventos de mouse
    """
    cv2.namedWindow(nombre_ventana)
    cv2.setMouseCallback(nombre_ventana, callback)


def dibujar_hud(ui, orientacion_actual, patrones):
    """
    Dibuja el HUD superior con información del estado.
    
    Args:
        ui: Frame de OpenCV donde dibujar
        orientacion_actual: Orientación actual detectada
        patrones: Diccionario con patrones calibrados
    """
    cv2.rectangle(ui, (0, 0), (640, 80), (0, 0, 0), -1)  # Fondo negro HUD
    cv2.putText(ui, f"MODO: {orientacion_actual}", (230, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    if orientacion_actual != "DESCONOCIDO":
        estado_txt = "LISTO" if patrones.get(orientacion_actual, {}).get("calibrado") else "NO CALIBRADO"
        color_estado = (0, 255, 0) if estado_txt == "LISTO" else (0, 0, 255)
        cv2.putText(ui, f"MEMORIA: {estado_txt}", (230, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_estado, 2)


def dibujar_boton_nuevo_patron(ui, calibrado):
    """
    Dibuja el botón de "NUEVO PATRÓN" si no hay calibración.
    
    Args:
        ui: Frame de OpenCV donde dibujar
        calibrado: Boolean indicando si está calibrado
    """
    if not calibrado:
        cv2.rectangle(ui, (20, 20), (200, 70), (200, 0, 0), -1)
        cv2.putText(ui, "NUEVO PATRON", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


def dibujar_cuerpo_derecho(ui, kp, col_b, col_t, col_chc):
    """
    Dibuja las líneas del cuerpo para perfil derecho.
    
    Args:
        ui: Frame de OpenCV donde dibujar
        kp: Keypoints del cuerpo
        col_b: Color para el brazo
        col_t: Color para el torso
        col_chc: Color para codo-hombro-cadera
    """
    cv2.line(ui, tuple(kp[H_D][:2].astype(int)), tuple(kp[C_D][:2].astype(int)), col_b, 3)
    cv2.line(ui, tuple(kp[C_D][:2].astype(int)), tuple(kp[M_D][:2].astype(int)), col_chc, 3)
    cv2.line(ui, tuple(kp[H_D][:2].astype(int)), tuple(kp[CAD_D][:2].astype(int)), col_t, 3)
    cv2.line(ui, tuple(kp[CAD_D][:2].astype(int)), tuple(kp[ROD_D][:2].astype(int)), col_t, 3)
    cv2.line(ui, tuple(kp[C_D][:2].astype(int)), tuple(kp[H_D][:2].astype(int)), col_chc, 3)
    cv2.line(ui, tuple(kp[H_D][:2].astype(int)), tuple(kp[CAD_D][:2].astype(int)), col_chc, 3)


def dibujar_cuerpo_izquierdo(ui, kp, col_b, col_t, col_chc):
    """
    Dibuja las líneas del cuerpo para perfil izquierdo.
    
    Args:
        ui: Frame de OpenCV donde dibujar
        kp: Keypoints del cuerpo
        col_b: Color para el brazo
        col_t: Color para el torso
        col_chc: Color para codo-hombro-cadera
    """
    cv2.line(ui, tuple(kp[H_I][:2].astype(int)), tuple(kp[C_I][:2].astype(int)), col_b, 3)
    cv2.line(ui, tuple(kp[C_I][:2].astype(int)), tuple(kp[M_I][:2].astype(int)), col_chc, 3)
    cv2.line(ui, tuple(kp[H_I][:2].astype(int)), tuple(kp[CAD_I][:2].astype(int)), col_t, 3)
    cv2.line(ui, tuple(kp[CAD_I][:2].astype(int)), tuple(kp[ROD_I][:2].astype(int)), col_t, 3)
    cv2.line(ui, tuple(kp[C_I][:2].astype(int)), tuple(kp[H_I][:2].astype(int)), col_chc, 3)
    cv2.line(ui, tuple(kp[H_I][:2].astype(int)), tuple(kp[CAD_I][:2].astype(int)), col_chc, 3)


def mostrar_mensaje_calibracion(ui, orientacion, tiempo_restante):
    """
    Muestra el mensaje de calibración en progreso.
    
    Args:
        ui: Frame de OpenCV donde dibujar
        orientacion: Orientación actual
        tiempo_restante: Segundos restantes para calibrar
    """
    cv2.putText(ui, f"CALIBRANDO {orientacion}: {tiempo_restante}", (50, 250), 
                cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 165, 255), 3)


def mostrar_mensaje_prescalibracion(ui):
    """
    Muestra mensaje pidiendo calibración.
    
    Args:
        ui: Frame de OpenCV donde dibujar
    """
    cv2.putText(ui, "PRESIONA 'NUEVO PATRON' PARA DETECTAR LA POSTURA", (30, 400), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
