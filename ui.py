"""
Módulo de Interfaz de Usuario (UI)
Contiene todas las funciones de visualización y renderizado de la pantalla
"""
import cv2
import numpy as np

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


def mostrar_menu_armas(nombre_ventana, lista_armas):
    """
    Muestra un menú visual para seleccionar o crear arma.

    Args:
        nombre_ventana: Nombre de la ventana de OpenCV
        lista_armas: Lista de nombres de armas existentes

    Returns:
        str: Nombre del arma seleccionada o nueva
    """
    seleccion = [None]
    input_texto = [""]
    modo_input = [False]
    scroll_offset = [0]

    # Área visible para armas (máximo 5 visibles a la vez)
    max_visibles = 5

    def click_menu(evento, x, y, flags, param):
        if evento != cv2.EVENT_LBUTTONDOWN:
            return

        # Botón "NUEVA ARMA"
        if 170 <= x <= 470 and 80 <= y <= 130:
            modo_input[0] = True
            input_texto[0] = ""
            return

        # Si está en modo input
        if modo_input[0]:
            # Botón CONFIRMAR
            if 170 <= x <= 470 and 160 <= y <= 200:
                if input_texto[0].strip():
                    seleccion[0] = input_texto[0].strip()
            # Botón CANCELAR
            elif 170 <= x <= 470 and 210 <= y <= 250:
                modo_input[0] = False
                input_texto[0] = ""
            return

        # Flechas de scroll
        if lista_armas and len(lista_armas) > max_visibles:
            # Flecha arriba
            if 480 <= x <= 520 and 155 <= y <= 185:
                scroll_offset[0] = max(0, scroll_offset[0] - 1)
                return
            # Flecha abajo
            if 480 <= x <= 520 and 155 + max_visibles * 50 - 30 <= y <= 155 + max_visibles * 50:
                scroll_offset[0] = min(len(lista_armas) - max_visibles, scroll_offset[0] + 1)
                return

        # Clic en armas listadas
        if lista_armas:
            inicio_y = 155
            visible = lista_armas[scroll_offset[0]:scroll_offset[0] + max_visibles]
            for i, arma in enumerate(visible):
                y_top = inicio_y + i * 50
                y_bot = y_top + 40
                if 170 <= x <= 470 and y_top <= y <= y_bot:
                    seleccion[0] = arma
                    return

    cv2.setMouseCallback(nombre_ventana, click_menu)

    while seleccion[0] is None:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Título
        cv2.putText(frame, "SELECCIONAR ARMA", (170, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        cv2.line(frame, (170, 50), (470, 50), (0, 255, 255), 2)

        if modo_input[0]:
            # Modo ingreso de nombre
            cv2.putText(frame, "NOMBRE DEL ARMA:", (170, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            # Campo de texto
            cv2.rectangle(frame, (170, 120), (470, 150), (255, 255, 255), 1)
            cv2.putText(frame, input_texto[0] + "|", (180, 143),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            # Botón confirmar
            cv2.rectangle(frame, (170, 160), (470, 200), (0, 130, 0), -1)
            cv2.putText(frame, "CONFIRMAR", (260, 187),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            # Botón cancelar
            cv2.rectangle(frame, (170, 210), (470, 250), (0, 0, 130), -1)
            cv2.putText(frame, "CANCELAR", (265, 237),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            # Botón nueva arma
            cv2.rectangle(frame, (170, 80), (470, 130), (180, 100, 0), -1)
            cv2.putText(frame, "+ NUEVA ARMA", (230, 113),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            # Lista de armas existentes
            if lista_armas:
                cv2.putText(frame, "ARMAS GUARDADAS:", (170, 148),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
                inicio_y = 155
                visible = lista_armas[scroll_offset[0]:scroll_offset[0] + max_visibles]
                for i, arma in enumerate(visible):
                    y_top = inicio_y + i * 50
                    cv2.rectangle(frame, (170, y_top), (470, y_top + 40), (80, 80, 80), -1)
                    cv2.rectangle(frame, (170, y_top), (470, y_top + 40), (0, 200, 200), 1)
                    cv2.putText(frame, arma.upper(), (185, y_top + 27),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

                # Flechas de scroll si hay más armas
                if len(lista_armas) > max_visibles:
                    if scroll_offset[0] > 0:
                        cv2.putText(frame, "^", (490, 180),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 200), 2)
                    if scroll_offset[0] < len(lista_armas) - max_visibles:
                        y_flecha = 155 + max_visibles * 50 - 10
                        cv2.putText(frame, "v", (490, y_flecha),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 200), 2)
            else:
                cv2.putText(frame, "No hay armas guardadas.", (175, 180),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 100, 100), 1)
                cv2.putText(frame, "Crea una nueva arma para comenzar.", (145, 210),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 100, 100), 1)

        # Instrucción inferior
        cv2.putText(frame, "Presiona 'Q' para salir", (210, 460),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

        cv2.imshow(nombre_ventana, frame)
        tecla = cv2.waitKey(30) & 0xFF

        if tecla == ord('q'):
            return None

        # Manejo de teclado en modo input
        if modo_input[0]:
            if tecla == 13:  # Enter
                if input_texto[0].strip():
                    seleccion[0] = input_texto[0].strip()
            elif tecla == 27:  # Escape
                modo_input[0] = False
                input_texto[0] = ""
            elif tecla == 8:  # Backspace
                input_texto[0] = input_texto[0][:-1]
            elif 32 <= tecla <= 126:  # Caracteres imprimibles
                if len(input_texto[0]) < 20:
                    input_texto[0] += chr(tecla)

    return seleccion[0]


def dibujar_hud(ui, orientacion_actual, patrones, arma_actual=None):
    """
    Dibuja el HUD superior con información del estado.

    Args:
        ui: Frame de OpenCV donde dibujar
        orientacion_actual: Orientación actual detectada
        patrones: Diccionario con patrones calibrados
        arma_actual: Nombre del arma seleccionada
    """
    cv2.rectangle(ui, (0, 0), (640, 80), (0, 0, 0), -1)  # Fondo negro HUD

    # Mostrar arma actual
    if arma_actual:
        cv2.putText(ui, f"ARMA: {arma_actual.upper()}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 200), 2)

    cv2.putText(ui, f"MODO: {orientacion_actual}", (230, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    if orientacion_actual != "DESCONOCIDO":
        estado_txt = "LISTO" if patrones.get(orientacion_actual, {}).get("calibrado") else "NO CALIBRADO"
        color_estado = (0, 255, 0) if estado_txt == "LISTO" else (0, 0, 255)
        cv2.putText(ui, f"MEMORIA: {estado_txt}", (230, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_estado, 2)


def dibujar_boton_nuevo_patron(ui, calibrado):
    """
    Dibuja botón de calibración: "NUEVO PATRON" o "RECALIBRAR".

    Args:
        ui: Frame de OpenCV donde dibujar
        calibrado: Boolean indicando si está calibrado
    """
    if calibrado:
        # Botón RECALIBRAR (ya está calibrado, puede recalibrar)
        cv2.rectangle(ui, (20, 20), (200, 70), (0, 130, 130), -1)
        cv2.putText(ui, "RECALIBRAR", (40, 52),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    else:
        # Botón NUEVO PATRON (sin calibración)
        cv2.rectangle(ui, (20, 20), (200, 70), (200, 0, 0), -1)
        cv2.putText(ui, "NUEVO PATRON", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


def dibujar_cuerpo(ui, kp, orientacion, colores):
    """
    Dibuja las líneas del cuerpo para cualquier perfil, incluyendo brazo de soporte.

    Args:
        ui: Frame de OpenCV donde dibujar
        kp: Keypoints del cuerpo
        orientacion: 'PERFIL_DERECHO' o 'PERFIL_IZQUIERDO'
        colores: Dict con 'col_b', 'col_t', 'col_chc', 'col_bs'
    """
    col_b = colores["col_b"]
    col_t = colores["col_t"]
    col_chc = colores["col_chc"]

    if orientacion == "PERFIL_DERECHO":
        dom_h, dom_c, dom_m = H_D, C_D, M_D
        dom_cad, dom_rod = CAD_D, ROD_D
        sop_h, sop_c, sop_m = H_I, C_I, M_I
    else:
        dom_h, dom_c, dom_m = H_I, C_I, M_I
        dom_cad, dom_rod = CAD_I, ROD_I
        sop_h, sop_c, sop_m = H_D, C_D, M_D

    # Brazo dominante
    cv2.line(ui, tuple(kp[dom_h][:2].astype(int)), tuple(kp[dom_c][:2].astype(int)), col_b, 3)
    cv2.line(ui, tuple(kp[dom_c][:2].astype(int)), tuple(kp[dom_m][:2].astype(int)), col_b, 3)

    # Torso (hombro-cadera-rodilla)
    cv2.line(ui, tuple(kp[dom_h][:2].astype(int)), tuple(kp[dom_cad][:2].astype(int)), col_t, 3)
    cv2.line(ui, tuple(kp[dom_cad][:2].astype(int)), tuple(kp[dom_rod][:2].astype(int)), col_t, 3)

    # Codo-hombro-cadera
    cv2.line(ui, tuple(kp[dom_c][:2].astype(int)), tuple(kp[dom_h][:2].astype(int)), col_chc, 3)
    cv2.line(ui, tuple(kp[dom_h][:2].astype(int)), tuple(kp[dom_cad][:2].astype(int)), col_chc, 3)

    # Brazo de soporte (si tiene evaluación)
    if colores.get("col_bs") is not None:
        col_bs = colores["col_bs"]
        cv2.line(ui, tuple(kp[sop_h][:2].astype(int)), tuple(kp[sop_c][:2].astype(int)), col_bs, 2)
        cv2.line(ui, tuple(kp[sop_c][:2].astype(int)), tuple(kp[sop_m][:2].astype(int)), col_bs, 2)


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
