"""
SISTEMA OMNIDIRECCIONAL DE EVALUACIÓN TÁCTICA - DINDES
Motor Biométrico IA para detección y evaluación de posturas

Este es el archivo principal que orquesta los módulos de:
- Calibración: Almacenamiento y gestión de patrones
- Cálculos: Operaciones matemáticas y detección
- UI: Interfaz de usuario y visualización
"""

import cv2
import time
from ultralytics import YOLO

# Importar módulos personalizados
from calibracion import GestorCalbracion
from calculos import detectar_orientacion, extraer_angulos, evaluar_postura
import ui

# Modelos de pose disponibles (YOLO26 - más reciente):
# yolo26n-pose.pt (nano), yolo26s-pose.pt (small), yolo26m-pose.pt (medium)
# Para detección de posturas de tiro se recomienda mínimo 'small'

# Índices COCO
H_I, H_D = 5, 6
C_I, C_D = 7, 8
M_I, M_D = 9, 10
CAD_I, CAD_D = 11, 12
ROD_I, ROD_D = 13, 14



class MotorBiometrico:
    """Orquestador principal del sistema"""

    def __init__(self, modelo_path='yolov8n-pose.pt'):
        """
        Inicializa el motor biométrico.

        Args:
            modelo_path: Ruta al modelo YOLO
        """
        self.modelo = YOLO(modelo_path)
        self.cap = cv2.VideoCapture(0)
        self.gestor = GestorCalbracion(tolerancia=12)
        self.orientacion_actual = "DESCONOCIDO"
        self.nombre_ventana = 'DINDES - Motor Biometrico IA'

        # Crear ventana
        ui.crear_ventana(self.nombre_ventana, self.callback_click)

        print("Iniciando Sistema Omnidireccional de Evaluación Táctica...")

    def seleccionar_arma(self):
        """
        Muestra el menú de selección de arma al inicio.

        Returns:
            bool: True si se seleccionó un arma, False si se canceló
        """
        lista_armas = self.gestor.obtener_lista_armas()
        arma = ui.mostrar_menu_armas(self.nombre_ventana, lista_armas)

        if arma is None:
            return False

        # Si el arma ya existe, seleccionarla; si no, crearla
        if arma in self.gestor.obtener_lista_armas():
            self.gestor.seleccionar_arma(arma)
            print(f"Arma seleccionada: {arma}")
        else:
            self.gestor.crear_arma(arma)
            print(f"Nueva arma creada: {arma}")

        # Restaurar callback del mouse para el modo normal
        cv2.setMouseCallback(self.nombre_ventana, self.callback_click)
        return True

    def callback_click(self, evento, x, y, flags, param):
        """Callback para eventos de mouse"""
        if evento == cv2.EVENT_LBUTTONDOWN:
            # Clic en el botón superior izquierdo (20,20 a 200,70)
            if 20 <= x <= 200 and 20 <= y <= 70:
                if self.orientacion_actual != "DESCONOCIDO" and self.gestor.obtener_estado() == "EVALUANDO":
                    self.gestor.iniciar_calibracion()

    def procesar_frame(self, frame):
        """
        Procesa un frame de video.

        Args:
            frame: Frame de OpenCV

        Returns:
            frame: Frame procesado con visualización
        """
        ui_frame = frame.copy()

        try:
            # Obtener predicciones
            resultados = self.modelo(frame, verbose=False)
            kp = resultados[0].keypoints.xy[0].cpu().numpy()
            conf = resultados[0].keypoints.conf[0].cpu().numpy()

            # 1. DETECCIÓN AUTOMÁTICA DE ORIENTACIÓN
            self.orientacion_actual = detectar_orientacion(kp, conf)

            # 2. DIBUJAR HUD (con nombre de arma)
            ui.dibujar_hud(ui_frame, self.orientacion_actual,
                           self.gestor.obtener_todos_los_patrones(),
                           self.gestor.obtener_arma_actual())

            # 3. LÓGICA DE CALIBRACIÓN Y EVALUACIÓN
            if self.orientacion_actual != "DESCONOCIDO":

                # Extraer ángulos según la vista actual (con confianza para brazo soporte)
                angulos = extraer_angulos(kp, self.orientacion_actual, conf)

                # --- ESTADO: CONTEO PARA CALIBRAR ---
                if self.gestor.obtener_estado() == "CONTEO":
                    tiempo_restante = self.gestor.obtener_tiempo_restante_calibracion()
                    ui.mostrar_mensaje_calibracion(ui_frame, self.orientacion_actual, tiempo_restante)

                    if self.gestor.calibracion_completada():
                        self.gestor.guardar_patron(
                            self.orientacion_actual,
                            angulos["brazo"], angulos["torso"],
                            angulos["codo_hombro_cadera"],
                            angulos.get("brazo_soporte")
                        )

                # --- ESTADO: EVALUACIÓN EN VIVO ---
                elif self.gestor.obtener_estado() == "EVALUANDO":
                    # Dibujar botón (NUEVO PATRON o RECALIBRAR)
                    ui.dibujar_boton_nuevo_patron(ui_frame, self.gestor.esta_calibrado(self.orientacion_actual))

                    if self.gestor.esta_calibrado(self.orientacion_actual):
                        # Evaluar postura
                        patron = self.gestor.obtener_patron(self.orientacion_actual)
                        colores = evaluar_postura(
                            angulos, patron,
                            self.gestor.obtener_tolerancia()
                        )

                        # Dibujar cuerpo con colores de evaluación
                        ui.dibujar_cuerpo(ui_frame, kp, self.orientacion_actual, colores)
                    else:
                        ui.mostrar_mensaje_prescalibracion(ui_frame)

        except Exception as e:
            pass

        return ui_frame

    def ejecutar(self):
        """Bucle principal de ejecución"""
        # Mostrar menú de selección de arma al inicio
        if not self.seleccionar_arma():
            print("No se seleccionó arma. Cerrando sistema.")
            self.cerrar()
            return

        while self.cap.isOpened():
            exito, frame = self.cap.read()
            if not exito:
                break

            frame_procesado = self.procesar_frame(frame)
            cv2.imshow(self.nombre_ventana, frame_procesado)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cerrar()

    def cerrar(self):
        """Cierra recursos"""
        self.cap.release()
        cv2.destroyAllWindows()
        print("Sistema cerrado correctamente.")


if __name__ == "__main__":
    motor = MotorBiometrico(modelo_path='yolo26s-pose.pt')
    motor.ejecutar()
