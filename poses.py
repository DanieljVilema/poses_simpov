"""
SISTEMA OMNIDIRECCIONAL DE EVALUACIÓN TÁCTICA - DINDES
Motor Biométrico IA para detección y evaluación de posturas
"""
import cv2
from ultralytics import YOLO

# Importar módulos personalizados
from calibracion import GestorCalbracion
from calculos import detectar_orientacion, extraer_angulos, evaluar_postura, SuavizadorTemporal
import ui

class MotorBiometrico:
    def __init__(self, modelo_path='yolo26n-pose.pt'):
        self.modelo = YOLO(modelo_path)
        self.cap = cv2.VideoCapture(0)
        self.gestor = GestorCalbracion() # Tolerancia manual eliminada, usa std
        self.suavizador = SuavizadorTemporal(ventana=5)
        self.orientacion_actual = "DESCONOCIDO"
        self.nombre_ventana = 'DINDES - Motor Biometrico IA'

        ui.crear_ventana(self.nombre_ventana, self.callback_click)
        print("Iniciando Sistema Omnidireccional de Evaluación Táctica...")

    def seleccionar_arma(self):
        lista_armas = self.gestor.obtener_lista_armas()
        arma = ui.mostrar_menu_armas(self.nombre_ventana, lista_armas)

        if arma is None: return False

        if arma in self.gestor.obtener_lista_armas():
            self.gestor.seleccionar_arma(arma)
            print(f"Arma seleccionada: {arma}")
        else:
            self.gestor.crear_arma(arma)
            print(f"Nueva arma creada: {arma}")

        cv2.setMouseCallback(self.nombre_ventana, self.callback_click)
        return True

    def callback_click(self, evento, x, y, flags, param):
        if evento == cv2.EVENT_LBUTTONDOWN:
            if 20 <= x <= 200 and 20 <= y <= 70:
                if self.orientacion_actual != "DESCONOCIDO" and self.gestor.obtener_estado() == "EVALUANDO":
                    # Pasamos la orientación para saber a quién le recolectamos datos
                    self.gestor.iniciar_calibracion(self.orientacion_actual)

    def procesar_frame(self, frame):
        ui_frame = frame.copy()
        try:
            # Usamos self.modelo normal para NO pedir la libreria 'lap'
            resultados = self.modelo(frame, verbose=False)
            
            if len(resultados[0].keypoints.xy) == 0:
                self.orientacion_actual = "DESCONOCIDO"
                ui.dibujar_hud(ui_frame, self.orientacion_actual, self.gestor.obtener_todos_los_patrones(), self.gestor.obtener_arma_actual())
                return ui_frame

            # Puntos crudos de la IA
            kp_raw = resultados[0].keypoints.xy[0].cpu().numpy()
            conf_raw = resultados[0].keypoints.conf[0].cpu().numpy()

            # Suavizado Temporal para estabilidad visual
            self.suavizador.actualizar(kp_raw, conf_raw)
            kp, conf = self.suavizador.obtener_suavizado()

            self.orientacion_actual = detectar_orientacion(kp, conf)
            ui.dibujar_hud(ui_frame, self.orientacion_actual, self.gestor.obtener_todos_los_patrones(), self.gestor.obtener_arma_actual())

            if self.orientacion_actual != "DESCONOCIDO":
                
                # Para la calibración recolectamos puntos CRUDOS (para la desviación estandar real)
                # Para la evaluación usamos puntos SUAVIZADOS (para UI fluida)
                angulos = extraer_angulos(kp, self.orientacion_actual, conf)

                if self.gestor.obtener_estado() == "CONTEO":
                    if self.orientacion_actual == self.gestor.orientacion_calibrando:
                        angulos_raw = extraer_angulos(kp_raw, self.orientacion_actual, conf_raw)
                        self.gestor.agregar_muestra(angulos_raw)

                    tiempo_restante = self.gestor.obtener_tiempo_restante_calibracion()
                    ui.mostrar_mensaje_calibracion(ui_frame, self.orientacion_actual, tiempo_restante, len(self.gestor.muestras))

                    if self.gestor.calibracion_completada():
                        self.gestor.finalizar_calibracion()

                elif self.gestor.obtener_estado() == "EVALUANDO":
                    ui.dibujar_boton_nuevo_patron(ui_frame, self.gestor.esta_calibrado(self.orientacion_actual))

                    if self.gestor.esta_calibrado(self.orientacion_actual):
                        patron = self.gestor.obtener_patron(self.orientacion_actual)
                        colores = evaluar_postura(angulos, patron)
                        
                        ui.dibujar_cuerpo(ui_frame, kp, self.orientacion_actual, colores)
                        ui.dibujar_score(ui_frame, colores.get("score", 0))
                    else:
                        ui.mostrar_mensaje_prescalibracion(ui_frame)

        except Exception as e:
            # Ahora vemos el error real si algo falla en vez de 'pass'
            print(f"[ERROR] procesar_frame: {e}")

        return ui_frame

    def ejecutar(self):
        if not self.seleccionar_arma():
            print("No se seleccionó arma. Cerrando sistema.")
            self.cerrar()
            return

        while self.cap.isOpened():
            exito, frame = self.cap.read()
            if not exito: break
            frame_procesado = self.procesar_frame(frame)
            cv2.imshow(self.nombre_ventana, frame_procesado)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            
        self.cerrar()

    def cerrar(self):
        self.cap.release()
        cv2.destroyAllWindows()
        print("Sistema cerrado correctamente.")

if __name__ == "__main__":
    motor = MotorBiometrico(modelo_path='yolo26n-pose.pt')
    motor.ejecutar()