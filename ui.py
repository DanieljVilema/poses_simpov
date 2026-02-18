"""
Módulo de Interfaz de Usuario (UI)
Se encarga de dibujar el HUD, botones, mensajes y el esqueleto evaluado.
"""
import cv2

# Índices para dibujar
NARIZ = 0
H_I, H_D = 5, 6
C_I, C_D = 7, 8
M_I, M_D = 9, 10
CAD_I, CAD_D = 11, 12
ROD_I, ROD_D = 13, 14
TOB_I, TOB_D = 15, 16

def dibujar_hud(ui, orientacion, patrones, arma_actual):
    cv2.rectangle(ui, (0, 0), (640, 80), (0, 0, 0), -1)
    
    texto_arma = f"ARMA: {arma_actual}" if arma_actual else "MODO LIBRE"
    cv2.putText(ui, texto_arma, (230, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
    cv2.putText(ui, f"VISTA: {orientacion}", (230, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    if orientacion != "DESCONOCIDO":
        estado_txt = "LISTO (MEMORIA)" if patrones.get(orientacion, {}).get("calibrado") else "NO CALIBRADO"
        color_estado = (0, 255, 0) if "LISTO" in estado_txt else (0, 0, 255)
        cv2.putText(ui, f"ESTADO: {estado_txt}", (230, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_estado, 2)

def dibujar_boton_nuevo_patron(ui, esta_calibrado):
    txt_boton = "RECALIBRAR" if esta_calibrado else "NUEVO PATRON"
    color_boton = (0, 100, 200) if esta_calibrado else (200, 0, 0)
    cv2.rectangle(ui, (20, 20), (200, 70), color_boton, -1)
    cv2.putText(ui, txt_boton, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

def mostrar_mensaje_calibracion(ui, orientacion, restante, num_muestras):
    cv2.putText(ui, f"CALIBRANDO {orientacion}: {restante}s", (50, 250), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 165, 255), 3)
    cv2.putText(ui, f"Muestras capturadas: {num_muestras}", (50, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(ui, "Mantenga postura estatica...", (50, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

def mostrar_mensaje_prescalibracion(ui):
    cv2.putText(ui, "PRESIONE EL BOTON PARA ENSEÑAR LA POSTURA", (30, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

def dibujar_score(ui, score):
    if score >= 80: color = (0, 255, 0)
    elif score >= 50: color = (0, 255, 255)
    else: color = (0, 0, 255)
    cv2.putText(ui, f"PRECISION: {score}%", (400, 450), cv2.FONT_HERSHEY_DUPLEX, 0.8, color, 2)

def dibujar_cuerpo(ui, kp, orientacion, colores):
    if orientacion == "PERFIL_DERECHO":
        dom_h, dom_c, dom_m, dom_cad, dom_rod, dom_tob = H_D, C_D, M_D, CAD_D, ROD_D, TOB_D
        sop_h, sop_c, sop_m = H_I, C_I, M_I
    else:
        dom_h, dom_c, dom_m, dom_cad, dom_rod, dom_tob = H_I, C_I, M_I, CAD_I, ROD_I, TOB_I
        sop_h, sop_c, sop_m = H_D, C_D, M_D

    def linea(p1, p2, color, grosor=3):
        cv2.line(ui, tuple(kp[p1][:2].astype(int)), tuple(kp[p2][:2].astype(int)), color, grosor)

    # Brazo
    col = colores.get("col_brazo", (200, 200, 200))
    linea(dom_h, dom_c, col); linea(dom_c, dom_m, col)
    # Tronco
    linea(dom_h, dom_cad, colores.get("col_codo_hombro_cadera", (200, 200, 200)))
    # Pierna
    linea(dom_cad, dom_rod, colores.get("col_torso", (200, 200, 200)))
    if colores.get("col_rodilla") is not None:
        linea(dom_rod, dom_tob, colores["col_rodilla"])
    # Cabeza
    if colores.get("col_cabeza") is not None:
        linea(NARIZ, dom_h, colores["col_cabeza"], 2)
    # Brazo Soporte
    if colores.get("col_brazo_soporte") is not None:
        col = colores["col_brazo_soporte"]
        linea(sop_h, sop_c, col, 2); linea(sop_c, sop_m, col, 2)