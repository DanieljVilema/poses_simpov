"""
Módulo de Interfaz de Usuario (UI)
Contiene todas las funciones de visualización y renderizado de la pantalla
"""
import cv2
import numpy as np

# Índices COCO
NARIZ = 0
H_I, H_D = 5, 6
C_I, C_D = 7, 8
M_I, M_D = 9, 10
CAD_I, CAD_D = 11, 12
ROD_I, ROD_D = 13, 14
TOB_I, TOB_D = 15, 16


def crear_ventana(nombre_ventana, callback):
    cv2.namedWindow(nombre_ventana)
    cv2.setMouseCallback(nombre_ventana, callback)


def mostrar_menu_armas(nombre_ventana, lista_armas):
    seleccion = [None]
    input_texto = [""]
    modo_input = [False]
    scroll_offset = [0]
    max_visibles = 5

    def click_menu(evento, x, y, flags, param):
        if evento != cv2.EVENT_LBUTTONDOWN: return
        if 170 <= x <= 470 and 80 <= y <= 130:
            modo_input[0] = True; input_texto[0] = ""
            return
        if modo_input[0]:
            if 170 <= x <= 470 and 160 <= y <= 200:
                if input_texto[0].strip(): seleccion[0] = input_texto[0].strip()
            elif 170 <= x <= 470 and 210 <= y <= 250:
                modo_input[0] = False; input_texto[0] = ""
            return
        if lista_armas and len(lista_armas) > max_visibles:
            if 480 <= x <= 520 and 155 <= y <= 185:
                scroll_offset[0] = max(0, scroll_offset[0] - 1); return
            if 480 <= x <= 520 and 155 + max_visibles * 50 - 30 <= y <= 155 + max_visibles * 50:
                scroll_offset[0] = min(len(lista_armas) - max_visibles, scroll_offset[0] + 1); return
        if lista_armas:
            inicio_y = 155
            visible = lista_armas[scroll_offset[0]:scroll_offset[0] + max_visibles]
            for i, arma in enumerate(visible):
                y_top = inicio_y + i * 50
                y_bot = y_top + 40
                if 170 <= x <= 470 and y_top <= y <= y_bot:
                    seleccion[0] = arma; return

    cv2.setMouseCallback(nombre_ventana, click_menu)

    while seleccion[0] is None:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, "SELECCIONAR ARMA", (170, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        cv2.line(frame, (170, 50), (470, 50), (0, 255, 255), 2)

        if modo_input[0]:
            cv2.putText(frame, "NOMBRE DEL ARMA:", (170, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            cv2.rectangle(frame, (170, 120), (470, 150), (255, 255, 255), 1)
            cv2.putText(frame, input_texto[0] + "|", (180, 143), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.rectangle(frame, (170, 160), (470, 200), (0, 130, 0), -1)
            cv2.putText(frame, "CONFIRMAR", (260, 187), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.rectangle(frame, (170, 210), (470, 250), (0, 0, 130), -1)
            cv2.putText(frame, "CANCELAR", (265, 237), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            cv2.rectangle(frame, (170, 80), (470, 130), (180, 100, 0), -1)
            cv2.putText(frame, "+ NUEVA ARMA", (230, 113), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            if lista_armas:
                cv2.putText(frame, "ARMAS GUARDADAS:", (170, 148), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
                inicio_y = 155
                visible = lista_armas[scroll_offset[0]:scroll_offset[0] + max_visibles]
                for i, arma in enumerate(visible):
                    y_top = inicio_y + i * 50
                    cv2.rectangle(frame, (170, y_top), (470, y_top + 40), (80, 80, 80), -1)
                    cv2.rectangle(frame, (170, y_top), (470, y_top + 40), (0, 200, 200), 1)
                    cv2.putText(frame, arma.upper(), (185, y_top + 27), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
                if len(lista_armas) > max_visibles:
                    if scroll_offset[0] > 0:
                        cv2.putText(frame, "^", (490, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 200), 2)
                    if scroll_offset[0] < len(lista_armas) - max_visibles:
                        cv2.putText(frame, "v", (490, 155 + max_visibles * 50 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 200), 2)
            else:
                cv2.putText(frame, "No hay armas guardadas.", (175, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 100, 100), 1)
                cv2.putText(frame, "Crea una nueva arma para comenzar.", (145, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 100, 100), 1)

        cv2.putText(frame, "Presiona 'Q' para salir", (210, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
        cv2.imshow(nombre_ventana, frame)
        tecla = cv2.waitKey(30) & 0xFF

        if tecla == ord('q'): return None
        if modo_input[0]:
            if tecla == 13:
                if input_texto[0].strip(): seleccion[0] = input_texto[0].strip()
            elif tecla == 27:
                modo_input[0] = False; input_texto[0] = ""
            elif tecla == 8: input_texto[0] = input_texto[0][:-1]
            elif 32 <= tecla <= 126 and len(input_texto[0]) < 20:
                input_texto[0] += chr(tecla)
    return seleccion[0]

def dibujar_hud(ui, orientacion_actual, patrones, arma_actual=None):
    cv2.rectangle(ui, (0, 0), (640, 80), (0, 0, 0), -1)
    if arma_actual:
        cv2.putText(ui, f"ARMA: {arma_actual.upper()}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 200), 2)
    cv2.putText(ui, f"MODO: {orientacion_actual}", (230, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    if orientacion_actual != "DESCONOCIDO":
        estado_txt = "LISTO" if patrones.get(orientacion_actual, {}).get("calibrado") else "NO CALIBRADO"
        color_estado = (0, 255, 0) if estado_txt == "LISTO" else (0, 0, 255)
        cv2.putText(ui, f"MEMORIA: {estado_txt}", (230, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_estado, 2)

def dibujar_boton_nuevo_patron(ui, calibrado):
    txt_boton = "RECALIBRAR" if calibrado else "NUEVO PATRON"
    color_boton = (0, 130, 130) if calibrado else (200, 0, 0)
    cv2.rectangle(ui, (20, 20), (200, 70), color_boton, -1)
    cv2.putText(ui, txt_boton, (30 if not calibrado else 40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

def mostrar_mensaje_calibracion(ui, orientacion, tiempo_restante, num_muestras):
    cv2.putText(ui, f"CALIBRANDO {orientacion}: {tiempo_restante}s", (50, 250), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 165, 255), 3)
    cv2.putText(ui, f"Muestras capturadas: {num_muestras}", (50, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

def mostrar_mensaje_prescalibracion(ui):
    cv2.putText(ui, "PRESIONA 'NUEVO PATRON' PARA ENSEÑAR LA POSTURA", (30, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

def dibujar_score(ui, score):
    color = (0, 255, 0) if score >= 80 else (0, 255, 255) if score >= 50 else (0, 0, 255)
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

    # Brazo dominante
    col = colores.get("col_brazo", (200, 200, 200))
    linea(dom_h, dom_c, col); linea(dom_c, dom_m, col)
    # Tronco
    linea(dom_h, dom_cad, colores.get("col_codo_hombro_cadera", (200, 200, 200)))
    # Pierna Superior e Inferior
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